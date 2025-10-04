# Agricultural Dashboard - System Architecture

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   DJI AGRAS T50 DRONE SYSTEM                    │
│  ┌──────────────────────┐    ┌──────────────────────────────┐  │
│  │  Pest Detection AI   │    │  Canopy Cover Model          │  │
│  │  Output: Heatmap     │    │  Output: 2D Grid (%)         │  │
│  └──────────┬───────────┘    └──────────┬───────────────────┘  │
└─────────────┼──────────────────────────┼──────────────────────┘
              │                          │
              │      Daily Ingestion     │
              └────────────┬─────────────┘
                           │
              ┌────────────▼────────────┐
              │   FastAPI Backend       │
              │  ┌──────────────────┐   │
              │  │ Data Processing  │   │
              │  │ - Heatmap Gen    │   │
              │  │ - Grid Analytics │   │
              │  │ - Aggregations   │   │
              │  │ - Alert Detection│   │
              │  └──────────────────┘   │
              │  ┌──────────────────┐   │
              │  │  REST API        │   │
              │  │  /api/pests      │   │
              │  │  /api/canopy     │   │
              │  │  /api/insights   │   │
              │  │  /api/drone 🚁   │   │
              │  │  /api/alerts     │   │
              │  └──────────────────┘   │
              │  ┌──────────────────┐   │
              │  │  Static Files    │   │
              │  │  /static/        │   │
              │  └──────────────────┘   │
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │      MongoDB            │
              │  ┌──────────────────┐   │
              │  │ daily_data       │   │
              │  │ field_config     │   │
              │  │ alerts           │   │
              │  │ drone_status 🚁  │   │
              │  │ flight_records 🚁│   │
              │  │ aggregates       │   │
              │  └──────────────────┘   │
              └────────────┬────────────┘
                           │
                    REST API Calls
                           │
              ┌────────────▼────────────┐
              │   React Frontend        │
              │  (Vite + TailwindCSS)   │
              │                         │
              │  ┌──────────────────┐   │
              │  │  Dashboard       │   │
              │  │  - KPI Cards     │   │
              │  │  - Trends        │   │
              │  │  - Alerts        │   │
              │  └──────────────────┘   │
              │  ┌──────────────────┐   │
              │  │  Heatmap View    │   │
              │  │  - Pest Density  │   │
              │  │  - Canopy Cover  │   │
              │  │  - Time Slider   │   │
              │  └──────────────────┘   │
              │  ┌──────────────────┐   │
              │  │  Field Insights  │   │
              │  │  - Grid Zones    │   │
              │  │  - Risk Analysis │   │
              │  └──────────────────┘   │
              │  ┌──────────────────┐   │
              │  │  Analytics       │   │
              │  │  - Charts        │   │
              │  │  - Statistics    │   │
              │  └──────────────────┘   │
              │  ┌──────────────────┐   │
              │  │  Drone Details 🚁│   │
              │  │  - Status        │   │
              │  │  - Flight History│   │
              │  │  - Flight Path   │   │
              │  │  - Specs         │   │
              │  └──────────────────┘   │
              └─────────────────────────┘
