"""
Cloud-Optimized Pipeline for Full Fire Area Processing
Leverages Google Earth Engine for server-side processing and distributed computing
"""
import ee
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
import logging
from datetime import datetime, timedelta
import time
from dataclasses import dataclass
import requests

@dataclass
class FireBoundary:
    """Fire boundary information"""
    name: str
    year: int
    geometry: ee.Geometry
    total_area_ha: float
    fire_start_date: str
    fire_end_date: str

class CloudOptimizedPipeline:
    """
    Cloud-optimized pipeline for processing entire fire areas using Google Earth Engine
    """
    
    def __init__(self, project_id: str = None, skip_ee_init: bool = False):
        """
        Initialize cloud pipeline
        
        Args:
            project_id: Google Cloud Project ID for Earth Engine
            skip_ee_init: Skip Earth Engine initialization for demo/testing
        """
        self.project_id = project_id
        self.logger = logging.getLogger(__name__)
        self.ee_available = False
        
        if not skip_ee_init:
            # Initialize Earth Engine
            try:
                if project_id and project_id != "your-project-id":
                    ee.Initialize(project=project_id)
                else:
                    ee.Initialize()
                self.logger.info("Earth Engine initialized successfully")
                self.ee_available = True
            except Exception as e:
                self.logger.warning(f"Earth Engine not available: {e}")
                self.logger.info("Running in demo mode without GEE")
                self.ee_available = False
    
    def get_fire_boundaries(self) -> List[FireBoundary]:
        """Get major Colorado fire boundaries from MTBS dataset"""
        
        # Load MTBS (Monitoring Trends in Burn Severity) dataset
        mtbs = ee.FeatureCollection("USGS/MTBS/2015-2018")
        
        # Define Colorado bounds
        colorado = ee.Geometry.Rectangle([-109.1, 36.9, -102.0, 41.0])
        
        # Filter for major Colorado fires
        colorado_fires = mtbs.filterBounds(colorado).filter(
            ee.Filter.gte('Acres', 50000)  # Large fires only
        )
        
        fire_boundaries = []
        
        # East Troublesome Fire (2020) - manually defined as it's newer than MTBS
        east_troublesome = FireBoundary(
            name="East Troublesome Fire",
            year=2020,
            geometry=ee.Geometry.Rectangle([-106.0, 40.0, -105.6, 40.4]),
            total_area_ha=78421,  # 193,812 acres = 78,421 hectares
            fire_start_date="2020-10-14",
            fire_end_date="2020-11-30"
        )
        fire_boundaries.append(east_troublesome)
        
        # Cameron Peak Fire (2020)
        cameron_peak = FireBoundary(
            name="Cameron Peak Fire", 
            year=2020,
            geometry=ee.Geometry.Rectangle([-105.8, 40.5, -105.3, 40.9]),
            total_area_ha=83508,  # 208,913 acres
            fire_start_date="2020-08-13",
            fire_end_date="2020-12-02"
        )
        fire_boundaries.append(cameron_peak)
        
        return fire_boundaries
    
    def create_processing_grid(self, 
                             fire_boundary: FireBoundary,
                             tile_size_km: float = 5.0) -> List[ee.Geometry]:
        """
        Create processing grid for large fire area
        
        Args:
            fire_boundary: Fire boundary to process
            tile_size_km: Size of each processing tile in kilometers
            
        Returns:
            List of tile geometries for processing
        """
        # Get fire boundary
        bounds = fire_boundary.geometry.bounds()
        coords = bounds.coordinates().get(0).getInfo()
        
        # Calculate tile dimensions in degrees (approximate)
        lat = (coords[0][1] + coords[2][1]) / 2
        lon_deg_per_km = 1 / (111.32 * np.cos(np.radians(lat)))
        lat_deg_per_km = 1 / 110.54
        
        tile_lon_deg = tile_size_km * lon_deg_per_km
        tile_lat_deg = tile_size_km * lat_deg_per_km
        
        # Create grid
        min_lon, min_lat = coords[0]
        max_lon, max_lat = coords[2]
        
        tiles = []
        lat = min_lat
        tile_id = 0
        
        while lat < max_lat:
            lon = min_lon
            while lon < max_lon:
                # Create tile geometry
                tile_bounds = [
                    [lon, lat],
                    [lon + tile_lon_deg, lat],
                    [lon + tile_lon_deg, lat + tile_lat_deg],
                    [lon, lat + tile_lat_deg],
                    [lon, lat]
                ]
                
                tile_geom = ee.Geometry.Polygon([tile_bounds])
                
                # Only include tiles that intersect with fire boundary
                if fire_boundary.geometry.intersects(tile_geom).getInfo():
                    tiles.append(tile_geom)
                
                lon += tile_lon_deg
                tile_id += 1
            lat += tile_lat_deg
        
        self.logger.info(f"Created {len(tiles)} processing tiles for {fire_boundary.name}")
        return tiles
    
    def process_fire_area_cloud(self,
                               fire_boundary: FireBoundary,
                               output_bucket: str = None,
                               export_scale: int = 10) -> Dict:
        """
        Process entire fire area using Earth Engine cloud processing
        
        Args:
            fire_boundary: Fire boundary to process
            output_bucket: Google Cloud Storage bucket for outputs
            export_scale: Export resolution in meters
            
        Returns:
            Dictionary with processing job information
        """
        
        # Define date ranges
        fire_start = datetime.strptime(fire_boundary.fire_start_date, "%Y-%m-%d")
        fire_end = datetime.strptime(fire_boundary.fire_end_date, "%Y-%m-%d")
        
        # Pre-fire period (1 year before to fire start)
        pre_start = fire_start - timedelta(days=365)
        pre_end = fire_start - timedelta(days=30)
        
        # Post-fire period (6 months after fire end to 1 year after)
        post_start = fire_end + timedelta(days=180)
        post_end = fire_end + timedelta(days=365)
        
        # Load Sentinel-2 collections
        pre_fire_collection = (ee.ImageCollection('COPERNICUS/S2_SR')
                              .filterBounds(fire_boundary.geometry)
                              .filterDate(pre_start.strftime('%Y-%m-%d'), 
                                        pre_end.strftime('%Y-%m-%d'))
                              .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
                              .map(self._mask_s2_clouds)
                              .map(self._add_indices))
        
        post_fire_collection = (ee.ImageCollection('COPERNICUS/S2_SR')
                               .filterBounds(fire_boundary.geometry)
                               .filterDate(post_start.strftime('%Y-%m-%d'),
                                         post_end.strftime('%Y-%m-%d'))
                               .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
                               .map(self._mask_s2_clouds)
                               .map(self._add_indices))
        
        # Create median composites
        pre_fire_composite = pre_fire_collection.median()
        post_fire_composite = post_fire_collection.median()
        
        # Calculate vegetation change indices
        ndvi_change = post_fire_composite.select('NDVI').subtract(
            pre_fire_composite.select('NDVI')
        ).rename('NDVI_change')
        
        nbr_change = pre_fire_composite.select('NBR').subtract(
            post_fire_composite.select('NBR')  # NBR: higher values = less burn
        ).rename('NBR_change')
        
        # Create severity classification
        severity = self._classify_burn_severity(nbr_change)
        
        # Combine all bands for export
        final_composite = ee.Image.cat([
            pre_fire_composite.select(['NDVI', 'NBR']).rename(['NDVI_pre', 'NBR_pre']),
            post_fire_composite.select(['NDVI', 'NBR']).rename(['NDVI_post', 'NBR_post']),
            ndvi_change,
            nbr_change,
            severity
        ]).clip(fire_boundary.geometry)
        
        # Export to Google Drive or Cloud Storage
        if output_bucket:
            # Export to Google Cloud Storage
            task = ee.batch.Export.image.toCloudStorage(
                image=final_composite,
                description=f'{fire_boundary.name.replace(" ", "_")}_analysis',
                bucket=output_bucket,
                fileNamePrefix=f'fire_analysis/{fire_boundary.name.replace(" ", "_")}',
                region=fire_boundary.geometry,
                scale=export_scale,
                maxPixels=1e10,
                fileDimensions=[4096, 4096],  # Optimize for large areas
                formatOptions={'cloudOptimized': True}
            )
        else:
            # Export to Google Drive
            task = ee.batch.Export.image.toDrive(
                image=final_composite,
                description=f'{fire_boundary.name.replace(" ", "_")}_analysis',
                folder='GhostForestWatcher',
                fileNamePrefix=f'{fire_boundary.name.replace(" ", "_")}_analysis',
                region=fire_boundary.geometry,
                scale=export_scale,
                maxPixels=1e10,
                fileDimensions=[4096, 4096]
            )
        
        # Start the export task
        task.start()
        
        # Return job information
        return {
            'task_id': task.id,
            'fire_name': fire_boundary.name,
            'status': task.status(),
            'export_scale': export_scale,
            'area_ha': fire_boundary.total_area_ha,
            'processing_start': datetime.now().isoformat(),
            'expected_completion': 'Unknown (check task status)',
            'output_location': output_bucket or 'Google Drive'
        }
    
    def _mask_s2_clouds(self, image):
        """Apply cloud mask to Sentinel-2 image"""
        scl = image.select('SCL')
        cloud_mask = scl.neq(3).And(scl.neq(8)).And(scl.neq(9)).And(scl.neq(10))
        return image.updateMask(cloud_mask).divide(10000)  # Scale to 0-1
    
    def _add_indices(self, image):
        """Add vegetation indices to Sentinel-2 image"""
        ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        nbr = image.normalizedDifference(['B8', 'B12']).rename('NBR')
        ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')
        return image.addBands([ndvi, nbr, ndwi])
    
    def _classify_burn_severity(self, nbr_change):
        """Classify burn severity based on NBR change"""
        return (nbr_change
                .where(nbr_change.lt(0.1), 1)     # Unburned
                .where(nbr_change.gte(0.1).And(nbr_change.lt(0.27)), 2)  # Low severity
                .where(nbr_change.gte(0.27).And(nbr_change.lt(0.44)), 3) # Moderate severity
                .where(nbr_change.gte(0.44).And(nbr_change.lt(0.66)), 4) # High severity
                .where(nbr_change.gte(0.66), 5)  # Very high severity
                .rename('burn_severity'))
    
    def monitor_processing_jobs(self, task_ids: List[str]) -> Dict:
        """Monitor status of Earth Engine processing jobs"""
        
        job_status = {}
        
        for task_id in task_ids:
            try:
                task = ee.batch.Task.status(task_id)
                job_status[task_id] = {
                    'state': task.get('state', 'UNKNOWN'),
                    'creation_timestamp': task.get('creation_timestamp_ms', 0),
                    'start_timestamp': task.get('start_timestamp_ms', 0),
                    'update_timestamp': task.get('update_timestamp_ms', 0),
                    'description': task.get('description', ''),
                    'error_message': task.get('error_message', None)
                }
                
                if task.get('state') == 'COMPLETED':
                    self.logger.info(f"Task {task_id} completed successfully")
                elif task.get('state') == 'FAILED':
                    self.logger.error(f"Task {task_id} failed: {task.get('error_message', 'Unknown error')}")
                    
            except Exception as e:
                self.logger.error(f"Error checking task {task_id}: {e}")
                job_status[task_id] = {'state': 'ERROR', 'error': str(e)}
        
        return job_status
    
    def estimate_processing_resources(self, fire_boundary: FireBoundary) -> Dict:
        """Estimate processing requirements for fire area"""
        
        # Calculate approximate data volumes
        area_km2 = fire_boundary.total_area_ha / 100  # Convert hectares to km²
        pixels_10m = area_km2 * 1000000 / 100  # 10m resolution
        
        # Estimate file sizes
        bytes_per_pixel = 4  # float32
        bands_per_composite = 7  # NDVI_pre, NBR_pre, NDVI_post, NBR_post, changes, severity
        
        estimated_size_gb = (pixels_10m * bytes_per_pixel * bands_per_composite) / (1024**3)
        
        # Estimate processing time (empirical estimates)
        estimated_minutes = max(30, int(area_km2 / 10))  # Rough estimate: 1 minute per 10 km²
        
        return {
            'fire_name': fire_boundary.name,
            'area_km2': area_km2,
            'total_pixels_10m': int(pixels_10m),
            'estimated_output_size_gb': round(estimated_size_gb, 2),
            'estimated_processing_time_minutes': estimated_minutes,
            'recommended_tile_size_km': 5 if area_km2 > 1000 else 10,
            'memory_requirements': {
                'minimum_ram_gb': max(8, int(estimated_size_gb * 2)),
                'recommended_ram_gb': max(16, int(estimated_size_gb * 4)),
                'cloud_processing_recommended': area_km2 > 500
            }
        }

