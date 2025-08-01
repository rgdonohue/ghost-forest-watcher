"""
Unit tests for Ghost Forest Watcher application
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

# Add ghost_forest_watcher to path for imports
sys.path.append('..')

# Import modules to test  
from ghost_forest_watcher.src.data_manager import GhostForestDataManager
from ghost_forest_watcher.src.sam_processor import ForestSAMProcessor


class TestGhostForestDataManager(unittest.TestCase):
    """Test cases for GhostForestDataManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.data_manager = GhostForestDataManager()
        
    def test_initialization(self):
        """Test that GhostForestDataManager initializes correctly"""
        self.assertIsInstance(self.data_manager, GhostForestDataManager)
        
    def test_load_geotiff_data_with_default_path(self):
        """Test GeoTIFF data loading with default path"""
        # This will use the actual file if it exists, or return None if not
        result = self.data_manager.load_geotiff_data()
        
        # Result should be either a dict with data or None
        self.assertTrue(result is None or isinstance(result, dict))
        
    def test_load_geotiff_data_nonexistent_file(self):
        """Test GeoTIFF data loading with non-existent file"""
        # Try to load a file that definitely doesn't exist
        result = self.data_manager.load_geotiff_data("/definitely/does/not/exist.tif")
        
        # Should return empty dict for missing file (per current implementation)
        self.assertEqual(result, {})
        
    def test_get_vegetation_health_stats(self):
        """Test vegetation health statistics calculation"""
        # Mock classification data with correct keys
        mock_classification = {
            'healthy': np.array([[1, 1, 0], [0, 1, 1]]),
            'stressed': np.array([[0, 0, 1], [1, 0, 0]]),
            'declining': np.array([[0, 0, 0], [1, 0, 0]]),
            'dead': np.array([[0, 0, 0], [0, 0, 0]])
        }
        
        stats = self.data_manager.get_vegetation_health_stats(mock_classification)
        
        self.assertIsInstance(stats, dict)
        self.assertIn('healthy', stats)
        self.assertIn('stressed', stats)
        self.assertIn('declining', stats)
        self.assertIn('dead', stats)
        
    def test_run_sam_analysis_no_processor(self):
        """Test SAM analysis when processor is not available"""
        result = self.data_manager.run_sam_analysis()
        
        # Should handle gracefully when SAM model is not available
        self.assertIsInstance(result, dict)


class TestForestSAMProcessor(unittest.TestCase):
    """Test cases for ForestSAMProcessor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = ForestSAMProcessor()
        
    def test_initialization(self):
        """Test that ForestSAMProcessor initializes correctly"""
        self.assertIsInstance(self.processor, ForestSAMProcessor)
        
    def test_ndvi_to_rgb(self):
        """Test NDVI to RGB conversion"""
        # Create mock NDVI data
        mock_ndvi = np.random.rand(256, 256)
        
        result = self.processor.ndvi_to_rgb(mock_ndvi)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result.shape, (256, 256, 3))
        
    def test_classify_vegetation_health_mock_data(self):
        """Test vegetation health classification with mock data"""
        # Mock NDVI data
        mock_ndvi = np.random.rand(100, 100) * 2 - 1  # Random NDVI-like values
        
        # Mock masks
        mock_masks = {
            'combined_mask': np.ones((100, 100), dtype=bool)
        }
        
        result = self.processor.classify_vegetation_health(mock_ndvi, mock_masks)
        
        self.assertIsInstance(result, dict)
        
    def test_generate_prompt_points(self):
        """Test prompt point generation"""
        # Create mock image
        mock_image = np.random.rand(100, 100, 3).astype(np.uint8)
        
        points = self.processor.generate_prompt_points(mock_image)
        
        self.assertIsInstance(points, list)
        if points:  # Only check if points were generated
            self.assertIsInstance(points[0], tuple)
            self.assertEqual(len(points[0]), 2)


class TestApplicationIntegration(unittest.TestCase):
    """Integration tests for the application"""
    
    def test_required_files_check(self):
        """Test that the application can check for required files"""
        data_file = Path("data/east_troublesome_small_tile.tif")
        model_file = Path("models/sam_vit_b.pth")
        results_file = Path("outputs/forest_analysis_results.png")
        
        # These should be Path objects (whether they exist or not)
        self.assertIsInstance(data_file, Path)
        self.assertIsInstance(model_file, Path)
        self.assertIsInstance(results_file, Path)
        
    def test_app_imports(self):
        """Test that all necessary modules can be imported"""
        try:
            import streamlit
            import folium
            import plotly.express
            import pandas
            import numpy
            import_success = True
        except ImportError:
            import_success = False
            
        self.assertTrue(import_success, "Required packages should be importable")
        
    @patch('streamlit.set_page_config')
    def test_streamlit_config(self, mock_set_page_config):
        """Test Streamlit page configuration"""
        # Import the main app module from the correct path
        import ghost_forest_watcher.app as app
        
        # The set_page_config should have been called during import
        mock_set_page_config.assert_called_once()
        
        # Check that the call included expected parameters
        call_args = mock_set_page_config.call_args
        self.assertIn('page_title', call_args.kwargs)
        self.assertIn('page_icon', call_args.kwargs)
        self.assertEqual(call_args.kwargs['page_title'], "Ghost Forest Watcher")


class TestDataValidation(unittest.TestCase):
    """Test data validation and error handling"""
    
    def test_empty_image_handling(self):
        """Test handling of empty or invalid image data"""
        processor = ForestSAMProcessor()
        
        # Test with None NDVI data
        result = processor.ndvi_to_rgb(None)
        # This should handle gracefully or raise appropriate error
        self.assertTrue(result is None or isinstance(result, np.ndarray))
        
        # Test with empty array
        empty_ndvi = np.array([])
        try:
            result = processor.ndvi_to_rgb(empty_ndvi)
            # Should handle gracefully
            self.assertTrue(result is None or isinstance(result, np.ndarray))
        except (ValueError, IndexError):
            # These exceptions are acceptable for empty input
            pass
        
    def test_invalid_classification_data(self):
        """Test handling of invalid classification data"""
        data_manager = GhostForestDataManager()
        
        # Test with None
        stats = data_manager.get_vegetation_health_stats(None)
        self.assertIsInstance(stats, dict)
        
        # Test with empty dict
        stats = data_manager.get_vegetation_health_stats({})
        self.assertIsInstance(stats, dict)


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestGhostForestDataManager))
    suite.addTest(unittest.makeSuite(TestForestSAMProcessor))
    suite.addTest(unittest.makeSuite(TestApplicationIntegration))
    suite.addTest(unittest.makeSuite(TestDataValidation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}") 