```

## 📊 Data Flow Pipeline

### 1. Daily Data Ingestion (Scheduled: 07:00)

```
AI Model Outputs → FastAPI Ingestion Endpoint → Data Processing → MongoDB Storage
```

**Processing Steps:**
1. Receive pest detection data (density heatmap)
2. Receive canopy cover 2D array `[[%, %, ...], [...]]`
3. Validate data integrity
4. Process into grid-based heatmaps
5. Calculate aggregates (total pests, avg canopy)
6. Compute weekly/monthly trends
7. Detect critical alerts (pest density > threshold)
8. Generate recommendations
9. Store raw + processed data

### 2. Real-time Dashboard Queries

```
User Request → React App → API Call → FastAPI → MongoDB Query → Response → Visualization
```

## 🗄️ MongoDB Schema Design

### Collection: `daily_data`

```json
{
  "_id": "ObjectId",
  "field_id": "field_001",
  "date": "2025-10-03",
  "timestamp": "2025-10-03T07:00:00Z",
  "canopy_cover": [
    [72.5, 68.3, 75.1, 82.0, ...],
    [70.2, 65.8, 71.5, 78.3, ...],
    [...]
  ],
  "field_dimensions": {
    "width_m": 50,
    "height_m": 50,
    "grid_resolution": 1.0
  },
  "aggregates": {
    "pest_count": 342,
    "avg_canopy": 72.4,
    "min_canopy": 45.2,
    "max_canopy": 95.6,
    "critical_zones": [
      {
        "zone_id": "grid_3_5",
        "pest_density": 8.5,
        "canopy_cover": 48.2,
        "risk_level": "high"
      }
    ]
  },
  "heatmaps": {
    "pest_density": [
      [0, 2, 5, 1, ...],
      [3, 7, 2, 0, ...],
      [...]
    ],
    "canopy_grid": [
      [72.5, 68.3, 75.1, ...],
      [70.2, 65.8, 71.5, ...],
      [...]
    ]
  },
  "metadata": {
    "drone_flight_id": "flight_20251003_0700",
    "weather": {
      "temperature": 22,
      "humidity": 65,
      "conditions": "sunny"
    }
  }
}
```

### Collection: `field_config`

```json
{
  "_id": "ObjectId",
  "field_id": "field_001",
  "name": "North Field",
  "location": {
    "coordinates": [34.0522, -118.2437],
    "address": "Farm Location"
  },
  "dimensions": {
    "width_m": 100,
    "height_m": 80,
    "area_hectares": 0.8
  },
  "grid_config": {
    "cell_size_m": 1.0,
    "grid_width": 100,
    "grid_height": 80
  },
  "thresholds": {
    "pest_density_warning": 5.0,
    "pest_density_critical": 10.0,
    "canopy_warning": 60.0,
    "canopy_critical": 50.0
  },
  "crop_type": "corn",
  "planting_date": "2025-04-15",
  "expected_harvest": "2025-11-01"
}
```

### Collection: `alerts`

```json
{
  "_id": "ObjectId",
  "field_id": "field_001",
  "date": "2025-10-03",
  "timestamp": "2025-10-03T07:15:00Z",
  "alert_type": "high_pest_density",
  "severity": "critical",
  "zone_id": "grid_3_5",
  "metrics": {
    "pest_density": 12.3,
    "canopy_cover": 48.2
  },
  "message": "Critical pest density detected in Zone 3-5. Immediate action recommended.",
  "recommendation": "Consider targeted pesticide application in this zone.",
  "status": "active",
  "acknowledged": false
}
```

### Collection: `weekly_aggregates`

```json
{
  "_id": "ObjectId",
  "field_id": "field_001",
  "week_start": "2025-09-29",
  "week_end": "2025-10-05",
  "daily_stats": [
    {
      "date": "2025-09-29",
      "pest_count": 320,
      "avg_canopy": 71.2
    },
    {
      "date": "2025-09-30",
      "pest_count": 335,
      "avg_canopy": 72.1
    }
  ],
  "weekly_summary": {
    "total_pests": 2340,
    "avg_pest_per_day": 334,
    "avg_canopy": 72.4,
    "canopy_trend": "improving",
    "pest_trend": "increasing",
    "change_vs_last_week": {
      "pest_change_pct": 12.5,
      "canopy_change_pct": 3.2
    }
  }
}
```

### Collection: `monthly_aggregates`

```json
{
  "_id": "ObjectId",
  "field_id": "field_001",
  "month": "2025-10",
  "total_pests": 9850,
  "avg_canopy": 73.1,
  "peak_pest_date": "2025-10-15",
  "lowest_canopy_date": "2025-10-03",
  "weekly_breakdown": [...],
  "trend_vs_last_month": {
    "pest_change_pct": -8.3,
    "canopy_change_pct": 5.7
  }
}
```

### Collection: `drone_status` 🚁

```json
{
  "_id": "ObjectId",
  "drone_id": "drone_001",
  "model": "DJI AGRAS T50",
  "serial_number": "T50-2024-001",
  "firmware_version": "v3.2.1",
  "battery_level": 85,
  "operational_status": "standby",
  "health_status": "excellent",
  "gps_status": "excellent",
  "motor_health": 95,
  "propeller_health": 92,
  "signal_strength": 88,
  "total_flights": 247,
  "total_flight_hours": 124.5,
  "auto_flight_enabled": true,
  "next_scheduled_flight": "2025-10-05T07:00:00Z",
  "last_maintenance": "2025-08-05T00:00:00Z",
  "next_service_due": "2025-11-03T00:00:00Z",
  "camera": {
    "model": "DJI Zenmuse P1",
    "resolution": "45MP Full-Frame",
    "sensor_type": "CMOS Full-Frame",
    "fov": "63.5° (35mm)",
    "lens_quality": "excellent",
    "image_quality": 99,
    "stabilization": "3-axis gimbal"
  },
  "specs": {
    "weight": "47.5 kg (with full tank)",
    "max_speed": "10 m/s",
    "max_altitude": "30 m AGL",
    "max_flight_time": "18 min (full load)",
    "wind_resistance": "8 m/s",
    "temp_range": "-10°C to 45°C",
    "spray_width": "11 m",
    "tank_capacity": "40 L"
  },
  "battery": {
    "type": "DB1560 Intelligent Battery",
    "capacity": "29,000 mAh",
    "voltage": "52.22 V",
    "charge_time": "10 min (80%)",
    "cycles": "247 / 1500",
    "health": "92%"
  },
  "image_url": "/static/drone.png",
  "last_updated": "2025-10-04T06:00:00Z"
}
```

### Collection: `flight_records` 🚁

```json
{
  "_id": "ObjectId",
  "date": "2025-10-03T07:00:00Z",
  "duration": 28,
  "distance_covered": 5.2,
  "battery_used": 65,
  "images_captured": 248,
  "status": "success",
  "field_id": "field_001"
}
```

## 🔌 API Design (FastAPI Endpoints)

### Base URL: `http://localhost:8000/api/v1`

