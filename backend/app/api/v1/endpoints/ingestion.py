"""
Data Ingestion Endpoints
Handles daily drone flight data ingestion
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime
import numpy as np

from app.models.daily_data import DailyData
from app.models.alert import Alert
from app.models.field_config import FieldConfig
from app.utils.heatmap import bounding_boxes_to_heatmap, find_hotspots
from app.utils.canopy import calculate_canopy_statistics, find_low_coverage_zones
from app.core.config import settings

router = APIRouter()


class IngestionRequest(BaseModel):
    """Request model for daily data ingestion"""
    field_id: str = Field(..., description="Field identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Flight timestamp")
    pest_grid: List[List[Dict[str, Any]]] = Field(..., description="2D pest grid with count and crop_type per cell")
    canopy_cover: List[List[float]] = Field(..., description="Canopy coverage 2D array")
    field_dimensions: Dict[str, float] = Field(..., description="Field dimensions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class IngestionResponse(BaseModel):
    """Response model for ingestion"""
    status: str
    data_id: str
    processing_summary: Dict[str, Any]


@router.post("/daily", response_model=IngestionResponse, status_code=status.HTTP_201_CREATED)
async def ingest_daily_data(request: IngestionRequest):
    """
    Ingest daily drone flight data
    
    - Receives pest_grid (2D array with count and crop_type per cell) and canopy cover data
    - Processes into per-crop-type heatmaps
    - Calculates aggregates per crop type
    - Generates alerts if needed
    - Stores in database
    """
    try:
        # Get field configuration for thresholds
        field_config = await FieldConfig.find_one(FieldConfig.field_id == request.field_id)
        if not field_config:
            # Use default thresholds
            pest_warning = settings.PEST_DENSITY_WARNING_THRESHOLD
            pest_critical = settings.PEST_DENSITY_CRITICAL_THRESHOLD
            canopy_warning = settings.CANOPY_WARNING_THRESHOLD
            canopy_critical = settings.CANOPY_CRITICAL_THRESHOLD
        else:
            pest_warning = field_config.thresholds.get("pest_density_warning", 5.0)
            pest_critical = field_config.thresholds.get("pest_density_critical", 10.0)
            canopy_warning = field_config.thresholds.get("canopy_warning", 60.0)
            canopy_critical = field_config.thresholds.get("canopy_critical", 50.0)
        
        # Process pest_grid to generate per-crop heatmaps
        field_width = request.field_dimensions.get("width_m", 50)
        field_height = request.field_dimensions.get("height_m", 50)
        grid_size = request.field_dimensions.get("grid_resolution", 1.0)
        
        pest_grid_array = np.array(request.pest_grid, dtype=object)
        grid_height, grid_width = pest_grid_array.shape
        
        # Build per-crop heatmaps and collect all crop types
        crop_types = set()
        pest_counts_by_crop = {}
        heatmaps_by_crop = {}
        
        for row in range(grid_height):
            for col in range(grid_width):
                cell_data = request.pest_grid[row][col]
                if isinstance(cell_data, dict):
                    count = cell_data.get("count", 0)
                    crop_type = cell_data.get("crop_type", "unknown")
                    if count > 0:
                        crop_types.add(crop_type)
                        pest_counts_by_crop[crop_type] = pest_counts_by_crop.get(crop_type, 0) + count
        
        # Initialize heatmaps for each crop type
        for crop_type in crop_types:
            heatmaps_by_crop[crop_type] = np.zeros((grid_height, grid_width), dtype=float)
        
        # Fill heatmaps per crop type
        for row in range(grid_height):
            for col in range(grid_width):
                cell_data = request.pest_grid[row][col]
                if isinstance(cell_data, dict):
                    count = cell_data.get("count", 0)
                    crop_type = cell_data.get("crop_type", "unknown")
                    if count > 0 and crop_type in heatmaps_by_crop:
                        heatmaps_by_crop[crop_type][row, col] = count
        
        # Convert heatmaps to lists for storage
        heatmaps_by_crop_lists = {crop: hmap.tolist() for crop, hmap in heatmaps_by_crop.items()}
        
        # Calculate canopy statistics
        canopy_array = np.array(request.canopy_cover)
        canopy_stats = calculate_canopy_statistics(request.canopy_cover)
        
        # Find hotspots per crop type and low coverage zones
        all_hotspots = []
        for crop_type, heatmap in heatmaps_by_crop.items():
            hotspots_for_crop = find_hotspots(heatmap, threshold=pest_warning, grid_size=grid_size)
            for hs in hotspots_for_crop:
                hs["crop_type"] = crop_type
            all_hotspots.extend(hotspots_for_crop)
        
        low_zones = find_low_coverage_zones(canopy_array, canopy_warning, canopy_critical)
        
        # Identify critical zones (high pest + low canopy)
        critical_zones = []
        for hotspot in all_hotspots:
            x, y = int(hotspot["position"]["x"]), int(hotspot["position"]["y"])
            if y < len(canopy_array) and x < len(canopy_array[0]):
                canopy_val = canopy_array[y][x]
                pest_count = hotspot["pest_count"]
                crop_type = hotspot.get("crop_type", "unknown")
                
                # Check if either condition is critical
                is_pest_critical = pest_count >= pest_critical
                is_canopy_critical = canopy_val < canopy_critical
                
                if is_pest_critical or is_canopy_critical:
                    critical_zones.append({
                        "zone_id": hotspot["zone_id"],
                        "pest_density": hotspot["density"],
                        "pest_count": pest_count,
                        "crop_type": crop_type,
                        "canopy_cover": float(canopy_val),
                        "risk_level": "critical"
                    })
        
        # Create aggregates
        total_pest_count = sum(pest_counts_by_crop.values())
        aggregates = {
            "pest_count": total_pest_count,
            "pest_counts_by_crop": pest_counts_by_crop,
            "avg_canopy": canopy_stats["avg"],
            "min_canopy": canopy_stats["min"],
            "max_canopy": canopy_stats["max"],
            "critical_zones": critical_zones[:10]  # Top 10
        }
        
        # Create daily data document
        date_str = request.timestamp.strftime("%Y-%m-%d")
        
        # Delete existing daily data for this date (to avoid duplicates when regenerating)
        await DailyData.find(
            DailyData.field_id == request.field_id,
            DailyData.date == date_str
        ).delete()
        
        # Delete existing alerts for this date (to avoid duplicates when regenerating)
        await Alert.find(
            Alert.field_id == request.field_id,
            Alert.date == date_str
        ).delete()
        
        daily_data = DailyData(
            field_id=request.field_id,
            date=date_str,
            timestamp=request.timestamp,
            pest_grid=request.pest_grid,
            canopy_cover=request.canopy_cover,
            field_dimensions=request.field_dimensions,
            aggregates=aggregates,
            heatmaps={
                "pest_density_by_crop": heatmaps_by_crop_lists,
                "canopy_grid": request.canopy_cover
            },
            metadata=request.metadata
        )
        
        await daily_data.insert()
        
        # Generate comprehensive recommendation alerts
        alerts_created = 0
        alerts_to_create = []
        
        # 1. Critical zones (high pest + low canopy combined risk)
        for zone in critical_zones:
            crop_type = zone.get("crop_type", "unknown").capitalize()
            pest_count = zone.get("pest_count", 0)
            canopy_val = zone["canopy_cover"]
            zone_id = zone["zone_id"]
            
            # Combined risk - most urgent
            if pest_count >= pest_critical and canopy_val < canopy_critical:
                alerts_to_create.append({
                    "type": "combined_risk",
                    "severity": "critical",
                    "zone_id": zone_id,
                    "message": f"⚠️ URGENT: {crop_type} crop under dual stress in {zone_id}",
                    "recommendation": f"🎯 Immediate Action Required:\n1. Apply targeted pesticide for {crop_type} pests ({pest_count} detected)\n2. Increase irrigation immediately - canopy at {canopy_val:.1f}%\n3. Monitor daily for next 3-5 days\n4. Consider soil nutrient analysis",
                    "metrics": {
                        "pest_count": pest_count,
                        "pest_density": zone["pest_density"],
                        "canopy_cover": canopy_val,
                        "crop_type": crop_type.lower()
                    }
                })
            # High pest density
            elif pest_count >= pest_critical:
                alerts_to_create.append({
                    "type": "pest_outbreak",
                    "severity": "critical",
                    "zone_id": zone_id,
                    "message": f"🐛 Pest Outbreak: {crop_type} zone {zone_id} needs attention",
                    "recommendation": f"🎯 Pest Control Action:\n1. Apply {crop_type}-specific pesticide to {zone_id}\n2. Inspect neighboring zones for spread\n3. Document pest species if possible\n4. Re-scan in 48 hours to verify treatment effectiveness",
                    "metrics": {
                        "pest_count": pest_count,
                        "pest_density": zone["pest_density"],
                        "canopy_cover": canopy_val,
                        "crop_type": crop_type.lower()
                    }
                })
            # Low canopy (stress indicator)
            elif canopy_val < canopy_critical:
                alerts_to_create.append({
                    "type": "canopy_stress",
                    "severity": "warning",
                    "zone_id": zone_id,
                    "message": f"🌱 Canopy Stress: {crop_type} health declining in {zone_id}",
                    "recommendation": f"🎯 Irrigation & Nutrition Action:\n1. Check irrigation coverage in {zone_id} (current: {canopy_val:.1f}%)\n2. Verify soil moisture levels\n3. Consider nitrogen/nutrient supplementation\n4. Inspect for disease or root issues",
                    "metrics": {
                        "pest_count": pest_count,
                        "canopy_cover": canopy_val,
                        "crop_type": crop_type.lower()
                    }
                })
        
        # 2. Moderate pest warnings (above warning threshold but below critical)
        for hotspot in all_hotspots:
            if hotspot["pest_count"] >= pest_warning and hotspot["pest_count"] < pest_critical:
                crop_type = hotspot.get("crop_type", "unknown").capitalize()
                zone_id = hotspot["zone_id"]
                pest_count = hotspot["pest_count"]
                
                # Check if not already alerted
                if not any(a["zone_id"] == zone_id for a in alerts_to_create):
                    alerts_to_create.append({
                        "type": "pest_warning",
                        "severity": "warning",
                        "zone_id": zone_id,
                        "message": f"👀 Monitor: {crop_type} pest activity increasing in {zone_id}",
                        "recommendation": f"🎯 Monitoring Recommendation:\n1. Inspect {zone_id} for {crop_type} pests ({pest_count} detected)\n2. Prepare pesticide equipment if count increases\n3. Check this zone again in 2-3 days\n4. Document pest species and behavior",
                        "metrics": {
                            "pest_count": pest_count,
                            "pest_density": hotspot["density"],
                            "crop_type": crop_type.lower()
                        }
                    })
        
        # 3. Low canopy zones needing irrigation
        for low_zone in low_zones:
            zone_id = f"grid_{low_zone['position']['y']}_{low_zone['position']['x']}"
            canopy_val = low_zone["coverage"]
            
            # Check if not already alerted
            if not any(a["zone_id"] == zone_id for a in alerts_to_create):
                if canopy_val < canopy_critical:
                    alerts_to_create.append({
                        "type": "irrigation_needed",
                        "severity": "warning",
                        "zone_id": zone_id,
                        "message": f"💧 Irrigation Alert: Low canopy in {zone_id} ({canopy_val:.1f}%)",
                        "recommendation": f"🎯 Irrigation Action:\n1. Increase water delivery to {zone_id}\n2. Current canopy: {canopy_val:.1f}% (target: >70%)\n3. Check for irrigation system blockages\n4. Monitor soil moisture daily",
                        "metrics": {
                            "canopy_cover": canopy_val,
                            "target_canopy": 70.0
                        }
                    })
        
        # 4. Crop-specific aggregate alerts (if one crop type is particularly affected)
        for crop_type, pest_count in pest_counts_by_crop.items():
            if pest_count > total_pest_count * 0.4:  # If one crop has >40% of all pests
                crop_display = crop_type.capitalize()
                alerts_to_create.append({
                    "type": "crop_outbreak",
                    "severity": "warning",
                    "zone_id": "field_wide",
                    "message": f"🌾 {crop_display} Alert: Field-wide pest concentration detected",
                    "recommendation": f"🎯 Field-Wide Strategy:\n1. {crop_display} crops are primary pest target ({pest_count} of {total_pest_count} total)\n2. Consider field-wide {crop_display}-specific treatment\n3. Review {crop_display} planting strategy for next season\n4. Monitor all {crop_display} zones closely",
                    "metrics": {
                        "crop_type": crop_type,
                        "pest_count": pest_count,
                        "total_pests": total_pest_count,
                        "percentage": round((pest_count / total_pest_count) * 100, 1)
                    }
                })
                break  # Only one field-wide alert
        
        # Create all alerts in database
        for alert_data in alerts_to_create:
            alert = Alert(
                field_id=request.field_id,
                date=date_str,
                timestamp=datetime.utcnow(),
                alert_type=alert_data["type"],
                severity=alert_data["severity"],
                zone_id=alert_data["zone_id"],
                metrics=alert_data["metrics"],
                message=alert_data["message"],
                recommendation=alert_data["recommendation"]
            )
            await alert.insert()
            alerts_created += 1
        
        return IngestionResponse(
            status="success",
            data_id=str(daily_data.id),
            processing_summary={
                "pest_count": aggregates["pest_count"],
                "avg_canopy": aggregates["avg_canopy"],
                "alerts_generated": alerts_created,
                "critical_zones": len(critical_zones)
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process data: {str(e)}"
        )


@router.get("/status/{field_id}")
async def get_ingestion_status(field_id: str):
    """
    Get latest ingestion status for a field
    """
    latest_data = await DailyData.find(
        DailyData.field_id == field_id
    ).sort("-timestamp").first_or_none()
    
    if not latest_data:
        return {
            "field_id": field_id,
            "status": "no_data",
            "message": "No data ingested yet for this field"
        }
    
    return {
        "field_id": field_id,
        "status": "active",
        "latest_date": latest_data.date,
        "latest_timestamp": latest_data.timestamp,
        "pest_count": latest_data.aggregates.get("pest_count", 0),
        "avg_canopy": latest_data.aggregates.get("avg_canopy", 0)
    }
