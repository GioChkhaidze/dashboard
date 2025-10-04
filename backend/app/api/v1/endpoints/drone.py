"""
Drone status and flight history endpoints
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, ValidationError
from app.models.drone import DroneStatus, FlightRecord

router = APIRouter()


@router.get("/status")
async def get_drone_status(drone_id: str = "drone_001"):
    """
    Get current drone status, specifications, and recent flight history
    
    Returns:
        - Drone specifications
        - Current battery, health metrics
        - Camera and sensor details
        - Recent flight history (last 10 flights)
    """
    try:
        # Get drone status
        drone = await DroneStatus.find_one(DroneStatus.drone_id == drone_id)
        
        if not drone:
            # Create default drone status if not found
            now = datetime.utcnow()
            drone = DroneStatus(
                drone_id=drone_id,
                last_maintenance=now - timedelta(days=60),  # Last maintenance 60 days ago
                next_service_due=now + timedelta(days=30)   # Next service in 30 days
            )
            await drone.insert()
        
        # Get recent flight history
        flights = await FlightRecord.find(
            FlightRecord.field_id == "field_001"
        ).sort(-FlightRecord.date).limit(10).to_list()
        
        # Calculate total flight statistics from all flight records
        all_flights = await FlightRecord.find(
            FlightRecord.field_id == "field_001"
        ).to_list()
        
        # Update drone statistics with accurate calculations
        drone.total_flights = len(all_flights)
        drone.total_flight_hours = round(sum(f.duration for f in all_flights) / 60, 1) if all_flights else 0.0
        
        # Calculate service due days
        if drone.next_service_due:
            days_until_service = (drone.next_service_due - datetime.utcnow()).days
            drone.service_due_days = max(0, days_until_service)
        
        return {
            "drone": drone.dict(),
            "flight_history": [flight.dict() for flight in flights]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching drone status: {str(e)}")


@router.get("/flights")
async def get_flight_history(
    drone_id: str = "drone_001",
    limit: int = 30,
    field_id: Optional[str] = None
):
    """
    Get detailed flight history
    
    Args:
        drone_id: Drone identifier
        limit: Maximum number of flights to return
        field_id: Optional field filter
    """
    try:
        query = {}
        if field_id:
            query["field_id"] = field_id
            
        flights = await FlightRecord.find(query).sort(
            -FlightRecord.date
        ).limit(limit).to_list()
        
        # Calculate summary statistics
        total_distance = sum(f.distance_covered for f in flights)
        total_duration = sum(f.duration for f in flights)
        total_images = sum(f.images_captured for f in flights)
        success_rate = (
            sum(1 for f in flights if f.status == "success") / len(flights) * 100
            if flights else 0
        )
        
        return {
            "flights": [flight.dict() for flight in flights],
            "summary": {
                "total_flights": len(flights),
                "total_distance_km": round(total_distance, 2),
                "total_flight_hours": round(total_duration / 60, 2),
                "total_images": total_images,
                "success_rate": round(success_rate, 1)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching flight history: {str(e)}")


@router.post("/update-status")
class DroneStatusUpdate(BaseModel):
    battery_level: Optional[int] = None
    operational_status: Optional[str] = None
    health_status: Optional[str] = None


async def update_drone_status(
    drone_id: str,
    payload: DroneStatusUpdate = Body(...)
):
    """
    Update drone status (typically called after flight or maintenance)
    
    Args:
        drone_id: Drone identifier
        battery_level: Current battery percentage
        operational_status: active, standby, offline
        health_status: excellent, good, fair, poor
    """
    try:
        drone = await DroneStatus.find_one(DroneStatus.drone_id == drone_id)
        
        if not drone:
            raise HTTPException(status_code=404, detail="Drone not found")
        
        # Update fields if provided
        if payload.battery_level is not None:
            drone.battery_level = payload.battery_level
        if payload.operational_status:
            drone.operational_status = payload.operational_status
        if payload.health_status:
            drone.health_status = payload.health_status
            
        drone.last_updated = datetime.utcnow()
        await drone.save()
        
        return {
            "status": "success",
            "message": "Drone status updated",
            "drone": drone.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating drone status: {str(e)}")


@router.post("/toggle-auto-flight")
async def toggle_auto_flight(
    drone_id: str = "drone_001",
    enabled: bool = Body(..., embed=True)
):
    """
    Toggle automatic flight scheduling on/off
    
    Args:
        drone_id: Drone identifier
        enabled: True to enable automatic flights, False to disable
    """
    try:
        drone = await DroneStatus.find_one(DroneStatus.drone_id == drone_id)
        
        if not drone:
            # Create default drone if not found
            drone = DroneStatus(drone_id=drone_id)
            await drone.insert()
        
        # Update auto flight status
        drone.auto_flight_enabled = enabled
        drone.last_updated = datetime.utcnow()
        
        # Clear next scheduled flight if disabling
        if not enabled:
            drone.next_scheduled_flight = None
        else:
            # Set next scheduled flight to tomorrow if enabling
            from datetime import timedelta
            drone.next_scheduled_flight = datetime.utcnow() + timedelta(days=1)
        
        await drone.save()
        
        return {
            "status": "success",
            "message": f"Automatic flights {'enabled' if enabled else 'disabled'}",
            "auto_flight_enabled": drone.auto_flight_enabled,
            "next_scheduled_flight": drone.next_scheduled_flight.isoformat() if drone.next_scheduled_flight else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling auto flight: {str(e)}")


@router.post("/upgrade-to-t50")
async def upgrade_to_t50(drone_id: str = "drone_001"):
    """
    Upgrade existing drone record to DJI AGRAS T50 specifications
    This is a one-time migration endpoint to update the drone model and specs
    If drone doesn't exist, it will be created with T50 specs
    """
    try:
        drone = await DroneStatus.find_one(DroneStatus.drone_id == drone_id)
        
        if not drone:
            # Create new drone with T50 specs
            drone = DroneStatus(drone_id=drone_id)
        
        # Update to DJI AGRAS T50 specs
        drone.model = "DJI AGRAS T50"
        drone.serial_number = "T50-2024-001"
        drone.firmware_version = "v3.2.1"
        
        # Update camera to DJI Zenmuse P1
        drone.camera = {
            "model": "DJI Zenmuse P1",
            "resolution": "45MP Full-Frame",
            "sensor_type": "CMOS Full-Frame",
            "fov": "63.5° (35mm)",
            "lens_quality": "excellent",
            "image_quality": 99,
            "stabilization": "3-axis gimbal",
            "last_calibration": None
        }
        
        # Update technical specs
        drone.specs = {
            "weight": "47.5 kg (with full tank)",
            "max_speed": "10 m/s",
            "max_altitude": "30 m AGL",
            "max_flight_time": "18 min (full load)",
            "wind_resistance": "8 m/s",
            "temp_range": "-10°C to 45°C",
            "spray_width": "11 m",
            "tank_capacity": "40 L"
        }
        
        # Update battery specs
        drone.battery = {
            "type": "DB1560 Intelligent Battery",
            "capacity": "29,000 mAh",
            "voltage": "52.22 V",
            "charge_time": "10 min (80%)",
            "cycles": "247 / 1500",
            "health": "92%"
        }
        
        # Set image URL
        drone.image_url = "/static/drone.png"
        
        # Set maintenance dates if not already set
        now = datetime.utcnow()
        if not drone.last_maintenance:
            drone.last_maintenance = now - timedelta(days=60)  # Last maintenance 60 days ago
        if not drone.next_service_due:
            drone.next_service_due = now + timedelta(days=30)  # Next service in 30 days
        
        drone.last_updated = now
        await drone.save()
        
        return {
            "status": "success",
            "message": "Drone upgraded to DJI AGRAS T50 successfully",
            "drone": drone.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error upgrading drone: {str(e)}")


class FlightCreate(BaseModel):
    date: datetime
    duration: int
    distance_covered: float
    battery_used: int
    images_captured: int
    status: str = "success"
    field_id: str = "field_001"


@router.post("/log-flight")
async def log_flight(flight: FlightCreate = Body(...)):
    """
    Log a completed flight
    
    Args:
        flight: Flight data including date, duration, distance, battery, images, status, field_id
    """
    try:
        # Create flight record from request model
        flight_doc = FlightRecord(
            date=flight.date,
            duration=flight.duration,
            distance_covered=flight.distance_covered,
            battery_used=flight.battery_used,
            images_captured=flight.images_captured,
            status=flight.status,
            field_id=flight.field_id,
        )
        await flight_doc.insert()
        
        # Update drone statistics
        drone = await DroneStatus.find_one(DroneStatus.drone_id == "drone_001")
        if drone:
            drone.total_flights += 1
            drone.total_flight_hours += flight.duration / 60
            await drone.save()
        
        return {
            "status": "success",
            "message": "Flight logged successfully",
            "flight_id": str(flight_doc.id)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging flight: {str(e)}")