### 1. Data Ingestion Endpoints

#### POST `/ingestion/daily`
Ingest daily field monitoring data

**Request:**
```json
{
  "field_id": "field_001",
  "timestamp": "2025-10-03T07:00:00Z",
  "pest_heatmap": [[0, 2, 5, 1, ...], [3, 7, 2, 0, ...], ...],
  "canopy_cover": [[72.5, 68.3, ...], ...],
  "field_dimensions": {
    "width_m": 100,
    "height_m": 80
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data_id": "67890abcdef",
  "processing_summary": {
    "pest_count": 342,
    "avg_canopy": 72.4,
    "alerts_generated": 2
  }
}
```

### 2. Dashboard KPI Endpoints

#### GET `/dashboard/kpis/today?field_id=field_001`

**Response:**
```json
{
  "date": "2025-10-03",
  "pest_count": 342,
  "avg_canopy_cover": 72.4,
  "change_vs_yesterday": {
    "pest_change": 15,
    "pest_change_pct": 4.6,
    "canopy_change": 1.2,
    "canopy_change_pct": 1.7
  },
  "status": "warning",
  "active_alerts": 2
}
```

#### GET `/dashboard/kpis/weekly?field_id=field_001`

**Response:**
```json
{
  "week_start": "2025-09-29",
  "week_end": "2025-10-05",
  "daily_pest_counts": [320, 335, 328, 342, 356, 370, 382],
  "daily_canopy_avg": [71.2, 72.1, 71.8, 72.4, 73.1, 73.5, 74.2],
  "weekly_summary": {
    "total_pests": 2433,
    "avg_canopy": 72.6,
    "pest_trend": "increasing",
    "canopy_trend": "improving"
  }
}
```

### 3. Pest Detection Endpoints

#### GET `/pests/daily?field_id=field_001&date=2025-10-03`

**Response:**
```json
{
  "date": "2025-10-03",
  "total_count": 342,
  "heatmap_grid": [
    [0, 2, 5, 1, ...],
    [3, 7, 2, 0, ...],
    [...]
  ],
  "grid_dimensions": {
    "width": 100,
    "height": 80,
    "cell_size_m": 1.0
  },
  "hotspots": [
    {
      "zone_id": "grid_3_5",
      "pest_count": 25,
      "density": 12.3
    }
  ]
}
```

#### GET `/pests/trend?field_id=field_001&days=7`

**Response:**
```json
{
  "start_date": "2025-09-27",
  "end_date": "2025-10-03",
  "daily_counts": [
    {"date": "2025-09-27", "count": 305},
    {"date": "2025-09-28", "count": 312},
    {"date": "2025-09-29", "count": 320},
    {"date": "2025-09-30", "count": 335},
    {"date": "2025-10-01", "count": 328},
    {"date": "2025-10-02", "count": 342},
    {"date": "2025-10-03", "count": 356}
  ],
  "trend": "increasing",
  "change_pct": 16.7
}
```

### 4. Canopy Cover Endpoints

#### GET `/canopy/daily?field_id=field_001&date=2025-10-03`

