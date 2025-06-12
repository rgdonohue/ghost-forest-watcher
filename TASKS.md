# ✅ Project Task List: Ghost Forests Watcher (Western Colorado Edition)

## 1. 🗺️ Project Initialization
- [ ] Create GitHub repo and project board
- [ ] Define project goals in README
- [ ] Choose AOI: 416 Fire or East Troublesome Fire
- [ ] Register Google Earth Engine (GEE) account + enable Python API
- [ ] Set up local dev environment (Python, virtualenv/conda, Streamlit)

## 2. 🌐 Imagery Acquisition + Preprocessing
- [ ] Load Sentinel-2 data via GEE for selected AOI
  - [ ] Choose dates pre- and post-fire (e.g., 2018 vs. 2024)
  - [ ] Apply GEE cloud masking
- [ ] Compute spectral indices
  - [ ] NDVI
  - [ ] NBR
  - [ ] NDWI
- [ ] Tile AOI into ~1 km² chunks and export image patches
- [ ] Troubleshoot GEE access and export permissions if needed

## 3. 🤖 Model Integration: SAM + GroundingDINO
- [ ] Set up Segment Anything (SAM) environment
  - [ ] Download SAM weights or MobileSAM version
  - [ ] Test on small tile
- [ ] Run segmentation on tiled image patches
  - [ ] Segment live canopy vs. dead forest vs. barren ground
- [ ] Optional: Integrate GroundingDINO for prompt-based inference
  - [ ] Test with prompts like "burned tree," "dead forest"
- [ ] Save mask outputs for visualization and downstream analysis
- [ ] Implement NDVI/NBR fallback classification if SAM fails

## 4. 🔄 Change Detection & Validation
- [ ] Compare NDVI/NBR values from multiple years
  - [ ] Calculate per-pixel or zonal change metrics
- [ ] Threshold areas with significant canopy loss
- [ ] Convert change-detection results to polygons
- [ ] Overlay SAM masks to cross-check spatial agreement
- [ ] Validate selected polygons using:
  - [ ] NAIP imagery in GEE
  - [ ] Google Earth (manual inspection)
  - [ ] Create annotated screenshots for documentation

## 5. 🗺️ Web Mapping via Streamlit
- [ ] Initialize Streamlit app and map component
- [ ] Display pre-/post- imagery layers
  - [ ] Implement before/after swipe slider
- [ ] Add overlay toggles:
  - [ ] NDVI
  - [ ] NBR
  - [ ] SAM masks
  - [ ]

## 6. 📊 Provenance/Ethics Dashboard
- [ ] Implement provenance/ethics dashboard for data and model transparency

## 7. 📝 User Feedback
- [ ] Integrate user feedback form in Streamlit app

## 8. 📦 Export Formats
- [ ] Enable export of both raster (GeoTIFF) and vector (shapefile/GeoJSON) formats

## 9. 📋 Annotation Tools
- [ ] Integrate annotation tools for crowdsourced validation or citizen science input

## 10. 📱 Mobile Testing
- [ ] Conduct accessibility review and improvements (color contrast, alt text, keyboard navigation)
- [ ] Test and optimize Streamlit app for mobile devices
