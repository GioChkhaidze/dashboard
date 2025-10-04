"""
Analytics Endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from app.models.daily_data import DailyData
from datetime import datetime
from calendar import monthrange

router = APIRouter()

@router.get("/monthly")
async def get_monthly_analytics(
    field_id: str = Query(...),
    month: str = Query(None)  # Format: YYYY-MM
):
    """Get monthly analytics"""
    if not month:
        month = datetime.utcnow().strftime("%Y-%m")
    
    year, month_num = map(int, month.split("-"))
    days_in_month = monthrange(year, month_num)[1]
    
    start_date = f"{month}-01"
    end_date = f"{month}-{days_in_month:02d}"
    
    monthly_data = await DailyData.find(
        DailyData.field_id == field_id,
        DailyData.date >= start_date,
        DailyData.date <= end_date
    ).to_list()
    
    if not monthly_data:
        raise HTTPException(status_code=404, detail="No data for this month")
    
    total_pests = sum(d.aggregates["pest_count"] for d in monthly_data)
    avg_canopy = sum(d.aggregates["avg_canopy"] for d in monthly_data) / len(monthly_data)
    
    return {
        "month": month,
        "total_pests": total_pests,
        "avg_canopy": round(avg_canopy, 2),
        "data_points": len(monthly_data)
    }