**Response:**
```json
{
  "date": "2025-10-03",
  "grid_data": [
    [72.5, 68.3, 75.1, ...],
    [70.2, 65.8, 71.5, ...],
    [...]
  ],
  "statistics": {
    "avg": 72.4,
    "min": 45.2,
    "max": 95.6,
    "std_dev": 12.3
  },
  "low_coverage_zones": [
    {
      "zone_id": "grid_3_5",
      "coverage": 48.2,
      "status": "critical"
    }
  ]
}
```

#### GET `/canopy/trend?field_id=field_001&days=7`

**Response:**
```json
{
  "daily_averages": [
    {"date": "2025-09-27", "avg_canopy": 68.5},
    {"date": "2025-09-28", "avg_canopy": 69.2},
    {"date": "2025-09-29", "avg_canopy": 71.2},
    {"date": "2025-09-30", "avg_canopy": 72.1},
    {"date": "2025-10-01", "avg_canopy": 71.8},
    {"date": "2025-10-02", "avg_canopy": 72.4},
    {"date": "2025-10-03", "avg_canopy": 73.1}
  ],
  "trend": "improving",
  "change_pct": 6.7
}
```

### 5. Field Insights Endpoints

#### GET `/insights/zones?field_id=field_001&date=2025-10-03`

**Response:**
```json
{
  "date": "2025-10-03",
  "grid_zones": [
    {
      "zone_id": "grid_0_0",
      "position": {"x": 0, "y": 0},
      "avg_canopy": 75.2,
      "pest_density": 2.1,
      "risk_level": "low",
      "weekly_change": {
        "canopy_change_pct": 3.5,
        "pest_change_pct": -5.2
      },
      "status": "healthy"
    },
    {
      "zone_id": "grid_3_5",
      "position": {"x": 3, "y": 5},
      "avg_canopy": 48.2,
      "pest_density": 12.3,
      "risk_level": "critical",
      "weekly_change": {
        "canopy_change_pct": -8.5,
        "pest_change_pct": 45.2
      },
      "status": "critical",
      "recommendation": "Immediate targeted pesticide application recommended"
    }
  ],
  "summary": {
    "healthy_zones": 85,
    "warning_zones": 10,
    "critical_zones": 5
  }
}
```

### 6. Alerts Endpoints

#### GET `/alerts/active?field_id=field_001`

**Response:**
```json
{
  "active_alerts": [
    {
      "alert_id": "alert_123",
      "type": "high_pest_density",
      "severity": "critical",
      "zone_id": "grid_3_5",
      "timestamp": "2025-10-03T07:15:00Z",
      "message": "Critical pest density detected in Zone 3-5",
      "metrics": {
        "pest_density": 12.3,
        "canopy_cover": 48.2
      },
      "recommendation": "Consider targeted pesticide application"
    }
  ],
  "total_active": 2
}
```

### 7. Analytics Endpoints

#### GET `/analytics/monthly?field_id=field_001&month=2025-10`

**Response:**
```json
{
  "month": "2025-10",
  "total_pests": 9850,
  "avg_canopy": 73.1,
  "comparison_vs_last_month": {
    "pest_change_pct": -8.3,
    "canopy_change_pct": 5.7
  },
  "weekly_breakdown": [
    {
      "week": 1,
      "avg_pests": 335,
      "avg_canopy": 72.1
    }
  ]
}
```

### 8. Drone Endpoints 🚁

#### GET `/drone/status?drone_id=drone_001`
Get DJI AGRAS T50 status and flight history

**Response:**
```json
{
  "drone": {
    "drone_id": "drone_001",
    "model": "DJI AGRAS T50",
    "battery_level": 85,
    "operational_status": "standby",
    "health_status": "excellent",
    "total_flights": 247,
    "total_flight_hours": 124.5,
    "auto_flight_enabled": true,
    "next_scheduled_flight": "2025-10-05T07:00:00Z",
    "camera": {...},
    "specs": {...},
    "battery": {...}
  },
  "flight_history": [
    {
      "date": "2025-10-03T07:00:00Z",
      "duration": 28,
      "distance_covered": 5.2,
      "battery_used": 65,
      "images_captured": 248,
      "status": "success"
    }
  ]
}
```

#### POST `/drone/log-flight`
Log a completed flight

