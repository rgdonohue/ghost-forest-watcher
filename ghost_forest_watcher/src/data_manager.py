"""
Data Management Layer for Ghost Forest Watcher Streamlit App
Handles loading, caching, and processing of geospatial data and analysis results
"""
import streamlit as st
import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import folium
from folium import plugins
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import json
from typing import Dict, Tuple, Optional, List
import base64
from PIL import Image
import io
from rasterio.coords import BoundingBox

# Import our SAM processor
from .sam_processor import ForestSAMProcessor

class GhostForestDataManager:
    """Centralized data management for the Ghost Forest Watcher app"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.outputs_dir = Path("outputs")
        self.models_dir = Path("models")
        
        # Cache keys
        self.CACHE_KEYS = {
            'geotiff_data': 'geotiff_data_cache',
            'sam_results': 'sam_results_cache',
            'analysis_stats': 'analysis_stats_cache',
            'folium_map': 'folium_map_cache'
        }
    
    @st.cache_data
    def load_geotiff_data(_self, file_path: str = "data/east_troublesome_small_tile.tif") -> Dict:
        """
        Load and process GeoTIFF data with caching
        
        Returns:
            Dictionary containing processed data and metadata
        """
        tiff_path = Path(file_path)
        if not tiff_path.exists():
            # Provide a small synthetic NDVI-difference-like dataset as a fallback
            st.warning(f"GeoTIFF not found at {tiff_path}. Using synthetic sample data for demo.")
            height, width = 100, 100
            # Synthetic NDVI difference in range [-0.5, 0.5]
            rng = np.random.default_rng(42)
            data_2d = (rng.random((height, width), dtype=np.float32) - 0.5)
            valid_data = data_2d[~np.isnan(data_2d)]
            stats = {
                'min': float(valid_data.min()),
                'max': float(valid_data.max()),
                'mean': float(valid_data.mean()),
                'std': float(valid_data.std()),
                'percentiles': {
                    '1': float(np.percentile(valid_data, 1)),
                    '5': float(np.percentile(valid_data, 5)),
                    '25': float(np.percentile(valid_data, 25)),
                    '50': float(np.percentile(valid_data, 50)),
                    '75': float(np.percentile(valid_data, 75)),
                    '95': float(np.percentile(valid_data, 95)),
                    '99': float(np.percentile(valid_data, 99))
                }
            }
            # Dummy WGS84 bounds roughly around Colorado
            metadata = {
                'bounds': BoundingBox(left=-106.0, bottom=40.0, right=-105.9, top=40.1),
                'crs': 'EPSG:4326',
                'transform': None,
                'shape': data_2d.shape,
                'dtype': str(data_2d.dtype),
                'nodata': None
            }
            return {
                'data': data_2d,
                'metadata': metadata,
                'statistics': stats,
                'valid_pixels': int(valid_data.size),
                'total_pixels': int(data_2d.size)
            }
            
        with rasterio.open(tiff_path) as src:
            # Read data
            data = src.read()
            
            # Get metadata
            metadata = {
                'bounds': src.bounds,
                'crs': str(src.crs),
                'transform': src.transform,
                'shape': data.shape,
                'dtype': str(data.dtype),
                'nodata': src.nodata
            }
            
            # Handle single or multi-band data
            if data.ndim == 3 and data.shape[0] == 1:
                data_2d = data[0]
            else:
                data_2d = data
            
            # Calculate statistics
            valid_data = data_2d[~np.isnan(data_2d)]
            if len(valid_data) > 0:
                stats = {
                    'min': float(valid_data.min()),
                    'max': float(valid_data.max()),
                    'mean': float(valid_data.mean()),
                    'std': float(valid_data.std()),
                    'percentiles': {
                        '1': float(np.percentile(valid_data, 1)),
                        '5': float(np.percentile(valid_data, 5)),
                        '25': float(np.percentile(valid_data, 25)),
                        '50': float(np.percentile(valid_data, 50)),
                        '75': float(np.percentile(valid_data, 75)),
                        '95': float(np.percentile(valid_data, 95)),
                        '99': float(np.percentile(valid_data, 99))
                    }
                }
            else:
                stats = {}
            
            return {
                'data': data_2d,
                'metadata': metadata,
                'statistics': stats,
                'valid_pixels': len(valid_data),
                'total_pixels': data_2d.size
            }
    
    @st.cache_data
    def run_sam_analysis(_self, _sam_processor: ForestSAMProcessor = None) -> Dict:
        """
        Run SAM analysis with caching (use _ prefix to avoid hashing the processor)
        
        Returns:
            Dictionary containing SAM analysis results
        """
        try:
            if _sam_processor is None:
                _sam_processor = ForestSAMProcessor(model_type="vit_b")
                _sam_processor.load_model()
            
            # Load data
            data_path = Path("data/east_troublesome_small_tile.tif")
            ndvi_data, metadata = _sam_processor.load_geotiff(data_path)
            
            # Convert to RGB
            rgb_image = _sam_processor.ndvi_to_rgb(ndvi_data)
            
            # Run segmentation
            segmentation_results = _sam_processor.segment_forest_areas(rgb_image)
            
            # Classify vegetation health
            classification_results = _sam_processor.classify_vegetation_health(
                ndvi_data, segmentation_results
            )
            
            return {
                'ndvi_data': ndvi_data,
                'rgb_image': rgb_image,
                'segmentation': segmentation_results,
                'classification': classification_results,
                'metadata': metadata
            }
            
        except Exception as e:
            st.error(f"SAM analysis failed: {e}")
            return {}
    
    def get_vegetation_health_stats(self, classification_results: Dict) -> Dict:
        """Extract and format vegetation health statistics"""
        if not classification_results:
            return {}
            
        stats = classification_results.get('statistics', {})
        
        return {
            'total_vegetation_pixels': stats.get('total_vegetation_pixels', 0),
            'healthy': {
                'pixels': stats.get('healthy_pixels', 0),
                'percent': stats.get('healthy_percent', 0)
            },
            'stressed': {
                'pixels': stats.get('stressed_pixels', 0),
                'percent': stats.get('stressed_percent', 0)
            },
            'declining': {
                'pixels': stats.get('declining_pixels', 0),
                'percent': stats.get('declining_percent', 0)
            },
            'dead': {
                'pixels': stats.get('dead_pixels', 0),
                'percent': stats.get('dead_percent', 0)
            }
        }
    
    def create_vegetation_health_chart(self, stats: Dict) -> go.Figure:
        """Create interactive vegetation health visualization"""
        if not stats:
            return go.Figure()
        
        # Prepare data
        categories = ['Healthy', 'Stressed', 'Declining', 'Dead']
        percentages = [
            stats['healthy']['percent'],
            stats['stressed']['percent'], 
            stats['declining']['percent'],
            stats['dead']['percent']
        ]
        pixels = [
            stats['healthy']['pixels'],
            stats['stressed']['pixels'],
            stats['declining']['pixels'], 
            stats['dead']['pixels']
        ]
        
        colors = ['#2E8B57', '#FFA500', '#FF4500', '#8B0000']  # Green, Orange, Red, Dark Red
        
        # Create subplots
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{"type": "pie"}, {"type": "bar"}]],
            subplot_titles=("Vegetation Health Distribution", "Pixel Counts by Category")
        )
        
        # Pie chart
        fig.add_trace(
            go.Pie(
                labels=categories,
                values=percentages,
                name="Vegetation Health",
                marker_colors=colors,
                textinfo='label+percent',
                textposition='auto'
            ),
            row=1, col=1
        )
        
        # Bar chart
        fig.add_trace(
            go.Bar(
                x=categories,
                y=pixels,
                name="Pixel Count",
                marker_color=colors,
                text=[f"{p:,}" for p in pixels],
                textposition='auto'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title_text="East Troublesome Fire - Vegetation Health Analysis",
            title_x=0.5,
            height=500,
            showlegend=False
        )
        
        return fig
    
    def create_ndvi_histogram(self, geotiff_data: Dict) -> go.Figure:
        """Create NDVI value distribution histogram"""
        if not geotiff_data or 'data' not in geotiff_data:
            return go.Figure()
        
        data = geotiff_data['data']
        valid_data = data[~np.isnan(data)]
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=valid_data,
            nbinsx=50,
            name='NDVI Difference',
            marker_color='rgba(0, 123, 255, 0.7)',
            opacity=0.8
        ))
        
        # Add threshold lines
        fig.add_vline(x=0.1, line_dash="dash", line_color="green", 
                     annotation_text="Healthy Threshold (0.1)")
        fig.add_vline(x=-0.1, line_dash="dash", line_color="orange",
                     annotation_text="Stressed Threshold (-0.1)")
        fig.add_vline(x=-0.3, line_dash="dash", line_color="red",
                     annotation_text="Dead Threshold (-0.3)")
        
        fig.update_layout(
            title="NDVI Difference Distribution (Pre-Fire vs Post-Fire)",
            xaxis_title="NDVI Difference",
            yaxis_title="Pixel Count",
            height=400,
            bargap=0.1
        )
        
        return fig
    
    def create_folium_map(self, geotiff_data: Dict, sam_results: Dict = None) -> folium.Map:
        """Create interactive Folium map with data overlays"""
        if not geotiff_data or 'metadata' not in geotiff_data:
            # Default map centered on Colorado
            return folium.Map(location=[40.2, -105.8], zoom_start=10)
        
        bounds = geotiff_data['metadata']['bounds']
        
        # Calculate center
        center_lat = (bounds.bottom + bounds.top) / 2
        center_lon = (bounds.left + bounds.right) / 2
        
        # Create base map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=13,
            tiles=None
        )
        
        # Add base layers
        folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m)
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Satellite',
            overlay=False
        ).add_to(m)
        
        # Add NDVI data as overlay if available
        if 'data' in geotiff_data:
            # Create bounds for the overlay
            bounds_list = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]
            
            # Convert NDVI data to image for overlay
            ndvi_data = geotiff_data['data']
            
            # Normalize for display
            vmin, vmax = np.percentile(ndvi_data[~np.isnan(ndvi_data)], [2, 98])
            ndvi_normalized = np.clip((ndvi_data - vmin) / (vmax - vmin), 0, 1)
            
            # Convert to RGB using colormap
            import matplotlib.pyplot as plt
            cmap = plt.get_cmap('RdYlGn')
            rgb_array = cmap(ndvi_normalized)[:, :, :3]  # Remove alpha
            rgb_uint8 = (rgb_array * 255).astype(np.uint8)
            
            # Convert to base64 for Folium
            img = Image.fromarray(rgb_uint8)
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_str = base64.b64encode(img_buffer.getvalue()).decode()
            
            # Add as image overlay
            folium.raster_layers.ImageOverlay(
                image=f"data:image/png;base64,{img_str}",
                bounds=bounds_list,
                name='NDVI Difference',
                opacity=0.7
            ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add marker for the study area
        folium.Marker(
            [center_lat, center_lon],
            popup=f"""
            <b>East Troublesome Fire Study Area</b><br>
            Coordinates: {center_lat:.4f}, {center_lon:.4f}<br>
            Area: ~1.2 km²<br>
            Resolution: 10m Sentinel-2
            """,
            icon=folium.Icon(color='red', icon='fire')
        ).add_to(m)
        
        return m
    
    def get_export_data(self, sam_results: Dict, format_type: str = 'json') -> bytes:
        """Prepare data for export in various formats"""
        if not sam_results:
            return b""
        
        if format_type.lower() == 'json':
            # Export statistics as JSON
            stats = self.get_vegetation_health_stats(sam_results.get('classification', {}))
            export_data = {
                'analysis_type': 'Forest Die-off Analysis (SAM)',
                'location': 'East Troublesome Fire, Colorado',
                'analysis_date': pd.Timestamp.now().isoformat(),
                'results': stats,
                'metadata': {
                    'model': 'Segment Anything Model (SAM)',
                    'data_source': 'Sentinel-2 NDVI Difference',
                    'resolution': '10m',
                    'area_km2': 1.2
                }
            }
            return json.dumps(export_data, indent=2).encode('utf-8')
        
        elif format_type.lower() == 'csv':
            # Export as CSV
            stats = self.get_vegetation_health_stats(sam_results.get('classification', {}))
            df = pd.DataFrame([
                {'Category': 'Healthy', 'Pixels': stats['healthy']['pixels'], 'Percent': stats['healthy']['percent']},
                {'Category': 'Stressed', 'Pixels': stats['stressed']['pixels'], 'Percent': stats['stressed']['percent']},
                {'Category': 'Declining', 'Pixels': stats['declining']['pixels'], 'Percent': stats['declining']['percent']},
                {'Category': 'Dead', 'Pixels': stats['dead']['pixels'], 'Percent': stats['dead']['percent']}
            ])
            return df.to_csv(index=False).encode('utf-8')
        
        return b""
    
    def load_results_image(self) -> Optional[Image.Image]:
        """Load the generated results visualization"""
        results_path = self.outputs_dir / "forest_analysis_results.png"
        if results_path.exists():
            return Image.open(results_path)
        return None 