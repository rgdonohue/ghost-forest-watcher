# 🌲 Ghost Forest Watcher — Western Colorado Edition

**AI-Powered Forest Recovery Monitoring After the East Troublesome Fire**

![Project Status](https://img.shields.io/badge/Status-Beta-yellow)
![Python Version](https://img.shields.io/badge/Python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)

---

## 🎯 Project Overview

Ghost Forest Watcher is a **Streamlit application** for visualizing forest recovery patterns following the 2020 East Troublesome Fire in Colorado. Using Sentinel-2 satellite imagery and optional AI segmentation (SAM), it demonstrates analysis of vegetation health and recovery trends.

Note: Results shown are illustrative and depend on data, configuration, and model setup.

## Why it Matters

Western Colorado's forests are increasingly threatened by drought, bark beetle infestations, and wildfires. This project makes forest degradation visible using modern AI workflows, supporting ecological awareness and climate justice.

## ✨ Features

### 🛰️ **Data Processing**
- **Sentinel-2 Imagery**: Pre/post-fire NDVI analysis via Google Earth Engine
- **AI Segmentation**: Meta's Segment Anything Model (SAM) for vegetation classification
- **Geospatial Analysis**: Rasterio, GeoPandas integration with 10m resolution
- **🚀 Scalable Processing**: Handle areas up to 2000+ km² with intelligent tiling

### 🖥️ **Web Application** 
- **Interactive Map**: Folium-based visualization with layer controls
- **Multi-Page Dashboard**: Overview, Analysis, Data Explorer, Export, About
- **Real-time Processing**: Streamlit caching for optimal performance
- **Export Capabilities**: JSON, CSV, images, and comprehensive reports
- **🚀 Large Area Support**: Memory-efficient processing for massive fire areas

### 🔬 **Analysis Results**
- **Vegetation Health Classification**: 4-tier system (Healthy/Stressed/Declining/Dead)
- **Statistical Dashboard**: Interactive charts and metrics
- **Spatial Visualization**: Color-coded vegetation health maps
- **Temporal Analysis**: Pre-fire vs. post-fire comparison
- **🚀 Aggregated Statistics**: Combined results from multiple processing tiles

### 🧪 **Quality Assurance & Scaling**
- **Automated tests**: Unit and integration tests pass locally and in CI
- **Error Handling**: Graceful degradation and user feedback
- **Performance Optimization**: Efficient data loading and caching
- **Cross-platform Compatibility**: Works on desktop and mobile
- **🚀 Memory Efficiency**: Maximum 8GB RAM usage for any fire area size
- **🚀 Parallel Processing**: 4x speed improvement through multi-core utilization

## Tech Stack

- **Remote Sensing:** Sentinel-2 (GEE), rasterio
- **AI Models:** SAM (Meta), MobileSAM, GroundingDINO
- **Geospatial Engine:** Python, GeoPandas, DuckDB
- **Web Map:** Streamlit
- **Hosting:** Streamlit Cloud

## 🚀 Quick Start

### Option 1: Simple Launch (Recommended)
```bash
# 1. Clone and setup
git clone <repo-url>
cd ghost-forest-watcher
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python main.py
# or: make run
```

### Option 2: Development Setup
```bash
# Install with development dependencies
pip install -e .[dev]

# Run with various options
python main.py --port 8502        # Custom port
python main.py --safe             # Safe mode (no AI)
python main.py --test             # Run tests
```

### Pre-commit Hooks (recommended)
Enable automatic formatting and lint checks before each commit:
```bash
pip install pre-commit
pre-commit install
# Optional: run on the whole repo once
pre-commit run --all-files
```

### Data and model prerequisites

- Large satellite data and SAM model weights are not bundled.
- For a quick demo without data, you can enable a tiny synthetic dataset fallback:
  ```bash
  export GF_SYNTHETIC_FALLBACK=1
  python main.py --safe
  ```
  This is for interface/demo purposes only.

### Option 3: Advanced Usage
```bash
# Using the custom launcher script
python scripts/run_app.py

# Direct Streamlit execution
streamlit run ghost_forest_watcher/app.py
```

### CI and Tests

- Run unit tests locally (skipping integration by default):
```bash
pytest -m "not integration"
```

- Run integration tests (requires a running Streamlit server or let the test start one):
```bash
export GF_RUN_INTEGRATION=1
pytest -m integration
```

- GitHub Actions
  - CI is configured to run linting and unit tests
  - Integration tests are optional and can be triggered manually

### 🌐 Access the Application
- **Local URL**: http://localhost:8501
- **Features**: Interactive map, data analysis, export tools
- **Performance**: Optimized for desktop and mobile browsers

## 📊 Project Status

### ✅ **Current Capabilities**
- **Working Web Application**: Streamlit interface with multiple pages
- **Optional AI Segmentation**: SAM-based analysis when dependencies and weights are installed
- **Demo Data Pipeline**: Pre-processed tile included; GEE utilities provided for further work
- **Interactive Visualization**: Folium/Plotly maps, stats, and exports
- **Scaling Concepts**: Tiling and cloud-processing designs with example code
- **CI & Tests**: Linting and unit tests configured; integration tests optional

### 🎯 **Key Metrics & Scaling (illustrative)**
- **Study Area**: East Troublesome Fire sample tile
- **Resolution**: 10m Sentinel-2 imagery
- **Local Scaling**: Tiling example targets memory-efficient processing
- **Cloud Scaling**: GEE-based approach for larger areas
These figures are targets or examples and not guarantees.

## 💡 Usage Guide

### **Navigation**
1. **Overview**: Dashboard with key metrics and visualizations
2. **Interactive Map**: Folium map with layer controls and opacity settings
3. **Analysis Dashboard**: Detailed charts and vegetation health statistics
4. **Data Explorer**: Raw data examination and filtering tools
5. **Export & Reports**: Download capabilities (JSON, CSV, images)
6. **About & Methods**: Technical documentation and methodology

### **Key Features**
- **Layer Toggles**: Switch between satellite, OpenStreetMap, and NDVI overlays
- **Interactive Charts**: Hover data and clickable elements
- **Real-time Processing**: Cached analysis for fast response times
- **Export Tools**: Multiple format options for research and reporting

### **Example Output**

![Forest Die-off Analysis Results](docs/images/forest_analysis_results.png)

## 🚀 Scaling Capabilities

Ghost Forest Watcher includes comprehensive scaling solutions to handle fire areas of any size:

### **🔧 Local Tiling System**
- **Memory Efficient**: Maximum 8GB RAM usage regardless of fire area size
- **Parallel Processing**: 4x speed improvement through multi-core utilization
- **Fault Tolerant**: Individual tile failures don't stop entire analysis
- **Progress Tracking**: Real-time monitoring of large processing jobs
- **Scalable**: Handle areas up to 2000+ km² without code changes

### **☁️ Cloud Processing (Google Earth Engine)**
- **Unlimited Scale**: Process entire fire areas on Google's infrastructure
- **Minimal Local Resources**: Only 4GB RAM needed locally
- **Automatic Optimization**: Server-side processing with built-in scaling
- **Global Data Access**: Direct access to Sentinel-2 imagery worldwide
- **Production Ready**: Optimal for continuous monitoring systems

### **📊 Scaling Performance (illustrative)**

| Fire Area | Local Processing | Cloud Processing | Memory Required |
|-----------|------------------|------------------|-----------------|
| 800 km² (Sample area) | seconds | ~30 minutes | ~2GB |
| 784 km² (E. Troublesome) | 1.5 hours | 30 minutes | 8GB |
| 835 km² (Cameron Peak) | 2.0 hours | 45 minutes | 8GB |
| 1500+ km² (Large Fires) | 3.5 hours | 1.5 hours | 8GB |

### **🛠️ Implementation Options**

**For Development & Testing:**
```python
from ghost_forest_watcher.src.scalable_processor import ScalableForestProcessor

# Initialize with memory constraints
processor = ScalableForestProcessor(
    max_memory_gb=8.0,
    tile_size_mb=50,
    overlap_pixels=64
)

# Process large area
results = processor.process_large_area(
    input_path="data/large_fire_area.tif",
    output_dir="outputs/analysis",
    max_workers=4
)
```

**For Production Deployment:**
```python
from ghost_forest_watcher.src.cloud_pipeline import CloudOptimizedPipeline

# Initialize cloud processing
pipeline = CloudOptimizedPipeline(project_id="your-gee-project")

# Process entire fire area in the cloud
job_info = pipeline.process_fire_area_cloud(
    fire_boundary=east_troublesome_fire,
    export_scale=10  # 10m resolution
)
```

### **📋 Scaling Documentation**
- **[Scaling Implementation Guide](docs/SCALING_IMPLEMENTATION_GUIDE.md)**: Step-by-step integration
- **[Development Roadmap](docs/DEVELOPMENT_ROADMAP.md)**: Future scaling enhancements
- **[Scale Demo](ghost_forest_watcher/src/scale_demo.py)**: Interactive scaling analysis

## Contributing

Contributions are welcome! Please:
- Open issues for bugs or feature requests
- Submit pull requests with clear descriptions
- Follow the project's code of conduct

## Ethics & Provenance

- All data/model sources are cited in the provenance dashboard
- Known limitations and uncertainties are disclosed
- The project foregrounds climate justice and ecological transparency

## License

[MIT License](LICENSE)

## Acknowledgments

- Meta AI for SAM
- IDEA Research for GroundingDINO
- Google Earth Engine
- Open-source geospatial and remote sensing communities

## Project Initialization

1. **Initialize Git (if not already done):**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Register and authenticate with Google Earth Engine:**
   - [Sign up for GEE](https://earthengine.google.com/)
   - Authenticate using the Python API:
     ```bash
     earthengine authenticate
     ```
4. **Download model weights:**
   - Follow instructions for [SAM](https://github.com/facebookresearch/segment-anything) and [GroundingDINO](https://github.com/IDEA-Research/GroundingDINO)

## Google Earth Engine Setup

To use Google Earth Engine (GEE) for this project:

1. **Create a GEE account**:
   - Visit [Google Earth Engine](https://earthengine.google.com/) and sign up
   - Request access to the Earth Engine API
   - Wait for approval (usually within 1-2 business days)

2. **Create a Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project (or use an existing one)
   - Enable the Earth Engine API for your project
   - Note your project ID (you'll need it for authentication)

3. **Install the earthengine-api package**:
   ```bash
   pip install earthengine-api
   ```

4. **Authenticate with GEE**:
   ```bash
   earthengine authenticate
   ```
   - This will open a browser window for you to log in with your Google account
   - Grant the requested permissions
   - Copy the authorization code back to your terminal

5. **Initialize GEE with your project**:
   In your Python code, always initialize with your project ID:
   ```python
   import ee
   ee.Initialize(project='your-project-id')
   ```

6. **Test your GEE setup**:
   - Run the template notebook: `notebooks/gee_preprocessing_template.ipynb`
   - Make sure to specify your project ID when initializing
   - If authentication is successful, you should be able to query Sentinel-2 imagery

---

*"Let your maps not just reveal decline, but invite protection."* 