**Request:**
```json
{
  "date": "2025-10-04T07:00:00Z",
  "duration": 30,
  "distance_covered": 5.5,
  "battery_used": 68,
  "images_captured": 265,
  "status": "success",
  "field_id": "field_001"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Flight logged successfully",
  "flight_id": "67890abcdef"
}
```

#### POST `/drone/toggle-auto-flight?drone_id=drone_001`
Enable/disable automatic flight scheduling

**Request:**
```json
{
  "enabled": false
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Automatic flights disabled",
  "auto_flight_enabled": false,
  "next_scheduled_flight": null
}
```

#### POST `/drone/upgrade-to-t50?drone_id=drone_001`
Upgrade drone to DJI AGRAS T50 specifications

**Response:**
```json
{
  "status": "success",
  "message": "Drone upgraded to DJI AGRAS T50 successfully",
  "drone": {...}
}
```

## 🎨 Frontend Component Architecture

### Component Hierarchy

```
App
├── Layout
│   ├── Sidebar
│   ├── Header
│   └── MainContent
├── DashboardView (default route: /)
│   ├── KPICards
│   │   ├── PestCountCard
│   │   ├── CanopyCoverCard
│   │   └── AlertsCard
│   ├── TrendCharts
│   │   ├── PestTrendChart
│   │   └── CanopyTrendChart
│   └── AlertsBanner
├── HeatmapView (route: /heatmap)
│   ├── HeatmapCanvas
│   │   ├── PestHeatmap
│   │   └── CanopyHeatmap
│   ├── TimeSlider
│   ├── LayerToggle
│   └── LegendPanel
├── FieldInsightsView (route: /insights)
│   ├── FieldGrid
│   │   └── GridZoneCard
│   ├── RiskMatrix
│   └── ZoneDetails
├── AnalyticsView (route: /analytics)
│   ├── StatisticsPanel
│   ├── ComparisonCharts
│   └── ExportButton
├── DroneDetailsView (route: /drone) 🚁
│   ├── DroneStatusCards
│   │   ├── BatteryCard
│   │   ├── FlightTimeCard
│   │   └── HealthCard
│   ├── DroneImageDisplay
│   ├── FlightPathMap
│   ├── TabNavigation
│   │   ├── OverviewTab
│   │   │   ├── DroneVisual
│   │   │   ├── CurrentStatus
│   │   │   ├── HealthCheck
│   │   │   └── FlightPathMap
│   │   ├── CameraTab
│   │   │   ├── CameraSpecs
│   │   │   └── SensorSystems
│   │   ├── HistoryTab
│   │   │   └── FlightHistoryTable
│   │   └── SpecsTab
│   │       ├── TechnicalSpecs
│   │       ├── BatterySpecs
│   │       └── MaintenanceSchedule
│   └── AutoFlightToggle
└── SettingsView (route: /settings)
    ├── FieldConfig
    └── ThresholdSettings
```

## 🔄 State Management

**Recommended: React Context + Custom Hooks**

```
contexts/
├── FieldContext.js       # Current field selection
├── DateContext.js        # Current date/time range
├── DataContext.js        # Dashboard data cache
└── AlertsContext.js      # Active alerts
```

## 🚀 Performance Optimizations

1. **Lazy Loading**: Code-split routes using React.lazy()
2. **Data Caching**: Use React Query or SWR for API caching
3. **Virtualization**: For large grid views (react-window)
4. **Debouncing**: Time slider updates
5. **Memoization**: React.memo for expensive components
6. **Web Workers**: Heavy heatmap calculations
7. **Canvas Rendering**: For smooth heatmap animations

## 🔐 Security Considerations

1. **Authentication**: JWT-based auth for API
2. **Field-level permissions**: Users see only their fields
3. **API rate limiting**: Prevent abuse
4. **Input validation**: Pydantic models in FastAPI
5. **CORS configuration**: Restrict origins
6. **Environment variables**: Secure credentials

## 📦 Technology Stack Summary

### Backend
- **Framework**: FastAPI 0.104+
- **Database**: MongoDB 7.0+ (Motor async driver)
- **Validation**: Pydantic v2
- **Processing**: NumPy, Pandas
- **Task Scheduling**: APScheduler or Celery

### Frontend
- **Framework**: React 18+
- **Build Tool**: Vite 5+
- **Styling**: TailwindCSS 3.4+
- **UI Components**: shadcn/ui
- **Charts**: Recharts / Chart.js
- **State**: React Context + React Query
- **Routing**: React Router v6

### DevOps
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: Winston (Node) / Loguru (Python)
