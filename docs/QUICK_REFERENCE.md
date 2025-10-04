# 🚀 Quick Reference Guide

## Project Structure

```
dashboard/
├── README.md                    # Main documentation
├── docker-compose.yml           # Production deployment
├── docker-compose.dev.yml       # Development environment
├── generate_dummy_data.py       # Test data generator
│
├── backend/                     # FastAPI Backend
│   ├── app/
│   │   ├── main.py             # FastAPI entry point
│   │   ├── core/               # Config & database
│   │   ├── models/             # MongoDB models (7 collections)
│   │   ├── api/v1/endpoints/   # API routes (8 endpoint files)
│   │   └── utils/              # Data processing utilities
│   ├── static/                 # Static files (drone.png)
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                    # React Frontend
│   ├── src/
│   │   ├── App.jsx             # Main app with routing
│   │   ├── components/         # UI components
│   │   ├── pages/              # 5 main pages
│   │   ├── hooks/              # React Query hooks
│   │   └── services/           # API client
│   ├── package.json
│   └── Dockerfile
│
└── docs/                        # Documentation
    ├── ARCHITECTURE.md          # System design
    ├── BACKEND_GUIDE.md         # Backend details
    ├── DEPLOYMENT.md            # LAN setup guide
    ├── DRONE_FEATURE.md         # DJI AGRAS T50 docs
    ├── DRONE_QUICKSTART.md      # Drone quick start
    ├── QUICK_REFERENCE.md       # This file
    └── UX_DESIGN.md             # UI/UX specs
```

---

## Quick Commands

### Docker Deployment

```bash
# Start development environment (hot reload)
docker-compose -f docker-compose.dev.yml up

# Start production environment
docker-compose up -d --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### Local Development

```bash
# Backend
cd backend
python -m venv venv
.\venv\Scripts\Activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python -m app.main

# Frontend
cd frontend
npm install
npm run dev

# Generate test data
python generate_dummy_data.py
```

---

## API Endpoints

**Base URL:** `http://[server-ip]:8000/api/v1`

### Dashboard
- `GET /dashboard/kpis/today?field_id=field_001`
- `GET /dashboard/kpis/weekly?field_id=field_001`

### Pests
- `GET /pests/daily?field_id=field_001&date=2025-10-04`
- `GET /pests/trend?field_id=field_001&days=7`

### Canopy
- `GET /canopy/daily?field_id=field_001&date=2025-10-04`
- `GET /canopy/trend?field_id=field_001&days=7`

### Insights
- `GET /insights/zones?field_id=field_001&date=2025-10-04`

### Alerts
- `GET /alerts/active?field_id=field_001`
- `POST /alerts/acknowledge/{alert_id}`

### Analytics
- `GET /analytics/monthly?field_id=field_001&month=2025-10`

### Drone (DJI AGRAS T50)
- `GET /drone/status?drone_id=drone_001`
- `GET /drone/flights?drone_id=drone_001&limit=30`
- `POST /drone/log-flight`
- `POST /drone/update-status?drone_id=drone_001`
- `POST /drone/toggle-auto-flight?drone_id=drone_001`
- `POST /drone/upgrade-to-t50?drone_id=drone_001`

### Ingestion
- `POST /ingestion/daily`
- `GET /ingestion/status/{field_id}`

---

## MongoDB Collections

```javascript
// Daily field data with pest/canopy grids
daily_data { field_id, date, pest_density_grid, canopy_cover_grid, ... }

// Field configuration
field_config { field_id, name, dimensions, grid_size, location }

// Active alerts
alerts { field_id, alert_type, severity, zone, recommendation, ... }

// Weekly aggregates
weekly_aggregates { field_id, week_start, avg_pest_density, ... }

// Monthly aggregates
monthly_aggregates { field_id, month, total_pests, avg_canopy, ... }

// DJI AGRAS T50 status
drone_status { drone_id, model, battery_level, auto_flight_enabled, ... }

// Flight records
flight_records { date, duration, distance_covered, battery_used, status, ... }
```

---

## Frontend Pages

| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/` | KPIs, trends, alerts |
| Heatmap | `/heatmap` | Field visualization |
| Insights | `/insights` | Zone analysis |
| Analytics | `/analytics` | Long-term trends |
| Drone | `/drone` | DJI AGRAS T50 status |

---

## Environment Variables

### Backend (.env)
```env
MONGODB_URL=mongodb://mongodb:27017
MONGODB_DB_NAME=agri_dashboard
CORS_ORIGINS=http://192.168.1.100,http://192.168.1.100:5173
```

### Frontend (.env)
```env
VITE_API_BASE_URL=http://192.168.1.100:8000/api/v1
```

---

## Common Tasks

### Generate Test Data
```bash
python generate_dummy_data.py
# Choose option 1 for fresh data
```

### Access API Documentation
```
http://[server-ip]:8000/docs  # Swagger UI
http://[server-ip]:8000/redoc  # ReDoc
```

### Check Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mongodb
```

### Restart Services
```bash
docker-compose restart
```

### Database Queries
```bash
# Connect to MongoDB
docker exec -it mongodb mongosh

# Switch to database
use agri_dashboard

# Count documents
db.daily_data.count()
db.flight_records.count()

# View drone status
db.drone_status.findOne({drone_id: "drone_001"})
```

---

## Troubleshooting

### Frontend won't load
```bash
# Check if running
docker-compose ps

# Restart frontend
docker-compose restart frontend

# Check logs
docker-compose logs frontend
```

### API returns 404
```bash
# Verify backend is running
curl http://localhost:8000/docs

# Check MongoDB connection
docker-compose logs mongodb
```

### No data showing
```bash
# Generate test data
python generate_dummy_data.py

# Verify data exists
docker exec -it mongodb mongosh
> use agri_dashboard
> db.daily_data.count()
```

### Can't access from other devices
```bash
# Check firewall (Windows)
New-NetFirewallRule -DisplayName "AgriDashboard" -Direction Inbound -LocalPort 80,8000 -Protocol TCP -Action Allow

# Check Docker networks
docker network ls
docker network inspect dashboard_default
```

---

## DJI AGRAS T50 Quick Reference

### Specifications
- Weight: 47.5 kg (with full tank)
- Max Speed: 10 m/s
- Spray Width: 11 m
- Tank Capacity: 40 L
- Battery: DB1560 (29,000 mAh)
- Camera: DJI Zenmuse P1 (45MP)

### Auto-Flight Toggle
```bash
# Enable automatic flights
curl -X POST http://localhost:8000/api/v1/drone/toggle-auto-flight?drone_id=drone_001 \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# Disable automatic flights
curl -X POST http://localhost:8000/api/v1/drone/toggle-auto-flight?drone_id=drone_001 \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

### Log Flight
```bash
curl -X POST http://localhost:8000/api/v1/drone/log-flight \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-10-04T07:00:00Z",
    "duration": 28,
    "distance_covered": 4.2,
    "battery_used": 62,
    "images_captured": 203,
    "status": "success",
    "field_id": "field_001"
  }'
```

---

## Network Access

### Local Network URLs
- **Dashboard**: `http://192.168.1.100` (replace with your server IP)
- **API**: `http://192.168.1.100:8000`
- **API Docs**: `http://192.168.1.100:8000/docs`
- **Drone Page**: `http://192.168.1.100/drone`

### Finding Server IP
```bash
# Windows
ipconfig

# Linux/Mac
ip addr show
ifconfig
```

---

## Performance Tips

1. **Regular Maintenance**: Run `docker system prune -f` weekly
2. **Monitor Resources**: Use `docker stats` to check usage
3. **Backup Data**: Regular MongoDB backups to external drive
4. **Clean Old Data**: Archive data older than 90 days
5. **Restart Weekly**: Schedule server restarts for updates

---

## Quick Help

| Issue | Solution |
|-------|----------|
| Services won't start | `docker-compose down && docker-compose up -d --build` |
| No data | `python generate_dummy_data.py` |
| Can't access remotely | Check firewall and network settings |
| Slow performance | Restart: `docker-compose restart` |
| Database errors | Check MongoDB: `docker-compose logs mongodb` |

---

## Documentation Links

- **Main README**: [../README.md](../README.md)
- **Architecture**: [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Deployment**: [DEPLOYMENT.md](./DEPLOYMENT.md)
- **Drone Feature**: [DRONE_FEATURE.md](./DRONE_FEATURE.md)
- **Drone Quickstart**: [DRONE_QUICKSTART.md](./DRONE_QUICKSTART.md)
- **Backend Guide**: [BACKEND_GUIDE.md](./BACKEND_GUIDE.md)

