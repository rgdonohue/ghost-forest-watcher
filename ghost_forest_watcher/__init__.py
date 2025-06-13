"""
Ghost Forest Watcher - AI-Powered Forest Recovery Monitoring

A production-ready web application for monitoring forest recovery patterns 
following the 2020 East Troublesome Fire in Colorado using Sentinel-2 
satellite imagery and Meta's Segment Anything Model (SAM).

Version: 3.0
Author: Ghost Forest Watcher Team
License: MIT
"""

__version__ = "3.0.0"
__author__ = "Ghost Forest Watcher Team"
__email__ = "contact@ghostforestwatcher.com"
__description__ = "AI-Powered Forest Recovery Monitoring System"

# Import main application components
try:
    from .src.data_manager import GhostForestDataManager
    from .src.sam_processor import ForestSAMProcessor
    from .src.streamlit_pages import (
        show_map_page, 
        show_analysis_page, 
        show_explorer_page,
        show_export_page, 
        show_about_page
    )
except ImportError:
    # Handle case where dependencies aren't installed
    pass

__all__ = [
    'GhostForestDataManager',
    'ForestSAMProcessor',
    'show_map_page',
    'show_analysis_page', 
    'show_explorer_page',
    'show_export_page',
    'show_about_page'
] 