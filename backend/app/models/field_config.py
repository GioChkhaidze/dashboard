"""
Field Configuration Model
Stores field metadata and configuration settings
"""
from typing import List, Dict, Any, Optional
from beanie import Document
from pydantic import Field


class FieldConfig(Document):
    """
    Field configuration and metadata
    
    Collection: field_config
    """
    field_id: str = Field(..., description="Unique field identifier")
    name: str = Field(..., description="Field name")
    
    location: Dict[str, Any] = Field(
        default_factory=dict,
        description="Geographic location"
    )
    
    dimensions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Field dimensions"
    )
    
    grid_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Grid configuration"
    )
    
    thresholds: Dict[str, float] = Field(
        default_factory=dict,
        description="Alert thresholds"
    )
    
    crop_types: Optional[List[str]] = Field(default_factory=list, description="Types of crops grown in field (e.g., ['wheat', 'corn'])")
    planting_date: Optional[str] = Field(None, description="Planting date")
    expected_harvest: Optional[str] = Field(None, description="Expected harvest date")
    
    class Settings:
        name = "field_config"
        indexes = ["field_id"]
    
    class Config:
        json_schema_extra = {
            "example": {
                "field_id": "field_001",
                "name": "North Field",
                "location": {
                    "coordinates": [34.0522, -118.2437],
                    "address": "Farm Location"
                },
                "dimensions": {
                    "width_m": 50,
                    "height_m": 50,
                    "area_hectares": 0.8
                },
                "grid_config": {
                    "cell_size_m": 1.0,
                    "grid_width": 50,
                    "grid_height": 50
                },
                "thresholds": {
                    "pest_density_warning": 5.0,
                    "pest_density_critical": 10.0,
                    "canopy_warning": 60.0,
                    "canopy_critical": 50.0
                },
                "crop_type": "corn",
                "planting_date": "2025-04-15",
                "expected_harvest": "2025-11-01"
            }
        }
