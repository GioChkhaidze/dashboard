# Alert & Recommendation System

## Overview
The Agricultural Dashboard now includes a comprehensive alert and recommendation system that provides actionable insights for farmers based on real-time field data.

## Alert Types

### 1. **Combined Risk (Critical)**
- **Trigger**: High pest density (≥10 pests/cell) AND low canopy (<50%)
- **Severity**: Critical
- **Icon**: ⚠️
- **Example Message**: "URGENT: Corn crop under dual stress in grid_15_23"
- **Recommendations**:
  1. Apply targeted pesticide for specific crop pests
  2. Increase irrigation immediately
  3. Monitor daily for next 3-5 days
  4. Consider soil nutrient analysis

### 2. **Pest Outbreak (Critical)**
- **Trigger**: Pest count ≥10 per cell
- **Severity**: Critical
- **Icon**: 🐛
- **Example Message**: "Pest Outbreak: Wheat zone grid_31_36 needs attention"
- **Recommendations**:
  1. Apply crop-specific pesticide to affected zone
  2. Inspect neighboring zones for spread
  3. Document pest species if possible
  4. Re-scan in 48 hours to verify treatment effectiveness

### 3. **Pest Warning (Warning)**
- **Trigger**: Pest count between 5-9 per cell
- **Severity**: Warning
- **Icon**: 👀
- **Example Message**: "Monitor: Wheat pest activity increasing in grid_28_41"
- **Recommendations**:
  1. Inspect zone for pests
  2. Prepare pesticide equipment if count increases
  3. Check this zone again in 2-3 days
  4. Document pest species and behavior

### 4. **Canopy Stress (Warning)**
- **Trigger**: Low canopy (<50%) in pest-affected zones
- **Severity**: Warning
- **Icon**: 🌱
- **Example Message**: "Canopy Stress: Corn health declining in grid_14_22"
- **Recommendations**:
  1. Check irrigation coverage in zone
  2. Verify soil moisture levels
  3. Consider nitrogen/nutrient supplementation
  4. Inspect for disease or root issues

### 5. **Irrigation Needed (Warning)**
- **Trigger**: Low canopy (<50%) without high pest count
- **Severity**: Warning
- **Icon**: 💧
- **Example Message**: "Irrigation Alert: Low canopy in grid_16_25 (43.9%)"
- **Recommendations**:
  1. Increase water delivery to zone
  2. Current vs. target canopy comparison
  3. Check for irrigation system blockages
  4. Monitor soil moisture daily

### 6. **Crop-Specific Outbreak (Warning)**
- **Trigger**: One crop type has >40% of total field pests
- **Severity**: Warning
- **Icon**: 🌾
- **Example Message**: "Wheat Alert: Field-wide pest concentration detected"
- **Recommendations**:
  1. Crop-specific treatment strategy
  2. Consider field-wide pesticide application
  3. Review planting strategy for next season
  4. Monitor all zones with this crop closely

## Thresholds

### Pest Thresholds
- **Warning**: 5 pests per grid cell
- **Critical**: 10 pests per grid cell

### Canopy Thresholds
- **Warning**: <60% coverage
- **Critical**: <50% coverage

## API Endpoints

### Get Active Alerts
```
GET /api/v1/alerts/active?field_id=field_001
```

**Response:**
```json
{
  "active_alerts": [
    {
      "alert_id": "68e09e8abc382923d4bd10ce",
      "type": "pest_outbreak",
      "severity": "critical",
      "zone_id": "grid_31_36",
      "timestamp": "2025-10-04T04:11:54.067000",
      "message": "🐛 Pest Outbreak: Corn zone grid_31_36 needs attention",
      "metrics": {
        "pest_count": 10,
        "pest_density": 10.0,
        "canopy_cover": 79.79,
        "crop_type": "Corn"
      },
      "recommendation": "🎯 Pest Control Action:\n1. Apply Corn-specific pesticide to grid_31_36\n2. Inspect neighboring zones for spread\n3. Document pest species if possible\n4. Re-scan in 48 hours to verify treatment effectiveness"
    }
  ],
  "total_active": 1774
}
```

### Acknowledge Alert
```
POST /api/v1/alerts/acknowledge/{alert_id}
```

## Data Generator Configuration

The dummy data generator has been optimized to create alert-triggering conditions:
- **Hotspot probability**: 70% (increased from 50%)
- **Low canopy zone probability**: 50% (increased from 30%)
- **Hotspot pest density**: 8-15 pests per cell (ensures critical alerts)
- **Stress patch severity**: 15-35% canopy reduction (ensures irrigation alerts)

## Alert Metrics

Typical data generation produces:
- **11-290 alerts per day** depending on field conditions
- Alert distribution:
  - ~60% Irrigation alerts (low canopy zones)
  - ~30% Pest warnings (moderate pest activity)
  - ~8% Pest outbreaks (critical pest density)
  - ~2% Combined risk (dual stress conditions)
  - <1% Field-wide crop alerts

## Implementation Details

### Alert Model
- **File**: `backend/app/models/alert.py`
- **Fields**: alert_type, severity, zone_id, metrics (Dict[str, Any]), message, recommendation, status
- **Status options**: active, acknowledged, resolved

### Ingestion Logic
- **File**: `backend/app/api/v1/endpoints/ingestion.py`
- Alerts are generated during data ingestion
- Multiple alert types checked per ingestion
- Alerts are zone-specific or field-wide
- Old alerts for same date are deleted before creating new ones

### Data Generator
- **File**: `generate_dummy_data.py`
- Creates realistic pest hotspots with gaussian distribution
- Generates canopy stress zones with multiple severity levels
- Ensures sufficient pest counts to trigger alert thresholds
- Produces multi-crop fields with crop-specific pest patterns

## Future Enhancements

Potential improvements:
1. **Alert Prioritization**: Sort by severity and urgency score
2. **Historical Tracking**: Alert resolution tracking and effectiveness metrics
3. **Predictive Alerts**: ML-based early warning system
4. **Mobile Notifications**: Push alerts to farmer mobile devices
5. **Zone-Based Actions**: Batch recommendations for adjacent zones
6. **Weather Integration**: Adjust thresholds based on weather conditions
7. **Cost Estimation**: Estimate treatment costs for recommendations

## Testing

To test the alert system:
```powershell
# Generate test data with alerts
python generate_dummy_data.py

# View active alerts
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/alerts/active?field_id=field_001"

# View in dashboard
# Navigate to Dashboard page - alerts shown in Alert Banner component
```
