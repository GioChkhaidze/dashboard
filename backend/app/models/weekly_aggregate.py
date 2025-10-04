"""
Weekly Aggregate Model
Stores weekly aggregated statistics
"""
from typing import List, Dict, Any
from beanie import Document
from pydantic import Field


class WeeklyAggregate(Document):
    """
    Weekly aggregated statistics
    
    Collection: weekly_aggregates
    """
    field_id: str = Field(..., description="Field identifier")
    week_start: str = Field(..., description="Week start date (Monday)")
    week_end: str = Field(..., description="Week end date (Sunday)")
    
    daily_stats: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Daily statistics for the week"
    )
    
    weekly_summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Weekly summary statistics"
    )
    
    class Settings:
        name = "weekly_aggregates"
        indexes = [
            "field_id",
            [("field_id", 1), ("week_start", -1)],
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "field_id": "field_001",
                "week_start": "2025-09-29",
                "week_end": "2025-10-05",
                "daily_stats": [
                    {
                        "date": "2025-09-29",
                        "pest_count": 320,
                        "avg_canopy": 71.2
                    }
                ],
                "weekly_summary": {
                    "total_pests": 2340,
                    "avg_pest_per_day": 334,
                    "avg_canopy": 72.4,
                    "canopy_trend": "improving",
                    "pest_trend": "increasing"
                }
            }
        }
