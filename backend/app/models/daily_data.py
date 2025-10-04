"""
Daily Data Model
Stores daily drone flight data including pest detections and canopy coverage
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from beanie import Document
from pydantic import Field


class FieldDimensions(Dict):
    """Field dimensions"""
    width_m: float
    height_m: float
    grid_resolution: float


class CriticalZone(Dict):
    """Critical zone information"""
    zone_id: str
    pest_density: float
    canopy_cover: float
    risk_level: str


class Aggregates(Dict):
    """Aggregated statistics"""
    pest_count: int
    pest_counts_by_crop: Dict[str, int]  # per-crop totals
    avg_canopy: float
    min_canopy: float
    max_canopy: float
    critical_zones: List[CriticalZone]


class Heatmaps(Dict):
    """Heatmap data"""
    pest_density_by_crop: Dict[str, List[List[float]]]  # per-crop heatmaps
    canopy_grid: List[List[float]]


class WeatherMetadata(Dict):
    """Weather information"""
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    conditions: Optional[str] = None


class Metadata(Dict):
    """Flight metadata"""
    drone_flight_id: str
    weather: Optional[WeatherMetadata] = None


class DailyData(Document):
    """
    Daily data from drone flights
    
    Collection: daily_data
    """
    field_id: str = Field(..., description="Field identifier")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Flight timestamp")
    
    # Raw AI model outputs
    pest_grid: List[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="2D grid of pest data per cell: [{count: int, crop_type: str}, ...]"
    )
    canopy_cover: List[List[float]] = Field(
        default_factory=list,
        description="2D array of canopy cover percentages"
    )
    
    # Field information
    field_dimensions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Field dimensions and grid resolution"
    )
    
    # Computed aggregates
    aggregates: Dict[str, Any] = Field(
        default_factory=dict,
        description="Aggregated statistics"
    )
    
    # Processed heatmaps
    heatmaps: Dict[str, Any] = Field(
        default_factory=dict,
        description="Pest density and canopy heatmap grids"
    )
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional flight metadata"
    )
    
    class Settings:
        name = "daily_data"
        indexes = [
            "field_id",
            "date",
            [("field_id", 1), ("date", -1)],
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "field_id": "field_001",
                "date": "2025-10-03",
                "timestamp": "2025-10-03T07:00:00Z",
                "bounding_boxes": [[125, 340, 50, 50], [680, 120, 45, 48]],
                "canopy_cover": [[72.5, 68.3, 75.1], [70.2, 65.8, 71.5]],
                "field_dimensions": {
                    "width_m": 50,
                    "height_m": 50,
                    "grid_resolution": 1.0
                },
                "aggregates": {
                    "pest_count": 342,
                    "avg_canopy": 72.4,
                    "min_canopy": 45.2,
                    "max_canopy": 95.6
                }
            }
        }
