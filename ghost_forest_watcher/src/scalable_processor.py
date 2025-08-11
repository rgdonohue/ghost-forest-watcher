"""
Scalable Processing System for Large-Area Forest Analysis
Handles memory-efficient processing of massive fire areas through intelligent tiling
"""
import numpy as np
import rasterio
from rasterio.windows import Window
from pathlib import Path
import json
from typing import Dict, List, Tuple, Generator
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import psutil
import math
from dataclasses import dataclass
from tqdm import tqdm

from .sam_processor import ForestSAMProcessor

# =====================
# Top-level worker API
# =====================

_GLOBAL_SAM_PROCESSOR = None

def _init_worker(model_type: str = "vit_b") -> None:
    """Initializer for worker processes to create a local SAM processor.

    Avoids pickling model objects by instantiating per-process.
    """
    global _GLOBAL_SAM_PROCESSOR
    _GLOBAL_SAM_PROCESSOR = ForestSAMProcessor(model_type=model_type)
    _GLOBAL_SAM_PROCESSOR.load_model()


def _process_tile_worker(
    input_path: str,
    output_dir: str,
    tile_job: Dict,
) -> Dict:
    """Process a single tile in a separate process.

    Args:
        input_path: Path to input GeoTIFF (string for pickling ease)
        output_dir: Base output directory (string)
        tile_job: Serializable dict describing the tile window and metadata

    Returns:
        Result dictionary similar to the previous implementation
    """
    try:
        # Re-open dataset in worker
        with rasterio.open(input_path) as src:
            # Reconstruct window
            col_off, row_off, width, height = tile_job["window"]
            window = Window(col_off, row_off, width, height)

            tile_data = src.read(window=window)
            tile_transform = rasterio.windows.transform(window, src.transform)

            tile_profile = src.profile.copy()
            tile_profile.update(
                {
                    "height": window.height,
                    "width": window.width,
                    "transform": tile_transform,
                }
            )

        # Use per-process SAM processor
        if _GLOBAL_SAM_PROCESSOR is None:
            # Fallback: initialize lazily if initializer wasn't used
            _init_worker("vit_b")

        rgb_image = _GLOBAL_SAM_PROCESSOR.ndvi_to_rgb(tile_data)
        if rgb_image is None:
            return {"tile_id": tile_job["id"], "status": "failed", "error": "RGB conversion failed"}

        segmentation_results = _GLOBAL_SAM_PROCESSOR.segment_forest_areas(rgb_image)
        classification_results = _GLOBAL_SAM_PROCESSOR.classify_vegetation_health(
            tile_data, segmentation_results
        )

        # Save artifacts
        tile_output_dir = Path(output_dir) / f"tile_{tile_job['id']:04d}"
        tile_output_dir.mkdir(exist_ok=True, parents=True)

        # Write NDVI tile
        with rasterio.open(tile_output_dir / "ndvi_data.tif", "w", **tile_profile) as dst:
            dst.write(tile_data)

        # Write masks as single-band uint8 rasters
        for mask_name, mask_data in classification_results["masks"].items():
            mask_profile = tile_profile.copy()
            mask_profile.update({"dtype": "uint8", "count": 1})
            with rasterio.open(tile_output_dir / f"{mask_name}_mask.tif", "w", **mask_profile) as dst:
                dst.write(mask_data.astype(np.uint8), 1)

        # Save statistics
        stats_file = tile_output_dir / "statistics.json"
        with open(stats_file, "w") as f:
            json.dump(
                {
                    "tile_id": tile_job["id"],
                    "bounds": tile_job["bounds"],
                    "area_km2": tile_job["area_km2"],
                    "statistics": classification_results["statistics"],
                    "processing_status": "completed",
                },
                f,
                indent=2,
            )

        return {
            "tile_id": tile_job["id"],
            "status": "completed",
            "statistics": classification_results["statistics"],
            "area_km2": tile_job["area_km2"],
            "output_dir": str(tile_output_dir),
        }

    except Exception as exc:  # pragma: no cover - defensive
        return {
            "tile_id": tile_job.get("id"),
            "status": "failed",
            "error": str(exc),
        }

@dataclass
class TileInfo:
    """Information about a processing tile"""
    id: int
    window: Window
    bounds: Tuple[float, float, float, float]
    area_km2: float
    priority: int = 1  # 1=high, 2=medium, 3=low

