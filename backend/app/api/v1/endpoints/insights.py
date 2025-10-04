"""
Field Insights Endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from app.models.daily_data import DailyData
from datetime import datetime
import numpy as np

router = APIRouter()

@router.get("/zones")
async def get_zone_insights(
    field_id: str = Query(...),
    date: str = Query(None)
):
    """Get insights for all zones"""
    if not date:
        date = datetime.utcnow().strftime("%Y-%m-%d")
    
    data = await DailyData.find_one(
        DailyData.field_id == field_id,
        DailyData.date == date
    )
    
    if not data:
        raise HTTPException(status_code=404, detail="No data found")
    
    # Aggregate pest density across all crops (sum all crop heatmaps)
    pest_density_by_crop = data.heatmaps.get("pest_density_by_crop", {})
    if pest_density_by_crop:
        # Sum all crop heatmaps to get total pest density
        all_heatmaps = [np.array(heatmap) for heatmap in pest_density_by_crop.values()]
        pest_heatmap = np.sum(all_heatmaps, axis=0)
    else:
        # Fallback to empty heatmap if no pest data
        canopy_grid = np.array(data.heatmaps["canopy_grid"])
        pest_heatmap = np.zeros_like(canopy_grid)
    
    canopy_grid = np.array(data.heatmaps["canopy_grid"])
    
    # Get critical zones from aggregates (generated during ingestion with actual pest counts)
    critical_zones_data = data.aggregates.get("critical_zones", [])
    
    # Create a map of zone_id -> zone data for quick lookup
    critical_zones_map = {zone.get("zone_id", ""): zone for zone in critical_zones_data}
    
    grid_zones = []
    healthy_count = 0
    warning_count = 0
    critical_count = 0
    
    height, width = pest_heatmap.shape
    for y in range(height):
        for x in range(width):
            zone_id = f"grid_{x}_{y}"
            pest_count_heatmap = float(pest_heatmap[y, x])  # Radial influence value
            canopy = float(canopy_grid[y, x])
            
            # Check if this zone has critical data from ingestion
            critical_zone_info = critical_zones_map.get(zone_id)
            
            if critical_zone_info:
                # Use actual pest count from critical zone data
                actual_pest_count = critical_zone_info.get("pest_count", pest_count_heatmap)
                risk_level = "critical"
                status = "critical"
                critical_count += 1
            elif canopy < 50:
                # Low canopy is critical regardless of pest count
                actual_pest_count = pest_count_heatmap
                risk_level = "critical"
                status = "critical"
                critical_count += 1
            elif pest_count_heatmap >= 5 or canopy < 60:
                actual_pest_count = pest_count_heatmap
                risk_level = "warning"
                status = "warning"
                warning_count += 1
            else:
                actual_pest_count = pest_count_heatmap
                risk_level = "low"
                status = "healthy"
                healthy_count += 1
            
            grid_zones.append({
                "zone_id": zone_id,
                "position": {"x": x, "y": y},
                "avg_canopy": round(canopy, 2),
                "pest_density": round(actual_pest_count, 2),
                "pest_count": int(actual_pest_count) if actual_pest_count >= 1 else 0,
                "risk_level": risk_level,
                "status": status
            })
    
    return {
        "date": date,
        "grid_zones": grid_zones,
        "summary": {
            "healthy_zones": healthy_count,
            "warning_zones": warning_count,
            "critical_zones": critical_count
        }
    }
