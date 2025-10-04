"""
Canopy Processing Utilities
Process canopy cover 2D arrays and calculate statistics
"""
import numpy as np
from typing import List, Dict, Tuple


def calculate_canopy_statistics(
    canopy_grid: List[List[float]]
) -> dict:
    """
    Calculate statistical measures for canopy coverage
    
    Args:
        canopy_grid: 2D array of canopy percentages
    
    Returns:
        Dictionary with avg, min, max, std_dev
    
    Example:
        >>> canopy = [[72.5, 68.3, 75.1], [70.2, 65.8, 71.5]]
        >>> stats = calculate_canopy_statistics(canopy)
        >>> print(stats['avg'])
        70.57
    """
    canopy_array = np.array(canopy_grid)
    
    return {
        "avg": round(float(np.mean(canopy_array)), 2),
        "min": round(float(np.min(canopy_array)), 2),
        "max": round(float(np.max(canopy_array)), 2),
        "std_dev": round(float(np.std(canopy_array)), 2),
        "median": round(float(np.median(canopy_array)), 2)
    }


def find_low_coverage_zones(
    canopy_grid: np.ndarray,
    warning_threshold: float = 60.0,
    critical_threshold: float = 50.0
) -> List[dict]:
    """
    Find zones with low canopy coverage
    
    Args:
        canopy_grid: 2D array of canopy percentages
        warning_threshold: Threshold for warning level
        critical_threshold: Threshold for critical level
    
    Returns:
        List of low coverage zones with status
    """
    low_zones = []
    height, width = canopy_grid.shape
    
    for y in range(height):
        for x in range(width):
            coverage = canopy_grid[y, x]
            
            if coverage < critical_threshold:
                status = "critical"
            elif coverage < warning_threshold:
                status = "warning"
            else:
                continue
            
            low_zones.append({
                "zone_id": f"grid_{x}_{y}",
                "position": {"x": x, "y": y},
                "coverage": round(float(coverage), 2),
                "status": status
            })
    
    # Sort by coverage (ascending - worst first)
    low_zones.sort(key=lambda z: z["coverage"])
    
    return low_zones


def calculate_coverage_distribution(
    canopy_grid: np.ndarray
) -> dict:
    """
    Calculate distribution of canopy coverage across ranges
    
    Args:
        canopy_grid: 2D array of canopy percentages
    
    Returns:
        Dictionary with coverage distribution by ranges
    """
    canopy_flat = canopy_grid.flatten()
    
    ranges = {
        "critical": (0, 50),      # 0-50%
        "low": (50, 60),          # 50-60%
        "moderate": (60, 70),     # 60-70%
        "good": (70, 80),         # 70-80%
        "excellent": (80, 100)    # 80-100%
    }
    
    distribution = {}
    total_cells = len(canopy_flat)
    
    for category, (min_val, max_val) in ranges.items():
        count = np.sum((canopy_flat >= min_val) & (canopy_flat < max_val))
        percentage = (count / total_cells) * 100
        distribution[category] = {
            "count": int(count),
            "percentage": round(percentage, 2)
        }
    
    return distribution


def identify_coverage_trends(
    historical_grids: List[np.ndarray]
) -> dict:
    """
    Identify trends in canopy coverage over time
    
    Args:
        historical_grids: List of canopy grids ordered by time
    
    Returns:
        Dictionary with trend analysis
    """
    if len(historical_grids) < 2:
        return {"trend": "insufficient_data"}
    
    # Calculate average coverage for each time point
    averages = [np.mean(grid) for grid in historical_grids]
    
    # Calculate overall trend
    first_avg = averages[0]
    last_avg = averages[-1]
    change = last_avg - first_avg
    change_pct = (change / first_avg) * 100 if first_avg > 0 else 0
    
    # Determine trend direction
    if change_pct > 5:
        trend = "improving"
    elif change_pct < -5:
        trend = "declining"
    else:
        trend = "stable"
    
    return {
        "trend": trend,
        "change": round(change, 2),
        "change_pct": round(change_pct, 2),
        "first_avg": round(first_avg, 2),
        "last_avg": round(last_avg, 2),
        "data_points": len(historical_grids)
    }


def generate_canopy_heatmap_colors(
    canopy_grid: np.ndarray
) -> List[List[str]]:
    """
    Generate color codes for canopy heatmap visualization
    
    Args:
        canopy_grid: 2D array of canopy percentages
    
    Returns:
        2D array of hex color codes
    """
    def get_color(value: float) -> str:
        """Map canopy percentage to color (red=low, green=high)"""
        if value < 20:
            return "#7f1d1d"  # Critical low
        elif value < 40:
            return "#dc2626"  # Very low
        elif value < 60:
            return "#f59e0b"  # Low
        elif value < 80:
            return "#84cc16"  # Good
        else:
            return "#22c55e"  # Excellent
    
    height, width = canopy_grid.shape
    colors = []
    
    for y in range(height):
        row = []
        for x in range(width):
            color = get_color(canopy_grid[y, x])
            row.append(color)
        colors.append(row)
    
    return colors


def calculate_field_health_score(
    canopy_grid: np.ndarray,
    pest_heatmap: np.ndarray = None
) -> dict:
    """
    Calculate overall field health score (0-100)
    
    Args:
        canopy_grid: 2D array of canopy percentages
        pest_heatmap: Optional pest density heatmap
    
    Returns:
        Dictionary with health score and breakdown
    """
    # Canopy component (60% weight)
    avg_canopy = np.mean(canopy_grid)
    canopy_score = (avg_canopy / 100) * 60
    
    # Pest component (40% weight) - if provided
    pest_score = 40.0
    if pest_heatmap is not None:
        avg_pest_density = np.mean(pest_heatmap)
        # Lower pest density = higher score
        # Assuming >20 pests/m² is worst case
        pest_normalized = max(0, min(1, 1 - (avg_pest_density / 20)))
        pest_score = pest_normalized * 40
    
    total_score = canopy_score + pest_score
    
    # Determine rating
    if total_score >= 80:
        rating = "excellent"
    elif total_score >= 60:
        rating = "good"
    elif total_score >= 40:
        rating = "fair"
    else:
        rating = "poor"
    
    return {
        "health_score": round(total_score, 1),
        "rating": rating,
        "components": {
            "canopy_score": round(canopy_score, 1),
            "pest_score": round(pest_score, 1)
        }
    }


def compare_zones(
    canopy_grid: np.ndarray,
    zone1_coords: Tuple[int, int],
    zone2_coords: Tuple[int, int]
) -> dict:
    """
    Compare two zones
    
    Args:
        canopy_grid: 2D array of canopy percentages
        zone1_coords: (x, y) coordinates of zone 1
        zone2_coords: (x, y) coordinates of zone 2
    
    Returns:
        Comparison dictionary
    """
    x1, y1 = zone1_coords
    x2, y2 = zone2_coords
    
    canopy1 = float(canopy_grid[y1, x1])
    canopy2 = float(canopy_grid[y2, x2])
    
    difference = canopy2 - canopy1
    difference_pct = (difference / canopy1) * 100 if canopy1 > 0 else 0
    
    return {
        "zone1": {
            "zone_id": f"grid_{x1}_{y1}",
            "canopy_cover": round(canopy1, 2)
        },
        "zone2": {
            "zone_id": f"grid_{x2}_{y2}",
            "canopy_cover": round(canopy2, 2)
        },
        "difference": round(difference, 2),
        "difference_pct": round(difference_pct, 2),
        "better_zone": "zone2" if canopy2 > canopy1 else "zone1"
    }
