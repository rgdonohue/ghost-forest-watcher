import ee

def initialize_gee(project=None):
    """Authenticate and initialize the Earth Engine API."""
    ee.Initialize(project=project)

def get_sentinel2_collection(aoi, start_date, end_date, cloud_pct=20):
    """Load and filter Sentinel-2 imagery for a given AOI and date range."""
    collection = (ee.ImageCollection('COPERNICUS/S2_SR')
                  .filterBounds(aoi)
                  .filterDate(start_date, end_date)
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_pct)))
    return collection

def apply_cloud_mask(image):
    """Apply cloud mask to a Sentinel-2 image."""
    cloud_mask = image.select('SCL').neq(3).And(image.select('SCL').neq(8))
    return image.updateMask(cloud_mask)

def compute_indices(image):
    """Compute NDVI, NBR, and NDWI for a Sentinel-2 image."""
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    nbr = image.normalizedDifference(['B8', 'B12']).rename('NBR')
    ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')
    return image.addBands([ndvi, nbr, ndwi])