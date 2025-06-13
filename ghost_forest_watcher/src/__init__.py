"""
Ghost Forest Watcher - Core Modules

This package contains the core functionality for the Ghost Forest Watcher
application including data management, AI processing, and UI components.
"""

from .data_manager import GhostForestDataManager
from .sam_processor import ForestSAMProcessor

__all__ = [
    'GhostForestDataManager',
    'ForestSAMProcessor'
] 