"""
gee_utils.py

Utility functions for defining AOIs and other GEE-related helpers.
"""

import ee

def get_416_fire_aoi():
    """
    Get the AOI for the 416 Fire (2018) near Durango, Colorado.
    Returns:
        ee.Geometry: Geometry object representing the AOI
    """
    # Approximate bounding box for the 416 Fire area
    return ee.Geometry.Rectangle([-107.9, 37.5, -107.5, 37.7])


def get_east_troublesome_fire_aoi():
    """
    Get the AOI for the East Troublesome Fire (2020) in Grand County, Colorado.
    Returns:
        ee.Geometry: Geometry object representing the AOI
    """
    # Approximate bounding box for the East Troublesome Fire area
    return ee.Geometry.Rectangle([-106.0, 40.0, -105.6, 40.4])


def get_pre_post_dates(fire_name):
    """
    Get pre and post fire dates for a specific fire.
    
    Args:
        fire_name: str, '416_fire' or 'east_troublesome'
        
    Returns:
        dict: Dictionary with pre_start, pre_end, post_start, post_end dates
    """
    if fire_name == '416_fire':
        # 416 Fire started on June 1, 2018
        return {
            'pre_start': '2018-05-01',
            'pre_end': '2018-05-31',
            'post_start': '2018-07-01',
            'post_end': '2018-07-31'
        }
    elif fire_name == 'east_troublesome':
        # East Troublesome Fire started on October 14, 2020
        return {
            'pre_start': '2020-09-01',
            'pre_end': '2020-10-13',
            'post_start': '2020-11-01',
            'post_end': '2020-11-30'
        }
    else:
        raise ValueError(f"Unknown fire name: {fire_name}")


def visualize_ndvi(image):
    """
    Get visualization parameters for NDVI.
    
    Args:
        image: ee.Image with NDVI band
        
    Returns:
        dict: Visualization parameters for NDVI
    """
    return {
        'min': 0.0,
        'max': 0.8,
        'bands': ['NDVI'],
        'palette': ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', 
                   '99B718', '74A901', '66A000', '529400', '3E8601', 
                   '207401', '056201', '004C00', '023B01', '012E01', 
                   '011D01', '011301']
    } 