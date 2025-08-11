"""
SAM (Segment Anything Model) Processing for Forest Die-off Detection
"""
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from pathlib import Path
import cv2
from PIL import Image
import torch
from typing import Tuple, List, Optional
import logging

try:
    from segment_anything import sam_model_registry, SamPredictor
    SAM_AVAILABLE = True
except ImportError:
    print("Warning: segment_anything not available. Install with: pip install segment-anything")
    SAM_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ForestSAMProcessor:
    """
    SAM-based processor for forest die-off detection and segmentation
    """
    
    def __init__(self, model_type: str = "vit_b", device: str = "auto"):
        """
        Initialize the SAM processor
        
        Args:
            model_type: SAM model type ('vit_b', 'vit_l', 'vit_h')
            device: Device to run on ('cuda', 'cpu', or 'auto')
        """
        self.model_type = model_type
        self.device = self._get_device(device)
        self.sam = None
        self.predictor = None
        self.sam_available = SAM_AVAILABLE

        # Model checkpoint URLs
        self.model_urls = {
            "vit_b": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth",
            "vit_l": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth", 
            "vit_h": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth"
        }
        
    def _get_device(self, device: str) -> str:
        """Determine the best device to use"""
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif torch.backends.mps.is_available():
                return "mps"  # Apple Silicon GPU
            else:
                return "cpu"
        return device
    
    def download_model(self, models_dir: Path = Path("models")) -> Path:
        """
        Download SAM model checkpoint if not already present
        
        Args:
            models_dir: Directory to store model checkpoints
            
        Returns:
            Path to the model checkpoint
        """
        if not self.sam_available:
            raise ImportError(
                "segment_anything is not installed. Install extras: pip install '.[sam]' or install segment-anything."
            )

        models_dir.mkdir(exist_ok=True)
        checkpoint_path = models_dir / f"sam_{self.model_type}.pth"
        
        if not checkpoint_path.exists():
            # Try to download, but provide a clear fallback instruction if it fails (e.g., no network)
            try:
                import requests
                url = self.model_urls[self.model_type]
                logger.info(f"Downloading SAM {self.model_type} model...")
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status()
                with open(checkpoint_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                logger.info(f"Model downloaded to {checkpoint_path}")
            except Exception as e:
                raise RuntimeError(
                    "Could not download SAM checkpoint. Place the weights at 'models/" 
                    f"sam_{self.model_type}.pth' or install with extras. Error: {e}"
                )
        
        return checkpoint_path
    
    def load_model(self, checkpoint_path: Optional[Path] = None):
        """
        Load the SAM model
        
        Args:
            checkpoint_path: Path to model checkpoint. If None, will download automatically.
        """
        if not self.sam_available:
            raise ImportError(
                "segment_anything not available. Install extras '.[sam]' and ensure weights are present."
            )

        if checkpoint_path is None:
            # Prefer local file if present, otherwise attempt download
            local_ckpt = Path("models") / f"sam_{self.model_type}.pth"
            checkpoint_path = local_ckpt if local_ckpt.exists() else self.download_model()

        logger.info(f"Loading SAM model on {self.device}")
        self.sam = sam_model_registry[self.model_type](checkpoint=str(checkpoint_path))
        self.sam.to(device=self.device)
        self.predictor = SamPredictor(self.sam)
        
    def load_geotiff(self, tiff_path: Path) -> Tuple[np.ndarray, dict]:
        """
        Load GeoTIFF file and extract relevant information
        
        Args:
            tiff_path: Path to the GeoTIFF file
            
        Returns:
            Tuple of (image_array, metadata)
        """
        with rasterio.open(tiff_path) as src:
            # Read the data
            data = src.read()
            
            # Store metadata
            metadata = {
                'crs': src.crs,
                'transform': src.transform,
                'bounds': src.bounds,
                'shape': data.shape,
                'dtype': data.dtype,
                'nodata': src.nodata
            }
            
            logger.info(f"Loaded GeoTIFF: {data.shape} {data.dtype}")
            logger.info(f"Bounds: {metadata['bounds']}")
            
        return data, metadata
    
    def ndvi_to_rgb(self, ndvi_data: np.ndarray, 
                    normalize: bool = True,
                    colormap: str = 'RdYlGn') -> np.ndarray:
        """
        Convert NDVI data to RGB for SAM processing
        
        Args:
            ndvi_data: NDVI array (can be difference data)
            normalize: Whether to normalize the data
            colormap: Matplotlib colormap to use
            
        Returns:
            RGB image array (H, W, 3) with values 0-255
        """
        # Handle None or empty input
        if ndvi_data is None or ndvi_data.size == 0:
            logger.warning("Empty or None NDVI data provided")
            return None
            
        # Handle single band or multi-band data
        if ndvi_data.ndim == 3:
            # Take first band if multi-band
            ndvi_2d = ndvi_data[0]
        else:
            ndvi_2d = ndvi_data
            
        # Remove nodata values (replace with median)
        if hasattr(ndvi_2d, 'mask'):
            ndvi_2d = np.ma.filled(ndvi_2d, np.ma.median(ndvi_2d))
        
        # Handle inf and nan values
        ndvi_2d = np.nan_to_num(ndvi_2d, nan=0.0, posinf=1.0, neginf=-1.0)
        
        if normalize:
            # Normalize to 0-1 range
            vmin, vmax = np.percentile(ndvi_2d, [2, 98])  # Robust normalization
            ndvi_normalized = np.clip((ndvi_2d - vmin) / (vmax - vmin), 0, 1)
        else:
            ndvi_normalized = np.clip(ndvi_2d, 0, 1)
        
        # Apply colormap
        cmap = plt.get_cmap(colormap)
        rgb_float = cmap(ndvi_normalized)[:, :, :3]  # Remove alpha channel
        
        # Convert to 8-bit RGB
        rgb_uint8 = (rgb_float * 255).astype(np.uint8)
        
        return rgb_uint8
    
    def generate_prompt_points(self, image: np.ndarray, 
                              strategy: str = "grid",
                              grid_size: int = 5) -> List[Tuple[int, int]]:
        """
        Generate prompt points for SAM segmentation
        
        Args:
            image: Input image
            strategy: Point generation strategy ('grid', 'edges', 'adaptive')
            grid_size: Grid size for grid strategy
            
        Returns:
            List of (x, y) coordinate tuples
        """
        h, w = image.shape[:2]
        points = []
        
        if strategy == "grid":
            # Regular grid of points
            x_points = np.linspace(w//6, 5*w//6, grid_size)
            y_points = np.linspace(h//6, 5*h//6, grid_size)
            
            for x in x_points:
                for y in y_points:
                    points.append((int(x), int(y)))
                    
        elif strategy == "edges":
            # Points based on edge detection
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            edge_points = np.where(edges > 0)
            
            # Sample subset of edge points
            if len(edge_points[0]) > 0:
                indices = np.random.choice(len(edge_points[0]), 
                                         min(25, len(edge_points[0])), 
                                         replace=False)
                for i in indices:
                    points.append((edge_points[1][i], edge_points[0][i]))
        
        return points
    
    def segment_forest_areas(self, image: np.ndarray, 
                           prompt_points: Optional[List[Tuple[int, int]]] = None) -> dict:
        """
        Segment forest areas using SAM
        
        Args:
            image: RGB image array
            prompt_points: List of prompt points. If None, will generate automatically.
            
        Returns:
            Dictionary containing masks and metadata
        """
        if self.predictor is None:
            raise ValueError("Model not loaded. Call load_model() first.")
            
        logger.info("Setting image for SAM predictor...")
        self.predictor.set_image(image)
        
        if prompt_points is None:
            prompt_points = self.generate_prompt_points(image)
            
        logger.info(f"Generating segments from {len(prompt_points)} prompt points...")
        
        all_masks = []
        all_scores = []
        
        for point in prompt_points:
            input_point = np.array([point])
            input_label = np.array([1])  # Positive prompt
            
            masks, scores, logits = self.predictor.predict(
                point_coords=input_point,
                point_labels=input_label,
                multimask_output=True,
            )
            
            # Take the best mask
            best_mask_idx = np.argmax(scores)
            all_masks.append(masks[best_mask_idx])
            all_scores.append(scores[best_mask_idx])
        
        return {
            'masks': all_masks,
            'scores': all_scores,
            'prompt_points': prompt_points,
            'combined_mask': self._combine_masks(all_masks)
        }
    
    def _combine_masks(self, masks: List[np.ndarray]) -> np.ndarray:
        """Combine multiple masks into a single mask"""
        if not masks:
            return np.array([])
            
        combined = np.zeros_like(masks[0], dtype=bool)
        for mask in masks:
            combined = combined | mask
            
        return combined
    
    def classify_vegetation_health(self, ndvi_data: np.ndarray, 
                                 masks: dict) -> dict:
        """
        Classify vegetation health based on NDVI values and SAM masks
        
        Args:
            ndvi_data: Original NDVI difference data
            masks: SAM segmentation results
            
        Returns:
            Dictionary with classification results
        """
        # Handle single band data
        if ndvi_data.ndim == 3:
            ndvi_2d = ndvi_data[0]
        else:
            ndvi_2d = ndvi_data
            
        combined_mask = masks['combined_mask']
        
        # Define thresholds for vegetation health
        # Negative values indicate vegetation loss/stress
        healthy_threshold = 0.1
        stressed_threshold = -0.1
        dead_threshold = -0.3
        
        # Create classification masks
        vegetation_areas = combined_mask
        healthy_veg = vegetation_areas & (ndvi_2d > healthy_threshold)
        stressed_veg = vegetation_areas & (ndvi_2d <= healthy_threshold) & (ndvi_2d > stressed_threshold)
        declining_veg = vegetation_areas & (ndvi_2d <= stressed_threshold) & (ndvi_2d > dead_threshold)
        dead_veg = vegetation_areas & (ndvi_2d <= dead_threshold)
        
        # Calculate statistics
        total_veg_pixels = np.sum(vegetation_areas)
        
        results = {
            'masks': {
                'vegetation': vegetation_areas,
                'healthy': healthy_veg,
                'stressed': stressed_veg,
                'declining': declining_veg,
                'dead': dead_veg
            },
            'statistics': {
                'total_vegetation_pixels': int(total_veg_pixels),
                'healthy_pixels': int(np.sum(healthy_veg)),
                'stressed_pixels': int(np.sum(stressed_veg)),
                'declining_pixels': int(np.sum(declining_veg)),
                'dead_pixels': int(np.sum(dead_veg)),
                'healthy_percent': float(np.sum(healthy_veg) / max(total_veg_pixels, 1) * 100),
                'stressed_percent': float(np.sum(stressed_veg) / max(total_veg_pixels, 1) * 100),
                'declining_percent': float(np.sum(declining_veg) / max(total_veg_pixels, 1) * 100),
                'dead_percent': float(np.sum(dead_veg) / max(total_veg_pixels, 1) * 100)
            }
        }
        
        return results
    
    def visualize_results(self, original_image: np.ndarray,
                         classification_results: dict,
                         save_path: Optional[Path] = None) -> plt.Figure:
        """
        Create visualization of segmentation and classification results
        
        Args:
            original_image: Original RGB image
            classification_results: Results from classify_vegetation_health
            save_path: Optional path to save the visualization
            
        Returns:
            Matplotlib figure
        """
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle('Forest Die-off Analysis Results', fontsize=16)
        
        # Original image
        axes[0, 0].imshow(original_image)
        axes[0, 0].set_title('Original NDVI Data')
        axes[0, 0].axis('off')
        
        # All vegetation
        axes[0, 1].imshow(original_image)
        axes[0, 1].imshow(classification_results['masks']['vegetation'], 
                          alpha=0.5, cmap='Greens')
        axes[0, 1].set_title('Detected Vegetation Areas')
        axes[0, 1].axis('off')
        
        # Healthy vegetation
        axes[0, 2].imshow(original_image)
        axes[0, 2].imshow(classification_results['masks']['healthy'], 
                          alpha=0.7, cmap='Greens')
        axes[0, 2].set_title('Healthy Vegetation')
        axes[0, 2].axis('off')
        
        # Stressed vegetation
        axes[1, 0].imshow(original_image)
        axes[1, 0].imshow(classification_results['masks']['stressed'], 
                          alpha=0.7, cmap='Oranges')
        axes[1, 0].set_title('Stressed Vegetation')
        axes[1, 0].axis('off')
        
        # Declining vegetation
        axes[1, 1].imshow(original_image)
        axes[1, 1].imshow(classification_results['masks']['declining'], 
                          alpha=0.7, cmap='Reds')
        axes[1, 1].set_title('Declining Vegetation')
        axes[1, 1].axis('off')
        
        # Dead vegetation
        axes[1, 2].imshow(original_image)
        axes[1, 2].imshow(classification_results['masks']['dead'], 
                          alpha=0.7, cmap='gray_r')
        axes[1, 2].set_title('Dead Vegetation')
        axes[1, 2].axis('off')
        
        # Add statistics text
        stats = classification_results['statistics']
        stats_text = f"""
        Vegetation Health Statistics:
        Healthy: {stats['healthy_percent']:.1f}%
        Stressed: {stats['stressed_percent']:.1f}%
        Declining: {stats['declining_percent']:.1f}%
        Dead: {stats['dead_percent']:.1f}%
        """
        
        plt.figtext(0.02, 0.02, stats_text, fontsize=10, 
                   bbox=dict(boxstyle="round", facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Visualization saved to {save_path}")
            
        return fig

def main():
    """Example usage of the ForestSAMProcessor"""
    
    # Initialize processor
    processor = ForestSAMProcessor(model_type="vit_b")
    
    # Load model (will download if needed)
    processor.load_model()
    
    # Load the GeoTIFF data
    data_path = Path("data/east_troublesome_small_tile.tif")
    ndvi_data, metadata = processor.load_geotiff(data_path)
    
    # Convert to RGB for SAM processing
    rgb_image = processor.ndvi_to_rgb(ndvi_data)
    
    # Segment forest areas
    segmentation_results = processor.segment_forest_areas(rgb_image)
    
    # Classify vegetation health
    classification_results = processor.classify_vegetation_health(
        ndvi_data, segmentation_results
    )
    
    # Print results
    stats = classification_results['statistics']
    print(f"\n=== Forest Die-off Analysis Results ===")
    print(f"Total vegetation pixels: {stats['total_vegetation_pixels']:,}")
    print(f"Healthy vegetation: {stats['healthy_percent']:.1f}%")
    print(f"Stressed vegetation: {stats['stressed_percent']:.1f}%")
    print(f"Declining vegetation: {stats['declining_percent']:.1f}%")
    print(f"Dead vegetation: {stats['dead_percent']:.1f}%")
    
    # Create visualization
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    fig = processor.visualize_results(
        rgb_image, 
        classification_results,
        save_path=output_dir / "forest_analysis_results.png"
    )
    
    plt.show()

if __name__ == "__main__":
    main() 
