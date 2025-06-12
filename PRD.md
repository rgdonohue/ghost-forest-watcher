# 📍 PRD: Ghost Forests Watcher — Western Colorado Edition

**Subtitle:** AI-Assisted Detection of Forest Die-Off in Response to Drought and Climate Stress

---

## 🧭 Overview

**Goal:** Build a demonstration project that uses Sentinel-2 imagery and foundation-model-assisted classification to detect areas of forest die-off in Western Colorado, with a focus on drought-stressed or beetle-impacted regions. This portfolio piece will showcase your ability to integrate remote sensing, environmental AI, and ethical geospatial storytelling.

**Why it Matters:** Western Colorado's forests—particularly Ponderosa pine, spruce-fir, and piñon-juniper ecosystems—are increasingly vulnerable to prolonged drought, bark beetle infestations, and wildfires. This project will make forest degradation visible using modern AI-enhanced workflows and culminate in a public-facing interactive map that blends scientific insight, ecological awareness, and climate justice.

---

## 🔧 Core Features

### 1. Imagery Ingestion + Preprocessing

* Source Sentinel-2 imagery from Google Earth Engine (GEE) and/or Microsoft Planetary Computer.
* Prioritize areas around the 2020 East Troublesome Fire or 2018 416 Fire scars to create high-contrast visual narratives.
* Apply GEE's built-in cloud masking; compute NDVI, NDWI, and NBR (Normalized Burn Ratio).
* Tile AOIs into \~1 km² segments to optimize model performance and resource use.
* Prepare to troubleshoot potential GEE authentication or API rate limit issues.

### 2. Foundation Model Integration

* Use Meta's Segment Anything Model (SAM) for tree canopy segmentation.
* Optionally integrate GroundingDINO for prompt-based detection (e.g., "dead forest," "sparse canopy").
* Run segmentation using 2–3 example prompts on selected AOIs.
* Provide fallback classification using NDVI/NBR thresholds.
* Consider using MobileSAM or lightweight variants to mitigate memory constraints.

### 3. Change Detection + Validation Module

* Conduct temporal analysis of NDVI and NBR from 2018–2024.
* Detect significant vegetation loss using threshold-based methods.
* Generate polygon shapefiles for high-confidence forest degradation zones.
* Perform visual validation with NAIP or Google Earth high-resolution imagery.

### 4. Cartographic Output

* Build an interactive web map using Streamlit for rapid deployment.
* Include layer toggles, before/after swipe comparison, and NDVI/NBR visualization tools.
* Enable export of GeoTIFFs or shapefiles for user download.

### 5. Narrative Panel

* Develop a side panel to communicate:

  * Ecological context: forest type distribution, drought records, and bark beetle data.
  * Technical summary of data sources, models used, and processing pipeline.
  * Ethical transparency: model provenance, known limitations, and uncertainty disclosures.
  * Climate justice framing: discuss the intersection of forest loss, water insecurity, and downstream impacts on Indigenous land management and rural communities.
  * Integrate demographic overlays to highlight vulnerable populations (e.g., tribal lands, underserved communities).

### 6. Provenance/Ethics Dashboard

* Build a provenance/ethics dashboard to track data and model sources, uncertainty, and citations.

### 7. User Feedback

* Integrate a user feedback form in the Streamlit app for error reporting and suggestions.

### 8. Accessibility and Mobile Optimization

* Ensure the Streamlit web map is accessible (color contrast, alt text, keyboard navigation) and mobile-optimized.

---

## 🛠️ Tech Stack

| Component         | Tool / Framework                                    |
| ----------------- | --------------------------------------------------- |
| Remote Sensing    | Sentinel-2 (via GEE), `rasterio`, `eo-learn`        |
| AI Models         | SAM (Meta), MobileSAM, GroundingDINO                |
| Geospatial Engine | Python, GeoPandas, DuckDB                           |
| Web Map           | Streamlit                                           |
| Hosting           | Streamlit Cloud                                     |
| Ethics Layer      | Provenance dashboard with uncertainty and citations |

---

## ✅ Success Criteria

* [ ] Working demo focused on Western Colorado AOI
* [ ] Clear segmentation layer of degraded forest areas
* [ ] NDVI/NBR-based temporal change detection
* [ ] Functional and mobile-accessible Streamlit map
* [ ] Deployed and publicly accessible via URL
* [ ] Accompanying README with full data and model citations
* [ ] Thoughtful narrative panel linking ecology, technology, and justice
* [ ] Basic validation using high-resolution imagery

---

## 📌 Definition of Done

A project is considered complete when:

* The Streamlit app loads without errors
* At least one AOI is processed and visualized with before/after comparison
* Segmentation masks are displayed clearly alongside NDVI/NBR layers
* Downloadable sample data (GeoTIFFs or shapefiles) is available
* A clear narrative panel communicates the methodology, ethics, and impacts
* The demo is hosted on Streamlit Cloud and accessible via a public link

---

## 🗓️ Timeline (Estimated: 9 Days)

| Day | Task                                                               |
| --- | ------------------------------------------------------------------ |
| 1   | Initialize repo, define AOI, acquire imagery + troubleshoot access |
| 2   | Preprocess NDVI/NBR, apply cloud masking                           |
| 3   | Begin SAM segmentation on a 1 km² tile                             |
| 4   | Finalize SAM integration; add NDVI fallback if needed              |
| 5   | Conduct temporal change detection                                  |
| 6   | Create shapefile output + validate with NAIP imagery               |
| 7   | Build interactive Streamlit web map                                |
| 8   | Write narrative panel and README documentation                     |
| 9   | Final QA, polish, deploy, and share                                |

---

## 🌱 Optional Extensions

* Fine-tune SAM with labeled Western Colorado imagery
* Add local environmental layers (e.g., fire history, precipitation anomaly maps)
* Introduce mindfulness layers such as Refuge Recovery forest walk guides
* Enable annotation tools for crowdsourced validation or citizen science input

---

> *"Let your maps not just reveal decline, but invite protection."*

This is your pathfinder, brosef. Ready to fire it up? 🔥
