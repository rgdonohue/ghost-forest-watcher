"""
Ghost Forest Watcher - Safe Mode
Version without PyTorch dependencies for troubleshooting
"""
import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Set environment variables to prevent conflicts
os.environ['PYTORCH_JIT'] = '0'
os.environ['TORCH_DISTRIBUTED_DEBUG'] = 'OFF'

# Page configuration
st.set_page_config(
    page_title="Ghost Forest Watcher (Safe Mode)",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application function - safe mode"""
    
    st.title("🌲 Ghost Forest Watcher - Safe Mode")
    st.info("🔧 Running in safe mode to avoid PyTorch-Streamlit conflicts")
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🌲 Navigation")
        
        pages = {
            "🏠 Overview": "overview",
            "🗺️ Basic Map": "map", 
            "📊 Simple Analysis": "analysis",
            "ℹ️ About": "about"
        }
        
        selected_page = st.selectbox(
            "Choose a page:",
            list(pages.keys()),
            index=0
        )
        
        current_page = pages[selected_page]
        
        # System status
        st.markdown("---")
        st.markdown("### 🔧 System Status")
        
        # Check data availability
        data_file = Path("data/east_troublesome_small_tile.tif")
        results_file = Path("outputs/forest_analysis_results.png")
        
        status_items = [
            ("📄 Data File", data_file.exists()),
            ("📊 Results", results_file.exists()),
            ("🚀 Safe Mode", True)
        ]
        
        for item, status in status_items:
            if status:
                st.markdown(f"✅ {item}")
            else:
                st.markdown(f"❌ {item}")
    
    # Main content
    if current_page == "overview":
        show_overview_safe()
    elif current_page == "map":
        show_map_safe()
    elif current_page == "analysis":
        show_analysis_safe()
    elif current_page == "about":
        show_about_safe()

def show_overview_safe():
    """Safe overview page without SAM dependencies"""
    
    st.markdown("## 📊 Overview - Safe Mode")
    st.markdown("""
    This is the safe mode version of Ghost Forest Watcher that runs without PyTorch dependencies.
    """)
    
    # Mock statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Study Area", "1.2 km²")
        
    with col2:
        st.metric("Resolution", "10m")
        
    with col3:
        st.metric("Data Source", "Sentinel-2")
        
    with col4:
        st.metric("Status", "Safe Mode")
    
    # Sample chart
    st.markdown("### 📈 Sample Data Visualization")
    
    # Create sample data
    categories = ['Healthy', 'Stressed', 'Declining', 'Dead']
    values = [45, 25, 20, 10]
    
    fig = px.pie(
        values=values,
        names=categories,
        title="Sample Vegetation Health Distribution",
        color_discrete_sequence=['#2E8B57', '#FFA500', '#FF4500', '#8B0000']
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_map_safe():
    """Safe map page without complex dependencies"""
    
    st.title("🗺️ Basic Map View")
    st.markdown("Simple map interface without SAM analysis.")
    
    # Simple map placeholder
    st.markdown("### 📍 Study Area Location")
    
    # Create a simple scatter plot as map substitute
    df = pd.DataFrame({
        'lat': [40.2],
        'lon': [-105.8],
        'name': ['East Troublesome Fire Area']
    })
    
    st.map(df)
    
    st.info("📍 East Troublesome Fire study area, Colorado")

def show_analysis_safe():
    """Safe analysis page with sample data"""
    
    st.title("📊 Simple Analysis")
    st.markdown("Basic analysis without machine learning components.")
    
    # Sample time series
    dates = pd.date_range('2020-01-01', '2023-12-31', freq='M')
    ndvi_values = np.random.normal(0.7, 0.1, len(dates))
    
    df = pd.DataFrame({
        'Date': dates,
        'NDVI': ndvi_values
    })
    
    fig = px.line(df, x='Date', y='NDVI', title='Sample NDVI Time Series')
    st.plotly_chart(fig, use_container_width=True)
    
    # Sample statistics table
    st.markdown("### 📋 Sample Statistics")
    
    stats_df = pd.DataFrame({
        'Metric': ['Mean NDVI', 'Std Dev', 'Min Value', 'Max Value'],
        'Value': [f"{ndvi_values.mean():.3f}", f"{ndvi_values.std():.3f}", 
                 f"{ndvi_values.min():.3f}", f"{ndvi_values.max():.3f}"]
    })
    
    st.dataframe(stats_df, use_container_width=True)

def show_about_safe():
    """About page"""
    
    st.title("ℹ️ About Ghost Forest Watcher")
    
    st.markdown("""
    ## 🌲 Project Overview
    
    Ghost Forest Watcher is a forest monitoring system designed to track vegetation health 
    and recovery patterns after forest fires using satellite imagery and AI analysis.
    
    ## 🔧 Safe Mode
    
    You are currently running in **Safe Mode** which:
    - ✅ Avoids PyTorch-Streamlit compatibility issues
    - ✅ Provides basic functionality for testing
    - ✅ Allows interface exploration without dependencies
    - ❌ Does not include SAM (Segment Anything Model) analysis
    - ❌ Limited to sample/mock data
    
    ## 🚀 Full Mode Features
    
    When running in full mode, the application includes:
    - Advanced AI-powered forest segmentation
    - Real satellite imagery analysis
    - Interactive machine learning results
    - Detailed vegetation health classification
    
    ## 📊 Technology Stack
    
    - **Frontend**: Streamlit
    - **Data Analysis**: Pandas, NumPy
    - **Visualization**: Plotly, Folium
    - **Geospatial**: Rasterio, GeoPandas
    - **AI/ML**: PyTorch, Segment Anything Model (SAM)
    
    ## 🛠️ Troubleshooting
    
    If you're seeing this safe mode, it means there were compatibility issues with PyTorch.
    To resolve this, try:
    
    1. Use the custom launcher: `python run_app.py`
    2. Check PyTorch installation: `pip install torch torchvision`
    3. Restart Streamlit with file watcher disabled
    """)

if __name__ == "__main__":
    main() 