# 🌲 Ghost Forests Watcher — Western Colorado Edition

**AI-Assisted Detection of Forest Die-Off in Response to Drought and Climate Stress**

---

## Overview

Ghost Forests Watcher is a demonstration project that leverages Sentinel-2 satellite imagery and state-of-the-art AI models to detect and visualize areas of forest die-off in Western Colorado. The project integrates remote sensing, environmental AI, and ethical geospatial storytelling, culminating in a public-facing interactive map.

## Why it Matters

Western Colorado's forests are increasingly threatened by drought, bark beetle infestations, and wildfires. This project makes forest degradation visible using modern AI workflows, supporting ecological awareness and climate justice.

## Core Features

- **Imagery Ingestion & Preprocessing:**
  - Sentinel-2 data via Google Earth Engine (GEE)
  - Cloud masking, NDVI, NDWI, and NBR computation
  - AOI tiling for efficient processing
- **AI Model Integration:**
  - Segment Anything Model (SAM) for canopy segmentation
  - Optional: GroundingDINO for prompt-based detection
  - NDVI/NBR fallback classification
- **Change Detection & Validation:**
  - Temporal NDVI/NBR analysis (2018–2024)
  - Polygon generation for degraded zones
  - Visual validation with NAIP/Google Earth
- **Web Mapping (Streamlit):**
  - Interactive map with before/after swipe, layer toggles
  - Export GeoTIFFs and shapefiles/GeoJSON
  - Provenance/ethics dashboard
  - User feedback form
  - Accessibility and mobile optimization
- **Narrative Panel:**
  - Ecological context, technical summary, ethics, and climate justice framing
  - Demographic overlays (e.g., tribal lands, underserved communities)
- **Crowdsourced Validation:**
  - Annotation tools for citizen science input

## Tech Stack

- **Remote Sensing:** Sentinel-2 (GEE), rasterio, eo-learn
- **AI Models:** SAM (Meta), MobileSAM, GroundingDINO
- **Geospatial Engine:** Python, GeoPandas, DuckDB
- **Web Map:** Streamlit
- **Hosting:** Streamlit Cloud

## Quickstart

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd ghost-forest-watcher
   ```
2. **Set up the environment:**
   - Create a virtual environment (conda or venv recommended)
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
3. **Register for Google Earth Engine:**
   - [Sign up for GEE](https://earthengine.google.com/)
   - Authenticate using the Python API
4. **Download model weights:**
   - Follow instructions for [SAM](https://github.com/facebookresearch/segment-anything) and [GroundingDINO](https://github.com/IDEA-Research/GroundingDINO)
5. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

## Usage

- Select an Area of Interest (AOI) in Western Colorado
- Choose pre- and post-fire dates for analysis
- View segmentation and change detection layers
- Toggle overlays (NDVI, NBR, SAM masks, demographic layers)
- Export results as GeoTIFF or shapefile/GeoJSON
- Submit feedback or annotate for crowdsourced validation

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

---

*"Let your maps not just reveal decline, but invite protection."* 