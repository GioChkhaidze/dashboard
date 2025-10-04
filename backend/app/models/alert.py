"""
Alert Model
Stores critical alerts for pest density and canopy issues
"""
from datetime import datetime
from typing import Dict, Any
from beanie import Document
from pydantic import Field


class Alert(Document):
    """
    Field alerts for critical conditions
    
    Collection: alerts
    """
    field_id: str = Field(..., description="Field identifier")
    date: str = Field(..., description="Alert date")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Alert timestamp")
    
    alert_type: str = Field(..., description="Type of alert (high_pest_density, low_canopy, etc.)")
    severity: str = Field(..., description="Severity level: info, warning, critical")
    zone_id: str = Field(..., description="Affected zone identifier")
    
    metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Relevant metrics (numeric and string values)"
    )
    
    message: str = Field(..., description="Human-readable alert message")
    recommendation: str = Field(..., description="Recommended action")
    
    status: str = Field(default="active", description="Alert status: active, acknowledged, resolved")
    acknowledged: bool = Field(default=False, description="Whether alert has been acknowledged")
    acknowledged_at: datetime | None = Field(default=None, description="Acknowledgement timestamp")
    
    class Settings:
        name = "alerts"
        indexes = [
            "field_id",
            "date",
            "status",
            [("field_id", 1), ("status", 1), ("date", -1)],
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "field_id": "field_001",
                "date": "2025-10-03",
                "timestamp": "2025-10-03T07:15:00Z",
                "alert_type": "high_pest_density",
                "severity": "critical",
                "zone_id": "grid_3_5",
                "metrics": {
                    "pest_density": 12.3,
                    "canopy_cover": 48.2
                },
                "message": "Critical pest density detected in Zone 3-5. Immediate action recommended.",
                "recommendation": "Consider targeted pesticide application in this zone.",
                "status": "active",
                "acknowledged": False
            }
        }
