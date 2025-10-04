"""
Heatmap Generation Utilities
Converts bounding boxes to pest density heatmap grids
"""
import numpy as np
from typing import List, Tuple


def bounding_boxes_to_heatmap(
    bounding_boxes: List[List[float]],
    field_width: float,
    field_height: float,
    grid_size: float = 1.0
) -> List[List[float]]:
    """
    Convert bounding box coordinates to pest density heatmap with radial influence
    
    Args:
        bounding_boxes: List of [x, y, w, h] coordinates
        field_width: Field width in meters
        field_height: Field height in meters
        grid_size: Grid cell size in meters (default: 1.0m)
    
    Returns:
        2D array of pest density values (with smooth gradients)
    
    Example:
        >>> boxes = [[125, 340, 50, 50], [680, 120, 45, 48]]
        >>> heatmap = bounding_boxes_to_heatmap(boxes, 1000, 800, 1.0)
        >>> print(heatmap[340][125])  # Pest density at position
        1.0
    """
    # Calculate grid dimensions
    grid_width = int(np.ceil(field_width / grid_size))
    grid_height = int(np.ceil(field_height / grid_size))
    
    # Initialize heatmap grid with float values for smooth gradients
    heatmap = np.zeros((grid_height, grid_width), dtype=float)
    
    # Process each bounding box with radial influence
    for bbox in bounding_boxes:
        if len(bbox) != 4:
            continue
            
        x, y, w, h = bbox
        
        # Calculate bounding box coverage in grid cells
        start_col = int(x / grid_size)
        end_col = min(int(np.ceil((x + w) / grid_size)), grid_width)
        start_row = int(y / grid_size)
        end_row = min(int(np.ceil((y + h) / grid_size)), grid_height)
        
        # Calculate center for radial gradient
        center_col = (start_col + end_col) / 2
        center_row = (start_row + end_row) / 2
        max_dist = np.sqrt((end_col - start_col)**2 + (end_row - start_row)**2) / 2
        
        # Add influence with radial gradient (extends beyond bounding box for smooth effect)
        influence_radius = 2  # cells beyond the bounding box
        for row in range(max(0, start_row - influence_radius), 
                        min(grid_height, end_row + influence_radius)):
            for col in range(max(0, start_col - influence_radius), 
                            min(grid_width, end_col + influence_radius)):
                # Calculate distance from center
                distance = np.sqrt((col - center_col)**2 + (row - center_row)**2)
                # Calculate influence (1.0 at center, fading to 0 at edges)
                influence = max(0, 1 - (distance / (max_dist + 3)))
                heatmap[row, col] += influence
    
    return heatmap.tolist()


def calculate_pest_density(
    heatmap: np.ndarray,
    grid_size: float = 1.0
) -> np.ndarray:
    """
    Calculate pest density (pests per square meter) from heatmap
    
    Args:
        heatmap: 2D array of pest counts
        grid_size: Grid cell size in meters
    
    Returns:
        2D array of pest density values
    """
    cell_area = grid_size * grid_size
    return heatmap / cell_area


def find_hotspots(
    heatmap: np.ndarray,
    threshold: float = 5.0,
    grid_size: float = 1.0
) -> List[dict]:
    """
    Find pest density hotspots above threshold
    
    Args:
        heatmap: 2D array of pest counts
        threshold: Minimum pest count to be considered hotspot
        grid_size: Grid cell size in meters
    
    Returns:
        List of hotspot dictionaries with zone_id, pest_count, density
    """
    hotspots = []
    height, width = heatmap.shape
    
    for y in range(height):
        for x in range(width):
            pest_count = heatmap[y, x]
            if pest_count >= threshold:
                density = pest_count / (grid_size * grid_size)
                hotspots.append({
                    "zone_id": f"grid_{x}_{y}",
                    "position": {"x": x, "y": y},
                    "pest_count": int(pest_count),
                    "density": round(float(density), 2)
                })
    
    # Sort by density (descending)
    hotspots.sort(key=lambda h: h["density"], reverse=True)
    
    return hotspots


def normalize_heatmap(
    heatmap: np.ndarray,
    max_value: float = None
) -> np.ndarray:
    """
    Normalize heatmap values to 0-1 range for visualization
    
    Args:
        heatmap: 2D array to normalize
        max_value: Optional max value for normalization (uses array max if None)
    
    Returns:
        Normalized 2D array
    """
    if max_value is None:
        max_value = heatmap.max()
    
    if max_value == 0:
        return heatmap
    
    return heatmap / max_value


def smooth_heatmap(
    heatmap: np.ndarray,
    kernel_size: int = 3
) -> np.ndarray:
    """
    Apply Gaussian smoothing to heatmap
    
    Args:
        heatmap: 2D array to smooth
        kernel_size: Size of smoothing kernel (default: 3)
    
    Returns:
        Smoothed 2D array
    """
    from scipy.ndimage import gaussian_filter
    
    sigma = kernel_size / 6.0
    return gaussian_filter(heatmap, sigma=sigma)


def get_zone_metrics(
    pest_heatmap: np.ndarray,
    canopy_grid: np.ndarray,
    x: int,
    y: int,
    grid_size: float = 1.0
) -> dict:
    """
    Get metrics for a specific zone
    
    Args:
        pest_heatmap: Pest density heatmap
        canopy_grid: Canopy coverage grid
        x: Grid X coordinate
        y: Grid Y coordinate
        grid_size: Grid cell size
    
    Returns:
        Dictionary with zone metrics
    """
    height, width = pest_heatmap.shape
    
    if not (0 <= x < width and 0 <= y < height):
        return None
    
    pest_count = int(pest_heatmap[y, x])
    pest_density = pest_count / (grid_size * grid_size)
    canopy_cover = float(canopy_grid[y, x]) if canopy_grid is not None else 0.0
    
    # Determine risk level
    risk_level = "low"
    if pest_density > 10 or canopy_cover < 50:
        risk_level = "critical"
    elif pest_density > 5 or canopy_cover < 60:
        risk_level = "warning"
    
    return {
        "zone_id": f"grid_{x}_{y}",
        "position": {"x": x, "y": y},
        "pest_count": pest_count,
        "pest_density": round(pest_density, 2),
        "canopy_cover": round(canopy_cover, 2),
        "risk_level": risk_level
    }


def calculate_correlation(
    pest_heatmap: np.ndarray,
    canopy_grid: np.ndarray
) -> dict:
    """
    Calculate correlation between pest density and canopy coverage
    
    Args:
        pest_heatmap: Pest density heatmap
        canopy_grid: Canopy coverage grid
    
    Returns:
        Dictionary with correlation metrics
    """
    # Flatten arrays
    pest_flat = pest_heatmap.flatten()
    canopy_flat = canopy_grid.flatten()
    
    # Calculate correlation coefficient
    correlation = np.corrcoef(pest_flat, canopy_flat)[0, 1]
    
    # Find zones with high pest & low canopy (critical)
    critical_zones = []
    height, width = pest_heatmap.shape
    
    for y in range(height):
        for x in range(width):
            pest_density = pest_heatmap[y, x]
            canopy = canopy_grid[y, x]
            
            if pest_density > 10 and canopy < 50:
                critical_zones.append({
                    "zone_id": f"grid_{x}_{y}",
                    "pest_density": float(pest_density),
                    "canopy_cover": float(canopy)
                })
    
    return {
        "correlation_coefficient": round(float(correlation), 3),
        "interpretation": "negative" if correlation < -0.3 else "neutral" if correlation < 0.3 else "positive",
        "critical_zones_count": len(critical_zones),
        "critical_zones": critical_zones[:10]  # Top 10
    }
