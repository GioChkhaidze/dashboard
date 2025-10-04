"""
Monthly Aggregate Model
Stores monthly aggregated statistics
"""
from typing import List, Dict, Any
from beanie import Document
from pydantic import Field


class MonthlyAggregate(Document):
    """
    Monthly aggregated statistics
    
    Collection: monthly_aggregates
    """
    field_id: str = Field(..., description="Field identifier")
    month: str = Field(..., description="Month in YYYY-MM format")
    
    total_pests: int = Field(0, description="Total pests detected in month")
    avg_canopy: float = Field(0.0, description="Average canopy coverage for month")
    
    peak_pest_date: str = Field(None, description="Date with highest pest count")
    lowest_canopy_date: str = Field(None, description="Date with lowest canopy")
    
    weekly_breakdown: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Weekly statistics within month"
    )
    
    trend_vs_last_month: Dict[str, float] = Field(
        default_factory=dict,
        description="Comparison to previous month"
    )
    
    class Settings:
        name = "monthly_aggregates"
        indexes = [
            "field_id",
            [("field_id", 1), ("month", -1)],
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "field_id": "field_001",
                "month": "2025-10",
                "total_pests": 9850,
                "avg_canopy": 73.1,
                "peak_pest_date": "2025-10-15",
                "lowest_canopy_date": "2025-10-03",
                "trend_vs_last_month": {
                    "pest_change_pct": -8.3,
                    "canopy_change_pct": 5.7
                }
            }
        }
