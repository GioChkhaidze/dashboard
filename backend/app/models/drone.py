"""
Drone data model for MongoDB storage
Stores drone specifications, health metrics, and flight history
"""
from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional, List


class FlightRecord(Document):
    """Individual flight record"""
    date: datetime
    duration: int  # minutes
    distance_covered: float  # km
    battery_used: int  # percentage
    images_captured: int
    status: str  # success, partial, failed
    field_id: str
    
    class Settings:
        name = "flight_records"


class DroneStatus(Document):
    """Drone specifications and current status"""
    drone_id: str = Field(default="drone_001")
    model: str = Field(default="DJI AGRAS T50")
    serial_number: str = Field(default="T50-2024-001")
    firmware_version: str = Field(default="v3.2.1")
    
    # Current Status
    battery_level: int = Field(default=85, ge=0, le=100)  # percentage
    operational_status: str = Field(default="standby")  # active, standby, offline
    health_status: str = Field(default="excellent")  # excellent, good, fair, poor
    gps_status: str = Field(default="excellent")
    
    # Health Metrics
    motor_health: int = Field(default=95, ge=0, le=100)
    propeller_health: int = Field(default=92, ge=0, le=100)
    signal_strength: int = Field(default=88, ge=0, le=100)
    
    # Flight Statistics
    total_flights: int = Field(default=0)
    total_flight_hours: float = Field(default=0.0)
    
    # Flight Scheduling
    auto_flight_enabled: bool = Field(default=True)  # Enable/disable automatic scheduled flights
    next_scheduled_flight: Optional[datetime] = None
    
    # Maintenance
    last_maintenance: Optional[datetime] = None
    next_service_due: Optional[datetime] = None
    service_due_days: Optional[int] = None
    
    # Camera Specifications
    camera: dict = Field(default_factory=lambda: {
        "model": "DJI Zenmuse P1",
        "resolution": "45MP Full-Frame",
        "sensor_type": "CMOS Full-Frame",
        "fov": "63.5° (35mm)",
        "lens_quality": "excellent",
        "image_quality": 99,
        "stabilization": "3-axis gimbal",
        "last_calibration": None
    })
    
    # Technical Specs
    specs: dict = Field(default_factory=lambda: {
        "weight": "47.5 kg (with full tank)",
        "max_speed": "10 m/s",
        "max_altitude": "30 m AGL",
        "max_flight_time": "18 min (full load)",
        "wind_resistance": "8 m/s",
        "temp_range": "-10°C to 45°C",
        "spray_width": "11 m",
        "tank_capacity": "40 L"
    })
    
    # Battery Specs
    battery: dict = Field(default_factory=lambda: {
        "type": "DB1560 Intelligent Battery",
        "capacity": "29,000 mAh",
        "voltage": "52.22 V",
        "charge_time": "10 min (80%)",
        "cycles": "247 / 1500",
        "health": "92%"
    })
    
    # Image URL (optional)
    image_url: Optional[str] = Field(default="/static/drone.png")
    
    # Timestamps
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "drone_status"
