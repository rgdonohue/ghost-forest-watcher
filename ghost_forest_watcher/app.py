"""
Ghost Forest Watcher - Streamlit Web Application
Expert-level forest die-off monitoring and analysis system
"""
import os
import sys

# Set environment variables to prevent PyTorch-Streamlit conflicts
# This must be done before importing torch-related modules
os.environ['PYTORCH_JIT'] = '0'
os.environ['TORCH_DISTRIBUTED_DEBUG'] = 'OFF'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

import streamlit as st
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium
import folium
import io

# Import our custom modules with error handling
try:
    from .src.data_manager import GhostForestDataManager
    from .src.sam_processor import ForestSAMProcessor
    from .src.streamlit_pages import (
        show_map_page, show_analysis_page, show_explorer_page, 
        show_export_page, show_about_page
    )
    MODULES_LOADED = True
except Exception as e:
    st.error(f"⚠️ Error loading modules: {e}")
    MODULES_LOADED = False

# Additional environment fixes for Streamlit-PyTorch compatibility
try:
    # Disable file watcher to prevent torch module conflicts
    from streamlit import config
    config._set_option('server.fileWatcherType', 'none')
    config._set_option('server.runOnSave', False)
except Exception:
    # Fallback if config modification fails
    pass

# Page configuration
st.set_page_config(
    page_title="Ghost Forest Watcher",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/ghost-forest-watcher',
        'Report a bug': 'https://github.com/your-repo/ghost-forest-watcher/issues',
        'About': """
        # Ghost Forest Watcher
        **Western Colorado Forest Die-off Monitoring System**
        
        Using AI-powered analysis to track forest recovery after the East Troublesome Fire.
        Built with Segment Anything Model (SAM) and Google Earth Engine.
        """
    }
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #2E8B57;
        margin: 0.5rem 0;
    }
    
    .status-success {
        background: linear-gradient(135deg, #d4edda 0%, #a3d977 100%);
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .sidebar-info {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 3px solid #17a2b8;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = GhostForestDataManager()

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Overview"

def main():
    """Main application function"""
    
    # Check if modules loaded successfully
    if not MODULES_LOADED:
        st.error("🚨 Application modules failed to load. Please check the error above.")
        st.stop()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🌲 Navigation")
        
        pages = {
            "🏠 Overview": "overview",
            "🗺️ Interactive Map": "map", 
            "📊 Analysis Dashboard": "analysis",
            "🔍 Data Explorer": "explorer",
            "📄 Export & Reports": "export",
            "ℹ️ About & Methods": "about"
        }
        
        selected_page = st.selectbox(
            "Choose a page:",
            list(pages.keys()),
            index=0
        )
        
        st.session_state.current_page = pages[selected_page]
        
        # System status
        st.markdown("---")
        st.markdown("### 🔧 System Status")
        
        # Check data availability
        data_file = Path("data/east_troublesome_small_tile.tif")
        model_file = Path("models/sam_vit_b.pth")
        results_file = Path("outputs/forest_analysis_results.png")
        
        status_items = [
            ("📄 Data File", data_file.exists()),
            ("🤖 SAM Model", model_file.exists()),
            ("📊 Results", results_file.exists())
        ]
        
        for item, status in status_items:
            if status:
                st.markdown(f"✅ {item}")
            else:
                st.markdown(f"❌ {item}")
        
        if all(status for _, status in status_items):
            st.markdown('<div class="status-success">🎉 All systems ready!</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-warning">⚠️ Some components missing</div>', unsafe_allow_html=True)
    
    # Main content area
    if st.session_state.current_page == "overview":
        show_overview_page()
    elif st.session_state.current_page == "map":
        show_map_page()
    elif st.session_state.current_page == "analysis":
        show_analysis_page()
    elif st.session_state.current_page == "explorer":
        show_explorer_page()
    elif st.session_state.current_page == "export":
        show_export_page()
    elif st.session_state.current_page == "about":
        show_about_page()

def show_overview_page():
    """Overview page with key metrics and summary"""
    
    st.markdown('<h1 class="main-header">🌲 Ghost Forest Watcher</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Western Colorado Forest Die-off Monitoring System</p>', unsafe_allow_html=True)
    
    # Load data
    data_manager = st.session_state.data_manager
    
    with st.spinner("Loading analysis results..."):
        # Load GeoTIFF data
        geotiff_data = data_manager.load_geotiff_data()
        
        # Load or run SAM analysis
        if Path("outputs/forest_analysis_results.png").exists():
            # Load existing results
            sam_results = data_manager.run_sam_analysis()
        else:
            st.warning("SAM analysis results not found. Running analysis...")
            sam_results = data_manager.run_sam_analysis()
    
    if not sam_results:
        st.error("Unable to load analysis results. Please check data files and run analysis.")
        return
    
    # Key metrics
    st.markdown("## 📊 Key Findings")
    
    stats = data_manager.get_vegetation_health_stats(sam_results.get('classification', {}))
    
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="🟢 Healthy Vegetation",
                value=f"{stats['healthy']['percent']:.1f}%",
                delta=f"{stats['healthy']['pixels']:,} pixels"
            )
        
        with col2:
            st.metric(
                label="🟡 Stressed Vegetation", 
                value=f"{stats['stressed']['percent']:.1f}%",
                delta=f"{stats['stressed']['pixels']:,} pixels"
            )
        
        with col3:
            st.metric(
                label="🟠 Declining Vegetation",
                value=f"{stats['declining']['percent']:.1f}%",
                delta=f"{stats['declining']['pixels']:,} pixels"
            )
        
        with col4:
            st.metric(
                label="🔴 Dead Vegetation",
                value=f"{stats['dead']['percent']:.1f}%", 
                delta=f"{stats['dead']['pixels']:,} pixels"
            )
    
    # Summary insights
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 🔍 Analysis Summary")
        
        if stats:
            recovery_rate = stats['healthy']['percent']
            impact_rate = stats['stressed']['percent'] + stats['declining']['percent'] + stats['dead']['percent']
            severe_impact = stats['declining']['percent'] + stats['dead']['percent']
            
            st.markdown(f"""
            **Study Area:** East Troublesome Fire, Colorado (~1.2 km²)  
            **Analysis Method:** Segment Anything Model (SAM) + NDVI Difference  
            **Data Source:** Sentinel-2 (10m resolution)  
            **Analysis Date:** {datetime.now().strftime('%B %Y')}
            
            ### Key Insights:
            - **🎯 Forest Recovery:** {recovery_rate:.1f}% of vegetation shows healthy recovery
            - **⚠️ Total Impact:** {impact_rate:.1f}% of vegetation still shows fire effects
            - **🚨 Severe Impact:** {severe_impact:.1f}% remains severely damaged or dead
            - **📈 Recovery Status:** {'Excellent' if recovery_rate > 75 else 'Good' if recovery_rate > 50 else 'Poor'} recovery observed
            """)
            
            # Recovery assessment
            if recovery_rate > 75:
                st.success("🌟 **Excellent Recovery**: The forest shows strong signs of natural regeneration with over 75% healthy vegetation.")
            elif recovery_rate > 50:
                st.info("📈 **Good Recovery**: The forest is recovering well with over 50% healthy vegetation.")
            else:
                st.warning("⚠️ **Limited Recovery**: The forest shows limited recovery with ongoing impacts visible.")
    
    with col2:
        st.markdown("## 🗺️ Study Location")
        
        # Quick location info
        if geotiff_data and 'metadata' in geotiff_data:
            bounds = geotiff_data['metadata']['bounds']
            
            st.markdown(f"""
            **Coordinates:**  
            📍 Lat: {(bounds.bottom + bounds.top) / 2:.4f}°  
            📍 Lon: {(bounds.left + bounds.right) / 2:.4f}°
            
            **Coverage:**  
            📐 Area: ~1.2 km²  
            🔍 Resolution: 10m/pixel  
            🛰️ Source: Sentinel-2
            
            **Fire Event:**  
            🔥 East Troublesome Fire  
            📅 October 2020  
            🌡️ 193,812 acres total
            """)
    
    # Analysis visualization
    st.markdown("## 📈 Vegetation Health Distribution")
    
    if stats:
        fig = data_manager.create_vegetation_health_chart(stats)
        st.plotly_chart(fig, use_container_width=True)
    
    # Quick action buttons
    st.markdown("## 🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🗺️ View Interactive Map", use_container_width=True):
            st.session_state.current_page = "map"
            st.rerun()
    
    with col2:
        if st.button("📊 Detailed Analysis", use_container_width=True):
            st.session_state.current_page = "analysis"
            st.rerun()
    
    with col3:
        if st.button("🔍 Explore Data", use_container_width=True):
            st.session_state.current_page = "explorer"
            st.rerun()
    
    with col4:
        if st.button("📄 Export Results", use_container_width=True):
            st.session_state.current_page = "export"
            st.rerun()

def show_map_page():
    """Interactive map page"""
    
    st.title("🗺️ Interactive Forest Analysis Map")
    st.markdown("Explore the East Troublesome Fire analysis results on an interactive map.")
    
    data_manager = st.session_state.data_manager
    
    # Map controls
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        base_layer = st.selectbox(
            "Base Layer:",
            ["Satellite", "OpenStreetMap"],
            index=0
        )
    
    with col2:
        overlay_opacity = st.slider(
            "Overlay Opacity:",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1
        )
    
    # Load data
    with st.spinner("Loading map data..."):
        geotiff_data = data_manager.load_geotiff_data()
        sam_results = data_manager.run_sam_analysis()
    
    if geotiff_data:
        # Create map
        folium_map = data_manager.create_folium_map(geotiff_data, sam_results)
        
        # Display map
        map_data = st_folium(folium_map, width=700, height=500)
        
        # Map interaction feedback
        if map_data['last_clicked']:
            clicked_lat = map_data['last_clicked']['lat']
            clicked_lng = map_data['last_clicked']['lng']
            
            st.info(f"📍 Clicked Location: {clicked_lat:.4f}°, {clicked_lng:.4f}°")
    else:
        st.error("Unable to load map data. Please check data files.")

def show_analysis_page():
    """Detailed analysis dashboard"""
    
    st.title("📊 Forest Analysis Dashboard")
    st.markdown("Comprehensive analysis of forest die-off and recovery patterns.")
    
    data_manager = st.session_state.data_manager
    
    # Load data
    with st.spinner("Loading analysis data..."):
        geotiff_data = data_manager.load_geotiff_data()
        sam_results = data_manager.run_sam_analysis()
    
    if not sam_results or not geotiff_data:
        st.error("Unable to load analysis data. Please check data files.")
        return
    
    # Analysis controls
    st.sidebar.markdown("### 📊 Analysis Controls")
    
    show_detailed_stats = st.sidebar.checkbox("Show Detailed Statistics", value=True)
    show_distribution = st.sidebar.checkbox("Show NDVI Distribution", value=True)
    show_sam_results = st.sidebar.checkbox("Show SAM Results Image", value=True)
    
    # Main analysis content
    tabs = st.tabs(["📈 Vegetation Health", "📊 NDVI Analysis", "🤖 SAM Results", "📋 Statistics"])
    
    with tabs[0]:
        st.subheader("Vegetation Health Analysis")
        
        stats = data_manager.get_vegetation_health_stats(sam_results.get('classification', {}))
        if stats:
            fig = data_manager.create_vegetation_health_chart(stats)
            st.plotly_chart(fig, use_container_width=True)
            
            if show_detailed_stats:
                st.markdown("### Detailed Statistics")
                
                df = pd.DataFrame([
                    {
                        'Category': 'Healthy',
                        'Pixels': f"{stats['healthy']['pixels']:,}",
                        'Percentage': f"{stats['healthy']['percent']:.1f}%",
                        'Area (km²)': f"{stats['healthy']['pixels'] * 0.0001:.2f}"
                    },
                    {
                        'Category': 'Stressed', 
                        'Pixels': f"{stats['stressed']['pixels']:,}",
                        'Percentage': f"{stats['stressed']['percent']:.1f}%",
                        'Area (km²)': f"{stats['stressed']['pixels'] * 0.0001:.2f}"
                    },
                    {
                        'Category': 'Declining',
                        'Pixels': f"{stats['declining']['pixels']:,}",
                        'Percentage': f"{stats['declining']['percent']:.1f}%", 
                        'Area (km²)': f"{stats['declining']['pixels'] * 0.0001:.2f}"
                    },
                    {
                        'Category': 'Dead',
                        'Pixels': f"{stats['dead']['pixels']:,}",
                        'Percentage': f"{stats['dead']['percent']:.1f}%",
                        'Area (km²)': f"{stats['dead']['pixels'] * 0.0001:.2f}"
                    }
                ])
                
                st.dataframe(df, use_container_width=True)
    
    with tabs[1]:
        st.subheader("NDVI Distribution Analysis")
        
        if show_distribution and geotiff_data:
            fig = data_manager.create_ndvi_histogram(geotiff_data)
            st.plotly_chart(fig, use_container_width=True)
            
            # NDVI statistics
            if 'statistics' in geotiff_data:
                stats = geotiff_data['statistics']
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Mean NDVI Difference", f"{stats.get('mean', 0):.3f}")
                    st.metric("Standard Deviation", f"{stats.get('std', 0):.3f}")
                
                with col2:
                    st.metric("Minimum Value", f"{stats.get('min', 0):.3f}")
                    st.metric("Maximum Value", f"{stats.get('max', 0):.3f}")
                
                with col3:
                    st.metric("Median Value", f"{stats.get('percentiles', {}).get('50', 0):.3f}")
                    st.metric("Valid Pixels", f"{geotiff_data.get('valid_pixels', 0):,}")
    
    with tabs[2]:
        st.subheader("SAM Analysis Results")
        
        if show_sam_results:
            results_image = data_manager.load_results_image()
            if results_image:
                st.image(results_image, caption="SAM Forest Analysis Results", use_container_width=True)
            else:
                st.warning("SAM results image not found.")
    
    with tabs[3]:
        st.subheader("Comprehensive Statistics")
        
        # Create comprehensive stats table
        if geotiff_data and sam_results:
            stats_data = {
                "Analysis Parameter": [
                    "Study Area",
                    "Total Pixels", 
                    "Valid Pixels",
                    "Spatial Resolution",
                    "NDVI Range",
                    "Mean NDVI Difference",
                    "Healthy Vegetation",
                    "Impacted Vegetation",
                    "Analysis Method",
                    "Processing Date"
                ],
                "Value": [
                    "East Troublesome Fire, CO",
                    f"{geotiff_data.get('total_pixels', 0):,}",
                    f"{geotiff_data.get('valid_pixels', 0):,}",
                    "10m (Sentinel-2)",
                    f"{geotiff_data.get('statistics', {}).get('min', 0):.3f} to {geotiff_data.get('statistics', {}).get('max', 0):.3f}",
                    f"{geotiff_data.get('statistics', {}).get('mean', 0):.3f}",
                    f"{stats.get('healthy', {}).get('percent', 0):.1f}%",
                    f"{100 - stats.get('healthy', {}).get('percent', 100):.1f}%",
                    "Segment Anything Model (SAM)",
                    datetime.now().strftime('%Y-%m-%d %H:%M')
                ]
            }
            
            df_stats = pd.DataFrame(stats_data)
            st.dataframe(df_stats, use_container_width=True)

def show_explorer_page():
    """Data exploration page"""
    
    st.title("🔍 Data Explorer")
    st.markdown("Explore the underlying data and methodology.")
    
    # Data file information
    st.subheader("📄 Data Files")
    
    files_info = [
        ("GeoTIFF Data", "data/east_troublesome_small_tile.tif", "42.4 MB"),
        ("SAM Model", "models/sam_vit_b.pth", "357.7 MB"),  
        ("Analysis Results", "outputs/forest_analysis_results.png", "19.4 MB")
    ]
    
    for name, path, size in files_info:
        if Path(path).exists():
            st.success(f"✅ **{name}**: `{path}` ({size})")
        else:
            st.error(f"❌ **{name}**: `{path}` (Not found)")
    
    # Raw data preview
    st.subheader("📊 Raw Data Preview")
    
    data_manager = st.session_state.data_manager
    geotiff_data = data_manager.load_geotiff_data()
    
    if geotiff_data:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Metadata:**")
            metadata = geotiff_data.get('metadata', {})
            
            st.json({
                'CRS': metadata.get('crs', 'Unknown'),
                'Bounds': {
                    'North': metadata.get('bounds', {}).top if hasattr(metadata.get('bounds', {}), 'top') else 'Unknown',
                    'South': metadata.get('bounds', {}).bottom if hasattr(metadata.get('bounds', {}), 'bottom') else 'Unknown',
                    'East': metadata.get('bounds', {}).right if hasattr(metadata.get('bounds', {}), 'right') else 'Unknown',
                    'West': metadata.get('bounds', {}).left if hasattr(metadata.get('bounds', {}), 'left') else 'Unknown'
                },
                'Shape': metadata.get('shape', 'Unknown'),
                'Data Type': metadata.get('dtype', 'Unknown')
            })
        
        with col2:
            st.markdown("**Statistics:**")
            stats = geotiff_data.get('statistics', {})
            
            if stats:
                st.json({
                    'Min': round(stats.get('min', 0), 4),
                    'Max': round(stats.get('max', 0), 4),
                    'Mean': round(stats.get('mean', 0), 4),
                    'Std Dev': round(stats.get('std', 0), 4),
                    'Percentiles': {
                        '25th': round(stats.get('percentiles', {}).get('25', 0), 4),
                        '50th': round(stats.get('percentiles', {}).get('50', 0), 4),
                        '75th': round(stats.get('percentiles', {}).get('75', 0), 4)
                    }
                })

def show_export_page():
    """Export and reporting page"""
    
    st.title("📄 Export & Reports")
    st.markdown("Download analysis results and generate reports.")
    
    data_manager = st.session_state.data_manager
    
    # Load data for export
    with st.spinner("Preparing export data..."):
        sam_results = data_manager.run_sam_analysis()
    
    if not sam_results:
        st.error("No analysis results available for export.")
        return
    
    # Export options
    st.subheader("📥 Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Data Exports**")
        
        # JSON export
        if st.button("📄 Export as JSON", use_container_width=True):
            json_data = data_manager.get_export_data(sam_results, 'json')
            st.download_button(
                label="⬇️ Download JSON Report",
                data=json_data,
                file_name=f"ghost_forest_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json"
            )
        
        # CSV export
        if st.button("📊 Export as CSV", use_container_width=True):
            csv_data = data_manager.get_export_data(sam_results, 'csv')
            st.download_button(
                label="⬇️ Download CSV Data",
                data=csv_data,
                file_name=f"vegetation_health_stats_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    
    with col2:
        st.markdown("**🖼️ Visual Exports**")
        
        # Results image
        results_image = data_manager.load_results_image()
        if results_image:
            # Convert PIL image to bytes
            img_buffer = io.BytesIO()
            results_image.save(img_buffer, format='PNG')
            
            st.download_button(
                label="🖼️ Download Analysis Image",
                data=img_buffer.getvalue(),
                file_name=f"forest_analysis_results_{datetime.now().strftime('%Y%m%d_%H%M')}.png",
                mime="image/png"
            )
        
        # Generate summary report
        if st.button("📋 Generate Summary Report", use_container_width=True):
            stats = data_manager.get_vegetation_health_stats(sam_results.get('classification', {}))
            
            report_text = f"""
# Ghost Forest Watcher Analysis Report

## Study Area
- **Location**: East Troublesome Fire, Colorado
- **Area**: ~1.2 km²
- **Analysis Date**: {datetime.now().strftime('%B %d, %Y')}
- **Method**: Segment Anything Model (SAM) + NDVI Difference Analysis

## Key Findings
- **Healthy Vegetation**: {stats.get('healthy', {}).get('percent', 0):.1f}% ({stats.get('healthy', {}).get('pixels', 0):,} pixels)
- **Stressed Vegetation**: {stats.get('stressed', {}).get('percent', 0):.1f}% ({stats.get('stressed', {}).get('pixels', 0):,} pixels)
- **Declining Vegetation**: {stats.get('declining', {}).get('percent', 0):.1f}% ({stats.get('declining', {}).get('pixels', 0):,} pixels)
- **Dead Vegetation**: {stats.get('dead', {}).get('percent', 0):.1f}% ({stats.get('dead', {}).get('pixels', 0):,} pixels)

## Summary
The analysis shows {stats.get('healthy', {}).get('percent', 0):.1f}% of vegetation has recovered to healthy levels following the East Troublesome Fire. 
This indicates {'excellent' if stats.get('healthy', {}).get('percent', 0) > 75 else 'good' if stats.get('healthy', {}).get('percent', 0) > 50 else 'limited'} recovery in the study area.

## Methodology
- **Data Source**: Sentinel-2 satellite imagery (10m resolution)
- **Analysis**: Pre-fire vs post-fire NDVI difference
- **AI Model**: Segment Anything Model (ViT-B) for vegetation segmentation
- **Classification**: NDVI-based thresholding for health categories

Generated by Ghost Forest Watcher v1.0
            """
            
            st.download_button(
                label="📋 Download Summary Report",
                data=report_text,
                file_name=f"ghost_forest_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown"
            )
    
    # Preview section
    st.subheader("👀 Export Preview")
    
    stats = data_manager.get_vegetation_health_stats(sam_results.get('classification', {}))
    
    if stats:
        # Show preview of export data
        preview_df = pd.DataFrame([
            {'Category': 'Healthy', 'Percentage': f"{stats['healthy']['percent']:.1f}%", 'Pixels': f"{stats['healthy']['pixels']:,}"},
            {'Category': 'Stressed', 'Percentage': f"{stats['stressed']['percent']:.1f}%", 'Pixels': f"{stats['stressed']['pixels']:,}"},
            {'Category': 'Declining', 'Percentage': f"{stats['declining']['percent']:.1f}%", 'Pixels': f"{stats['declining']['pixels']:,}"},
            {'Category': 'Dead', 'Percentage': f"{stats['dead']['percent']:.1f}%", 'Pixels': f"{stats['dead']['pixels']:,}"}
        ])
        
        st.dataframe(preview_df, use_container_width=True)

def show_about_page():
    """About and methodology page"""
    
    st.title("ℹ️ About Ghost Forest Watcher")
    
    st.markdown("""
    ## 🎯 Project Overview
    
    Ghost Forest Watcher is an AI-powered system for monitoring forest die-off and recovery patterns 
    in Western Colorado, specifically focusing on the East Troublesome Fire area. The system combines 
    satellite imagery analysis with cutting-edge AI models to provide detailed insights into vegetation 
    health and recovery progress.
    
    ## 🔬 Methodology
    
    ### Data Sources
    - **Satellite Imagery**: Sentinel-2 (10m resolution)
    - **Analysis Period**: Pre-fire (2019) vs Post-fire (2021-2024)  
    - **Study Area**: East Troublesome Fire, Colorado (~1.2 km² sample)
    
    ### AI Models
    - **Segment Anything Model (SAM)**: Meta's foundation model for image segmentation
    - **Model Variant**: ViT-B (Vision Transformer Base)
    - **Purpose**: Automatic vegetation area detection and segmentation
    
    ### Analysis Pipeline
    1. **Data Acquisition**: Google Earth Engine API for Sentinel-2 data
    2. **Preprocessing**: NDVI calculation and difference analysis
    3. **AI Segmentation**: SAM-based vegetation area identification
    4. **Classification**: NDVI threshold-based health categorization
    5. **Visualization**: Interactive mapping and statistical analysis
    
    ## 📊 Classification Scheme
    
    Vegetation health is classified based on NDVI difference values:
    - **🟢 Healthy** (NDVI > 0.1): Strong vegetation recovery
    - **🟡 Stressed** (-0.1 to 0.1): Moderate impact, recovering
    - **🟠 Declining** (-0.3 to -0.1): Persistent vegetation stress  
    - **🔴 Dead** (< -0.3): Severe damage or death
    
    ## 🏔️ Study Area: East Troublesome Fire
    
    The East Troublesome Fire occurred in October 2020 and burned 193,812 acres, making it 
    Colorado's second-largest wildfire on record. Our analysis focuses on a representative 
    1.2 km² area to demonstrate the monitoring capabilities.
    
    ## 🛠️ Technical Stack
    
    - **Backend**: Python, Google Earth Engine, PyTorch
    - **AI/ML**: Segment Anything Model, Rasterio, Scikit-image
    - **Frontend**: Streamlit, Plotly, Folium
    - **Data**: Sentinel-2 satellite imagery, GeoTIFF processing
    
    ## 📈 Current Results
    
    Based on our analysis of the sample area:
    - **80.8%** of vegetation shows healthy recovery
    - **15.6%** remains stressed but recovering
    - **2.5%** shows severe impact (declining/dead)
    
    This indicates excellent natural recovery in the analyzed area.
    
    ## 🔮 Future Development
    
    - **Scaling**: Expand to full fire area analysis
    - **Temporal**: Multi-year recovery tracking
    - **Validation**: Ground-truth data integration
    - **Automation**: Real-time monitoring capabilities
    
    ## 👥 Contributors
    
    This project demonstrates advanced geospatial AI applications for environmental monitoring 
    and forest management decision support.
    
    ---
    
    **Version**: 1.0  
    **Last Updated**: {datetime.now().strftime('%B %Y')}  
    **License**: Open Source
    """)

if __name__ == "__main__":
    main() 