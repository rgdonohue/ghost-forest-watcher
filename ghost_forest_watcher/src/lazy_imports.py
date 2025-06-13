"""
Lazy import system to prevent PyTorch-Streamlit conflicts
This module delays the import of PyTorch-related modules until they're actually needed
"""
import importlib
import logging

logger = logging.getLogger(__name__)

class LazyImporter:
    """Lazy importer that loads modules only when accessed"""
    
    def __init__(self, module_name, class_name=None):
        self.module_name = module_name
        self.class_name = class_name
        self._module = None
        self._class = None
        
    def _load_module(self):
        """Load the module if not already loaded"""
        if self._module is None:
            try:
                self._module = importlib.import_module(self.module_name)
                logger.info(f"Lazy loaded module: {self.module_name}")
            except Exception as e:
                logger.error(f"Failed to lazy load {self.module_name}: {e}")
                self._module = False  # Mark as failed
        return self._module if self._module is not False else None
    
    def _load_class(self):
        """Load the class if not already loaded"""
        if self._class is None and self.class_name:
            module = self._load_module()
            if module:
                try:
                    self._class = getattr(module, self.class_name)
                    logger.info(f"Lazy loaded class: {self.class_name}")
                except AttributeError as e:
                    logger.error(f"Class {self.class_name} not found in {self.module_name}: {e}")
                    self._class = False
        return self._class if self._class is not False else None
    
    def __call__(self, *args, **kwargs):
        """Allow the importer to be called like a class constructor"""
        cls = self._load_class()
        if cls:
            return cls(*args, **kwargs)
        else:
            raise ImportError(f"Could not load {self.class_name} from {self.module_name}")
    
    def __getattr__(self, name):
        """Proxy attribute access to the loaded module"""
        module = self._load_module()
        if module:
            return getattr(module, name)
        else:
            raise AttributeError(f"Module {self.module_name} not available")

# Create lazy importers for problematic modules
LazyForestSAMProcessor = LazyImporter('sam_processor', 'ForestSAMProcessor')
LazyTorch = LazyImporter('torch')

def safe_import_sam_processor():
    """Safely import ForestSAMProcessor with fallback"""
    try:
        return LazyForestSAMProcessor()
    except Exception as e:
        logger.warning(f"SAM processor not available: {e}")
        
        # Return a mock class that handles all methods gracefully
        class MockSAMProcessor:
            def __init__(self, *args, **kwargs):
                logger.warning("Using mock SAM processor - no actual processing will occur")
                
            def __getattr__(self, name):
                def mock_method(*args, **kwargs):
                    logger.warning(f"Mock SAM method called: {name}")
                    return None
                return mock_method
        
        return MockSAMProcessor()

def is_torch_available():
    """Check if PyTorch is available without importing it"""
    try:
        LazyTorch._load_module()
        return LazyTorch._module is not None
    except:
        return False 