def main():
    """Example usage of cloud-optimized pipeline"""
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize pipeline (requires GEE authentication)
    try:
        pipeline = CloudOptimizedPipeline(project_id="your-project-id")
        
        # Get fire boundaries
        fire_boundaries = pipeline.get_fire_boundaries()
        
        print(f"Available fire areas for processing:")
        for fire in fire_boundaries:
            resources = pipeline.estimate_processing_resources(fire)
            print(f"\n🔥 {fire.name} ({fire.year})")
            print(f"   Area: {resources['area_km2']:.0f} km²")
            print(f"   Est. output: {resources['estimated_output_size_gb']:.1f} GB")
            print(f"   Est. time: {resources['estimated_processing_time_minutes']} minutes")
            print(f"   Cloud recommended: {resources['memory_requirements']['cloud_processing_recommended']}")
        
        # Process East Troublesome Fire
        if fire_boundaries:
            east_troublesome = fire_boundaries[0]  # First fire
            
            print(f"\n🚀 Starting cloud processing for {east_troublesome.name}...")
            
            job_info = pipeline.process_fire_area_cloud(
                fire_boundary=east_troublesome,
                output_bucket=None,  # Export to Google Drive
                export_scale=10      # 10m resolution
            )
            
            print(f"✅ Processing job started:")
            print(f"   Task ID: {job_info['task_id']}")
            print(f"   Fire: {job_info['fire_name']}")
            print(f"   Area: {job_info['area_ha']:,.0f} hectares")
            print(f"   Output: {job_info['output_location']}")
            
            # Monitor job (example)
            print(f"\n📊 Monitoring job status...")
            status = pipeline.monitor_processing_jobs([job_info['task_id']])
            print(f"Current status: {status[job_info['task_id']]['state']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you have authenticated with Google Earth Engine:")
        print("  earthengine authenticate")

if __name__ == "__main__":
    main()
