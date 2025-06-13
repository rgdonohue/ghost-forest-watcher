# SAM Forest Die-off Analysis

This module uses the Segment Anything Model (SAM) to analyze forest die-off patterns in the East Troublesome area.

## What It Does

1. **Loads GeoTIFF Data**: Reads the NDVI difference data exported from Google Earth Engine
2. **Converts to RGB**: Transforms NDVI data into RGB images suitable for SAM processing
3. **Segments Vegetation**: Uses SAM to identify and segment vegetation areas
4. **Classifies Health**: Categorizes vegetation into health classes based on NDVI values:
   - **Healthy** (NDVI > 0.1): Thriving vegetation
   - **Stressed** (-0.1 to 0.1): Vegetation under stress
   - **Declining** (-0.3 to -0.1): Vegetation in decline
   - **Dead** (< -0.3): Dead or severely damaged vegetation

## Usage

### Quick Start
```bash
# Make sure you're in the project root and venv is activated
python src/sam_processor.py
```

### Advanced Usage
```python
from src.sam_processor import ForestSAMProcessor
from pathlib import Path

# Initialize processor
processor = ForestSAMProcessor(model_type="vit_b")
processor.load_model()

# Load and process data
data_path = Path("data/east_troublesome_small_tile.tif")
ndvi_data, metadata = processor.load_geotiff(data_path)
rgb_image = processor.ndvi_to_rgb(ndvi_data)

# Run segmentation
segmentation_results = processor.segment_forest_areas(rgb_image)

# Classify vegetation health
classification_results = processor.classify_vegetation_health(
    ndvi_data, segmentation_results
)

# Create visualization
processor.visualize_results(rgb_image, classification_results)
```

## Model Types
- `vit_b`: Base model (~375MB) - Good balance of speed and accuracy
- `vit_l`: Large model (~1.2GB) - Better accuracy, slower
- `vit_h`: Huge model (~2.6GB) - Best accuracy, slowest

## Output
The script generates:
- **Terminal output**: Statistics on vegetation health percentages
- **Visualization**: `outputs/forest_analysis_results.png` showing different vegetation health classes
- **Model files**: SAM models downloaded to `models/` directory

## Data Requirements
- Input: GeoTIFF file with NDVI difference data
- Format: Single or multi-band raster
- Expected values: NDVI difference (-1 to 1)
- Projection: Any (automatically handled)

## Performance Notes
- **First run**: Downloads SAM model (~375MB for vit_b)
- **Processing time**: ~2-5 minutes for 1km² tile
- **Memory usage**: ~2-4GB RAM
- **GPU acceleration**: Automatic on Apple Silicon (MPS) or CUDA GPUs 