class ScalableForestProcessor:
    """
    Memory-efficient processor for large forest areas using adaptive tiling
    """
    
    def __init__(self, 
                 max_memory_gb: float = None,
                 tile_size_mb: int = 50,
                 overlap_pixels: int = 64):
        """
        Initialize scalable processor
        
        Args:
            max_memory_gb: Maximum memory to use (auto-detect if None)
            tile_size_mb: Target tile size in MB
            overlap_pixels: Overlap between tiles to prevent edge effects
        """
        self.max_memory_gb = max_memory_gb or self._get_available_memory()
        self.tile_size_mb = tile_size_mb
        self.overlap_pixels = overlap_pixels
        self.logger = logging.getLogger(__name__)
        
        # Initialize SAM processor (shared across tiles)
        self.sam_processor = None
        
    def _get_available_memory(self) -> float:
        """Get available system memory in GB"""
        return psutil.virtual_memory().available / (1024**3) * 0.7  # Use 70% of available
    
    def calculate_optimal_tiling(self, 
                                input_path: Path,
                                fire_boundary: Dict = None) -> List[TileInfo]:
        """
        Calculate optimal tiling strategy for large raster
        
        Args:
            input_path: Path to large GeoTIFF
            fire_boundary: Optional fire boundary for priority weighting
            
        Returns:
            List of TileInfo objects with processing strategy
        """
        with rasterio.open(input_path) as src:
            total_pixels = src.width * src.height
            pixel_size_bytes = 4  # float32
            total_size_mb = (total_pixels * pixel_size_bytes) / (1024**2)
            
            self.logger.info(f"Input raster: {src.width}x{src.height} ({total_size_mb:.1f} MB)")
            
            # Calculate optimal tile dimensions
            pixels_per_tile = (self.tile_size_mb * 1024**2) // pixel_size_bytes
            tile_dimension = int(math.sqrt(pixels_per_tile))
            
            # Adjust for actual raster dimensions
            tiles_x = math.ceil(src.width / tile_dimension)
            tiles_y = math.ceil(src.height / tile_dimension)
            
            actual_tile_width = src.width / tiles_x
            actual_tile_height = src.height / tiles_y
            
            self.logger.info(f"Tiling strategy: {tiles_x}x{tiles_y} tiles "
                           f"({actual_tile_width:.0f}x{actual_tile_height:.0f} pixels each)")
            
            tiles = []
            tile_id = 0
            
            for row in range(tiles_y):
                for col in range(tiles_x):
                    # Calculate window with overlap
                    col_off = max(0, int(col * actual_tile_width) - self.overlap_pixels)
                    row_off = max(0, int(row * actual_tile_height) - self.overlap_pixels)
                    
                    width = min(int(actual_tile_width) + 2 * self.overlap_pixels, 
                              src.width - col_off)
                    height = min(int(actual_tile_height) + 2 * self.overlap_pixels, 
                               src.height - row_off)
                    
                    window = Window(col_off, row_off, width, height)
                    
                    # Calculate geographic bounds
                    window_bounds = rasterio.windows.bounds(window, src.transform)
                    
                    # Calculate area
                    area_km2 = self._calculate_area_km2(window_bounds, src.crs)
                    
                    # Determine priority (higher priority for fire center areas)
                    priority = self._calculate_priority(window_bounds, fire_boundary)
                    
                    tiles.append(TileInfo(
                        id=tile_id,
                        window=window,
                        bounds=window_bounds,
                        area_km2=area_km2,
                        priority=priority
                    ))
                    
                    tile_id += 1
            
            # Sort by priority (high priority first)
            tiles.sort(key=lambda t: t.priority)
            
            self.logger.info(f"Generated {len(tiles)} tiles for processing")
            return tiles
    
    def _calculate_area_km2(self, bounds: Tuple, crs) -> float:
        """Calculate area of bounds in km²"""
        from pyproj import CRS, Transformer
        
        # Convert to appropriate projected CRS for area calculation
        if crs.is_geographic:
            # Use UTM zone for Colorado (approximately Zone 13N)
            utm_crs = CRS.from_epsg(32613)  # UTM Zone 13N
            transformer = Transformer.from_crs(crs, utm_crs, always_xy=True)
            
            x1, y1 = transformer.transform(bounds[0], bounds[1])
            x2, y2 = transformer.transform(bounds[2], bounds[3])
            
            area_m2 = abs(x2 - x1) * abs(y2 - y1)
            return area_m2 / 1000000  # Convert to km²
        else:
            # Already projected
            area_m2 = abs(bounds[2] - bounds[0]) * abs(bounds[3] - bounds[1])
            return area_m2 / 1000000
    
    def _calculate_priority(self, bounds: Tuple, fire_boundary: Dict = None) -> int:
        """Calculate processing priority for tile (1=high, 3=low)"""
        if fire_boundary is None:
            return 2  # Medium priority
        
        # TODO: Implement geometric intersection with fire boundary
        # For now, return medium priority
        return 2
    
    def process_tile(self, 
                     input_path: Path,
                     tile: TileInfo,
                     output_dir: Path) -> Dict:
        """
        Process a single tile with SAM analysis
        
        Args:
            input_path: Path to input GeoTIFF
            tile: TileInfo object
            output_dir: Directory for tile outputs
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Initialize SAM processor if needed
            if self.sam_processor is None:
                self.sam_processor = ForestSAMProcessor(model_type="vit_b")
                self.sam_processor.load_model()
            
            # Read tile data
            with rasterio.open(input_path) as src:
                tile_data = src.read(window=tile.window)
                tile_transform = rasterio.windows.transform(tile.window, src.transform)
                
                # Prepare tile metadata
                tile_profile = src.profile.copy()
                tile_profile.update({
                    'height': tile.window.height,
                    'width': tile.window.width,
                    'transform': tile_transform
                })
            
            # Convert to RGB for SAM
            rgb_image = self.sam_processor.ndvi_to_rgb(tile_data)
            if rgb_image is None:
                return {'tile_id': tile.id, 'status': 'failed', 'error': 'RGB conversion failed'}
            
            # Run SAM segmentation
            segmentation_results = self.sam_processor.segment_forest_areas(rgb_image)
            
            # Classify vegetation health
            classification_results = self.sam_processor.classify_vegetation_health(
                tile_data, segmentation_results
            )
            
            # Save tile results
            tile_output_dir = output_dir / f"tile_{tile.id:04d}"
            tile_output_dir.mkdir(exist_ok=True)
            
            # Save processed data
            with rasterio.open(tile_output_dir / "ndvi_data.tif", 'w', **tile_profile) as dst:
                dst.write(tile_data)
            
            # Save classification masks
            for mask_name, mask_data in classification_results['masks'].items():
                mask_profile = tile_profile.copy()
                mask_profile.update({'dtype': 'uint8'})
                
                with rasterio.open(tile_output_dir / f"{mask_name}_mask.tif", 'w', **mask_profile) as dst:
                    dst.write(mask_data.astype(np.uint8), 1)
            
            # Save statistics
            stats_file = tile_output_dir / "statistics.json"
            with open(stats_file, 'w') as f:
                json.dump({
                    'tile_id': tile.id,
                    'bounds': tile.bounds,
                    'area_km2': tile.area_km2,
                    'statistics': classification_results['statistics'],
                    'processing_status': 'completed'
                }, f, indent=2)
            
            return {
                'tile_id': tile.id,
                'status': 'completed',
                'statistics': classification_results['statistics'],
                'area_km2': tile.area_km2,
                'output_dir': str(tile_output_dir)
            }
            
        except Exception as e:
            self.logger.error(f"Error processing tile {tile.id}: {e}")
            return {
                'tile_id': tile.id,
                'status': 'failed',
                'error': str(e)
            }
    
    def process_large_area(self,
                          input_path: Path,
                          output_dir: Path,
                          fire_boundary: Dict = None,
                          max_workers: int = None) -> Dict:
        """
        Process entire large area using tiling strategy
        
        Args:
            input_path: Path to large GeoTIFF
            output_dir: Output directory for results
            fire_boundary: Optional fire boundary for priority
            max_workers: Number of parallel workers (auto-detect if None)
            
        Returns:
            Dictionary with aggregated results
        """
        output_dir.mkdir(exist_ok=True)
        
        # Calculate tiling strategy
        tiles = self.calculate_optimal_tiling(input_path, fire_boundary)
        
        # Determine number of workers
        if max_workers is None:
            max_workers = min(4, max(1, psutil.cpu_count() // 2))
        
        self.logger.info(f"Processing {len(tiles)} tiles with {max_workers} workers")
        
        # Build serializable jobs
        jobs: List[Dict] = []
        for tile in tiles:
            jobs.append(
                {
                    "id": tile.id,
                    "window": (
                        int(tile.window.col_off),
                        int(tile.window.row_off),
                        int(tile.window.width),
                        int(tile.window.height),
                    ),
                    "bounds": tile.bounds,
                    "area_km2": tile.area_km2,
                }
            )

        # Process tiles in parallel using per-process SAM instances
        results: List[Dict] = []
        completed_tiles = 0
        failed_tiles = 0

        with ProcessPoolExecutor(
            max_workers=max_workers,
            initializer=_init_worker,
            initargs=("vit_b",),
        ) as executor:
            futures = [
                executor.submit(
                    _process_tile_worker,
                    str(input_path),
                    str(output_dir),
                    job,
                )
                for job in jobs
            ]

            with tqdm(total=len(futures), desc="Processing tiles") as pbar:
                for future in as_completed(futures):
                    try:
                        result = future.result(timeout=300)
                        results.append(result)
                        if result.get("status") == "completed":
                            completed_tiles += 1
                        else:
                            failed_tiles += 1
                    except Exception as e:  # pragma: no cover - defensive
                        self.logger.error(f"Tile processing failed: {e}")
                        failed_tiles += 1
                    finally:
                        pbar.update(1)
                        pbar.set_postfix({"Completed": completed_tiles, "Failed": failed_tiles})
        
        # Aggregate results
        total_area = sum(r.get('area_km2', 0) for r in results if r['status'] == 'completed')
        
        # Combine statistics from all tiles
        aggregated_stats = self._aggregate_tile_statistics(results)
        
        # Save aggregated results
        summary = {
            'processing_summary': {
                'total_tiles': len(tiles),
                'completed_tiles': completed_tiles,
                'failed_tiles': failed_tiles,
                'success_rate': completed_tiles / len(tiles) * 100,
                'total_area_km2': total_area
            },
            'aggregated_statistics': aggregated_stats,
            'tile_results': results
        }
        
        with open(output_dir / "processing_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info(f"Processing complete: {completed_tiles}/{len(tiles)} tiles successful")
        
        return summary
    
    def _aggregate_tile_statistics(self, results: List[Dict]) -> Dict:
        """Aggregate statistics from all processed tiles"""
        total_pixels = {'healthy': 0, 'stressed': 0, 'declining': 0, 'dead': 0}
        total_vegetation_pixels = 0
        
        for result in results:
            if result['status'] == 'completed' and 'statistics' in result:
                stats = result['statistics']
                total_pixels['healthy'] += stats.get('healthy_pixels', 0)
                total_pixels['stressed'] += stats.get('stressed_pixels', 0)
                total_pixels['declining'] += stats.get('declining_pixels', 0)
                total_pixels['dead'] += stats.get('dead_pixels', 0)
                total_vegetation_pixels += stats.get('total_vegetation_pixels', 0)
        
        # Calculate percentages
        if total_vegetation_pixels > 0:
            percentages = {
                f'{category}_percent': (pixels / total_vegetation_pixels * 100)
                for category, pixels in total_pixels.items()
            }
        else:
            percentages = {f'{category}_percent': 0 for category in total_pixels.keys()}
        
        return {
            **{f'{category}_pixels': pixels for category, pixels in total_pixels.items()},
            'total_vegetation_pixels': total_vegetation_pixels,
            **percentages
        }

def main():
    """Example usage of scalable processor"""
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize processor
    processor = ScalableForestProcessor(
        max_memory_gb=8.0,  # Use 8GB max
        tile_size_mb=100,   # 100MB tiles
        overlap_pixels=64   # 64 pixel overlap
    )
    
    # Process large area
    input_path = Path("data/east_troublesome_small_tile.tif")
    output_dir = Path("outputs/large_scale_analysis")
    
    if input_path.exists():
        results = processor.process_large_area(
            input_path=input_path,
            output_dir=output_dir,
            max_workers=4
        )
        
        print(f"Processing complete!")
        print(f"Total area processed: {results['processing_summary']['total_area_km2']:.1f} km²")
        print(f"Success rate: {results['processing_summary']['success_rate']:.1f}%")
        
        # Print aggregated vegetation health
        stats = results['aggregated_statistics']
        print(f"\nAggregated Vegetation Health:")
        print(f"  Healthy: {stats['healthy_percent']:.1f}%")
        print(f"  Stressed: {stats['stressed_percent']:.1f}%")
        print(f"  Declining: {stats['declining_percent']:.1f}%")
        print(f"  Dead: {stats['dead_percent']:.1f}%")
    else:
        print(f"Input file not found: {input_path}")

if __name__ == "__main__":
    main()
