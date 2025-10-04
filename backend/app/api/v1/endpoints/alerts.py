"""
Alerts Endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from app.models.alert import Alert
from datetime import datetime

router = APIRouter()

@router.get("/active")
async def get_active_alerts(field_id: str = Query(...)):
    """Get all active alerts"""
    alerts = await Alert.find(
        Alert.field_id == field_id,
        Alert.status == "active"
    ).sort("-timestamp").to_list()
    
    return {
        "active_alerts": [
            {
                "alert_id": str(alert.id),
                "type": alert.alert_type,
                "severity": alert.severity,
                "zone_id": alert.zone_id,
                "timestamp": alert.timestamp,
                "message": alert.message,
                "metrics": alert.metrics,
                "recommendation": alert.recommendation
            }
            for alert in alerts
        ],
        "total_active": len(alerts)
    }


@router.post("/acknowledge/{alert_id}")
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert"""
    alert = await Alert.get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.acknowledged = True
    alert.acknowledged_at = datetime.utcnow()
    await alert.save()
    
    return {"status": "success", "alert_id": alert_id}
