"""
Canopy Coverage Endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from app.models.daily_data import DailyData
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/daily")
async def get_daily_canopy_data(
    field_id: str = Query(...),
    date: str = Query(None)
):
    """Get canopy data for a specific date"""
    if not date:
        date = datetime.utcnow().strftime("%Y-%m-%d")
    
    data = await DailyData.find_one(
        DailyData.field_id == field_id,
        DailyData.date == date
    )
    
    if not data:
        raise HTTPException(status_code=404, detail="No data found")
    
    return {
        "date": data.date,
        "grid_data": data.heatmaps["canopy_grid"],
        "statistics": {
            "avg": data.aggregates["avg_canopy"],
            "min": data.aggregates["min_canopy"],
            "max": data.aggregates["max_canopy"]
        },
        "low_coverage_zones": [
            zone for zone in data.aggregates.get("critical_zones", [])
            if zone["canopy_cover"] < 60
        ]
    }


@router.get("/trend")
async def get_canopy_trend(
    field_id: str = Query(...),
    days: int = Query(7, ge=1, le=30)
):
    """Get canopy trend over time"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    daily_data = await DailyData.find(
        DailyData.field_id == field_id,
        DailyData.timestamp >= start_date,
        DailyData.timestamp <= end_date
    ).sort("date").to_list()
    
    daily_averages = [
        {"date": d.date, "avg_canopy": d.aggregates["avg_canopy"]}
        for d in daily_data
    ]
    
    if len(daily_averages) > 1:
        change_pct = ((daily_averages[-1]["avg_canopy"] - daily_averages[0]["avg_canopy"]) / 
                     daily_averages[0]["avg_canopy"] * 100)
        trend = "improving" if change_pct > 0 else "declining"
    else:
        change_pct = 0
        trend = "stable"
    
    return {
        "daily_averages": daily_averages,
        "trend": trend,
        "change_pct": round(change_pct, 2)
    }
