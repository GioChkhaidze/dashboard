"""
Pest Detection Endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from app.models.daily_data import DailyData
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/daily")
async def get_daily_pest_data(
    field_id: str = Query(...),
    date: str = Query(None),
    crop_type: str = Query(None, description="Filter by crop type (wheat, corn, etc.)")
):
    """Get pest data for a specific date, optionally filtered by crop type"""
    if not date:
        date = datetime.utcnow().strftime("%Y-%m-%d")
    
    data = await DailyData.find_one(
        DailyData.field_id == field_id,
        DailyData.date == date
    )
    
    if not data:
        raise HTTPException(status_code=404, detail="No data found")
    
    # Get critical zones with actual pest counts
    critical_zones = data.aggregates.get("critical_zones", [])
    
    # Get available crop types
    pest_counts_by_crop = data.aggregates.get("pest_counts_by_crop", {})
    available_crop_types = list(pest_counts_by_crop.keys())
    
    # Get heatmap for requested crop type or first available
    heatmaps_by_crop = data.heatmaps.get("pest_density_by_crop", {})
    
    if crop_type and crop_type in heatmaps_by_crop:
        selected_heatmap = heatmaps_by_crop[crop_type]
        selected_crop = crop_type
    elif available_crop_types:
        # Default to first available crop type
        selected_crop = available_crop_types[0]
        selected_heatmap = heatmaps_by_crop.get(selected_crop, [])
    else:
        selected_heatmap = []
        selected_crop = None
    
    # Filter critical zones by crop type if requested
    if crop_type:
        critical_zones = [z for z in critical_zones if z.get("crop_type") == crop_type]
    
    return {
        "date": data.date,
        "total_count": data.aggregates["pest_count"],
        "pest_counts_by_crop": pest_counts_by_crop,
        "available_crop_types": available_crop_types,
        "selected_crop_type": selected_crop,
        "pest_grid": data.pest_grid,
        "heatmap_grid": selected_heatmap,
        "heatmaps_by_crop": heatmaps_by_crop,
        "grid_dimensions": data.field_dimensions,
        "hotspots": critical_zones,
        "critical_zones_count": len(critical_zones)
    }


@router.get("/trend")
async def get_pest_trend(
    field_id: str = Query(...),
    days: int = Query(7, ge=1, le=30),
    crop_type: str = Query(None, description="Filter by crop type")
):
    """Get pest trend over time, optionally by crop type"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    daily_data = await DailyData.find(
        DailyData.field_id == field_id,
        DailyData.timestamp >= start_date,
        DailyData.timestamp <= end_date
    ).sort("date").to_list()
    
    if crop_type:
        # Trend for specific crop
        daily_counts = [
            {
                "date": d.date,
                "count": d.aggregates.get("pest_counts_by_crop", {}).get(crop_type, 0)
            }
            for d in daily_data
        ]
    else:
        # Overall trend
        daily_counts = [
            {"date": d.date, "count": d.aggregates["pest_count"]}
            for d in daily_data
        ]
    
    if len(daily_counts) > 1:
        change_pct = ((daily_counts[-1]["count"] - daily_counts[0]["count"]) / 
                     daily_counts[0]["count"] * 100) if daily_counts[0]["count"] > 0 else 0
        trend = "increasing" if change_pct > 0 else "decreasing"
    else:
        change_pct = 0
        trend = "stable"
    
    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "crop_type": crop_type,
        "daily_counts": daily_counts,
        "trend": trend,
        "change_pct": round(change_pct, 2)
    }
