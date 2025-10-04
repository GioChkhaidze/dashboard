# 🚁 Quick Start - DJI AGRAS T50 Drone Feature

## What's Included

### Frontend
- `DroneDetailsPage.jsx` - Complete drone monitoring dashboard
- `FlightPathMap.jsx` - Interactive flight path visualization
- Four tabs: Overview, Camera/Sensors, Flight History, Specifications
- Auto-flight scheduling toggle button

### Backend
- `/api/v1/drone/status` - Get drone status & flights
- `/api/v1/drone/log-flight` - Log completed flight
- `/api/v1/drone/toggle-auto-flight` - Enable/disable scheduling
- `/api/v1/drone/upgrade-to-t50` - Initialize/upgrade to T50 specs

### Data Models
- `DroneStatus` - DJI AGRAS T50 status & specifications
- `FlightRecord` - Flight logs with stats

## Quick Test (3 Steps)

### 1. Start Services

```bash
# Using Docker (recommended)
docker-compose -f docker-compose.dev.yml up -d

# OR start locally
cd backend && python -m app.main
```

### 2. Generate Data

```bash
python generate_dummy_data.py
```

Enter `1` to clear and generate fresh data.

Expected output:
```
🚁 Generating drone status and flight history...
   Upgrading drone to DJI AGRAS T50 specifications...
   ✅ Drone upgraded to DJI AGRAS T50
✅ Drone status updated with 13 flight records
```

### 3. View Dashboard

```bash
cd frontend && npm run dev
```

Open: `http://localhost:5173/drone`

## What You'll See

### Header
- Blue banner: "🚁 Drone Status & Details"
- Health badge (Excellent/Good/Fair)
- **Toggle button** (Red: "Disable Auto Flights" / Green: "Enable Auto Flights")
- Next scheduled flight time (when enabled)
- Warning banner (when disabled)

### Quick Status Cards
- Battery Level (85%) with color gauge
- Total Flight Time (6.4h)
- Last Flight Distance (3.8 km)
- Total Flights (13)

### Overview Tab
- DJI AGRAS T50 image
- Model: DJI AGRAS T50, Serial: T50-2024-001, Firmware: v3.2.1
- Current status cards (Operational, Maintenance, GPS)
- Health metrics with progress bars
- **Flight Path Map** - Interactive SVG showing zigzag pattern

### Camera & Sensors Tab
- DJI Zenmuse P1 specs (45MP, 3-axis gimbal)
- AI systems with accuracy percentages

### Flight History Tab
- Table of 10 recent flights
- Date, duration, distance, battery, images, status

### Specifications Tab
- T50 technical specs (47.5kg, 10m/s, 11m spray width)
- DB1560 battery specs (29,000 mAh, 10min fast charge)
- Maintenance checklist

## Testing Auto-Flight Toggle

1. Click **"Disable Auto Flights"** button
   - Button turns green
   - Warning banner appears
   - Next flight info disappears

2. Click **"Enable Auto Flights"** button
   - Button turns red
   - Next scheduled flight shows (tomorrow 7:00 AM)
   - Warning banner disappears

## API Testing

```bash
# Get drone status
curl http://localhost:8000/api/v1/drone/status?drone_id=drone_001

# Toggle auto-flight (enable)
curl -X POST http://localhost:8000/api/v1/drone/toggle-auto-flight?drone_id=drone_001 \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# Upgrade to T50 specs
curl -X POST http://localhost:8000/api/v1/drone/upgrade-to-t50?drone_id=drone_001
```

## Troubleshooting

**Image not showing?**
- Check `backend/static/drone.png` exists
- Verify backend is running on port 8000
- Check browser console for errors

**No flight data?**
- Run `python generate_dummy_data.py` again
- Choose option 1 to clear and regenerate

**Statistics showing 0?**
- Backend automatically calculates from flight records
- Restart backend if just updated code
- Check MongoDB has `flight_records` collection

**Auto-flight toggle not working?**
- Check browser console for errors
- Verify backend endpoint returns 200
- Check network tab in DevTools

## Key Files

```
backend/
├── app/models/drone.py              # DroneStatus, FlightRecord models
├── app/api/v1/endpoints/drone.py    # All drone endpoints
└── static/drone.png                  # DJI AGRAS T50 image

frontend/
├── src/pages/DroneDetailsPage.jsx   # Main drone page
├── src/components/drone/
│   └── FlightPathMap.jsx            # Flight path visualization
├── src/hooks/useApi.js              # useDroneStatus hook
└── src/services/api.js              # droneAPI functions
```

## Next Steps

- Review [DRONE_FEATURE.md](./DRONE_FEATURE.md) for detailed documentation
- Check [DEPLOYMENT.md](./DEPLOYMENT.md) for production setup
- See main [README.md](../README.md) for full project info

