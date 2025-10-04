"""
Dashboard KPI Endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from app.models.daily_data import DailyData
from app.models.alert import Alert

router = APIRouter()

@router.get("/kpis/today")
async def get_today_kpis(field_id: str = Query(...)):
    """Get today's KPIs"""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    today_data = await DailyData.find_one(
        DailyData.field_id == field_id,
        DailyData.date == today
    )
    
    yesterday_data = await DailyData.find_one(
        DailyData.field_id == field_id,
        DailyData.date == yesterday
    )
    
    if not today_data:
        raise HTTPException(status_code=404, detail="No data for today")
    
    # Calculate changes
    pest_change = 0
    canopy_change = 0
    if yesterday_data:
        pest_change = today_data.aggregates["pest_count"] - yesterday_data.aggregates["pest_count"]
        canopy_change = today_data.aggregates["avg_canopy"] - yesterday_data.aggregates["avg_canopy"]
    
    # Check active alerts
    active_alerts = await Alert.find(
        Alert.field_id == field_id,
        Alert.status == "active"
    ).count()
    
    return {
        "date": today,
        "pest_count": today_data.aggregates["pest_count"],
        "avg_canopy_cover": today_data.aggregates["avg_canopy"],
        "change_vs_yesterday": {
            "pest_change": pest_change,
            "pest_change_pct": (pest_change / yesterday_data.aggregates["pest_count"] * 100) if yesterday_data else 0,
            "canopy_change": canopy_change,
            "canopy_change_pct": (canopy_change / yesterday_data.aggregates["avg_canopy"] * 100) if yesterday_data else 0
        },
        "status": "critical" if active_alerts > 0 else "healthy",
        "active_alerts": active_alerts
    }


@router.get("/kpis/weekly")
async def get_weekly_kpis(field_id: str = Query(...)):
    """Get weekly KPIs and trends"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    daily_data = await DailyData.find(
        DailyData.field_id == field_id,
        DailyData.timestamp >= start_date,
        DailyData.timestamp <= end_date
    ).sort("date").to_list()
    
    if not daily_data:
        raise HTTPException(status_code=404, detail="No data for this week")
    
    daily_pest_counts = [d.aggregates["pest_count"] for d in daily_data]
    daily_canopy_avg = [d.aggregates["avg_canopy"] for d in daily_data]
    
    # Determine trends
    pest_trend = "increasing" if daily_pest_counts[-1] > daily_pest_counts[0] else "decreasing"
    canopy_trend = "improving" if daily_canopy_avg[-1] > daily_canopy_avg[0] else "declining"
    
    return {
        "week_start": start_date.strftime("%Y-%m-%d"),
        "week_end": end_date.strftime("%Y-%m-%d"),
        "daily_pest_counts": daily_pest_counts,
        "daily_canopy_avg": daily_canopy_avg,
        "weekly_summary": {
            "total_pests": sum(daily_pest_counts),
            "avg_canopy": sum(daily_canopy_avg) / len(daily_canopy_avg),
            "pest_trend": pest_trend,
            "canopy_trend": canopy_trend
        }
    }
