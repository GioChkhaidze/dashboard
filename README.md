# 🌾 Agricultural Dashboard - Complete Project

A modern, AI-powered agricultural dashboard for visualizing pest detection and canopy coverage data from drone imagery.

## 🏗️ Project Structure

```
dashboard/
├── backend/          # FastAPI backend
├── frontend/         # React + Vite frontend
├── docs/             # Documentation files
├── docker-compose.yml
├── docker-compose.dev.yml
├── generate_dummy_data.py
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local backend development)
- Node.js 18+ (for local frontend development)
- MongoDB 7.0+ (or use Docker)

### Option 1: Docker (Recommended)

```bash
# Development environment with hot reload
docker-compose -f docker-compose.dev.yml up

# Production environment
docker-compose up --build
```

Access the application:
- Frontend: http://localhost:80 (production) or http://localhost:5173 (dev)
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MongoDB: localhost:27017

### Option 2: Local Development

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Start MongoDB (using Docker)
docker run -d -p 27017:27017 --name mongodb mongo:7.0

# Run the API
python -m app.main
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Start development server
npm run dev
```

## 📊 Features

### ✅ Implemented

1. **Dashboard**
   - Today's KPI cards (Pest Count, Canopy Coverage)
   - Weekly trend charts
   - Active alerts banner
   - Quick statistics

2. **Heatmap View**
   - Interactive field visualization
   - Layer toggles (Pest/Canopy/Overlay)
   - Time slider for historical data

3. **Field Insights**
   - Zone-by-zone analysis
   - Health status per grid cell
   - Risk level indicators
   - Actionable recommendations

4. **Analytics**
   - Monthly comparisons and statistics
   - Multi-week trend analysis
   - Performance metrics and change indicators
   - Historical data visualization

5. **Drone Status** 🚁 ✨ NEW
   - **DJI AGRAS T50** monitoring with live image display
   - Real-time battery, GPS, and health status
   - Automatic flight scheduling with toggle controls
   - Interactive flight path visualization (predetermined zigzag pattern)
   - Comprehensive flight history with 30-day logs
   - **DJI Zenmuse P1** camera specifications (45MP Full-Frame)
   - Complete technical specs and maintenance schedule
   - DB1560 battery monitoring (29,000 mAh capacity)

6. **Backend API**
   - Data ingestion endpoints
   - Dashboard KPIs
   - Pest & Canopy data APIs
   - Insights & Alerts
   - Drone status & flight history APIs
   - MongoDB integration

### 🚧 To Be Enhanced

- Real-time WebSocket updates
- User authentication & authorization
- Multiple field support
- Advanced heatmap rendering (Canvas/D3.js)
- Export reports (PDF/CSV)
- Mobile app
- Weather integration
- Predictive analytics

## 📁 Architecture

### Backend (FastAPI)

```
backend/app/
├── api/v1/
│   ├── endpoints/       # API route handlers
│   │   ├── dashboard.py
│   │   ├── pests.py
│   │   ├── canopy.py
│   │   ├── insights.py
│   │   ├── alerts.py
│   │   ├── analytics.py
│   │   ├── drone.py     # Drone status & flights
│   │   └── ingestion.py
│   └── router.py        # Main router
├── models/              # MongoDB models (Beanie ODM)
│   ├── daily_data.py
│   ├── drone.py         # DroneStatus, FlightRecord
│   └── alert.py
├── utils/               # Heatmap & canopy utilities
├── core/                # Config & database
├── static/              # Static files (drone images)
└── main.py              # Application entry point
```

**Key Technologies:**
- FastAPI 0.104+ for REST API
- MongoDB with Beanie ODM (async)
- NumPy for data processing
- Pydantic v2 for validation
- Static file serving for drone images

### Frontend (React)

```
frontend/src/
├── components/          # Reusable UI components
├── pages/               # Page components
├── hooks/               # Custom React hooks
├── services/            # API client
└── App.jsx              # Main app
```

**Key Technologies:**
- React 18 with Hooks
- Vite for build tooling
- TailwindCSS for styling
- React Query for data fetching
- Recharts for visualizations
- React Router for routing

### Database (MongoDB)

**Collections:**
- `daily_data` - Daily field monitoring data
- `field_config` - Field configurations
- `alerts` - Active alerts and recommendations
- `weekly_aggregates` - Weekly statistical summaries
- `monthly_aggregates` - Monthly statistical summaries
- `drone_status` - DJI AGRAS T50 status and health metrics
- `flight_records` - Historical flight logs and telemetry

## 🔌 API Endpoints

### Ingestion
- `POST /api/v1/ingestion/daily` - Ingest daily drone data
- `GET /api/v1/ingestion/status/{field_id}` - Get ingestion status

### Dashboard
- `GET /api/v1/dashboard/kpis/today` - Today's KPIs
- `GET /api/v1/dashboard/kpis/weekly` - Weekly KPIs

### Pests
- `GET /api/v1/pests/daily` - Daily pest data
- `GET /api/v1/pests/trend` - Pest trend over time

### Canopy
- `GET /api/v1/canopy/daily` - Daily canopy data
- `GET /api/v1/canopy/trend` - Canopy trend over time

### Insights
- `GET /api/v1/insights/zones` - Zone-by-zone insights

### Alerts
- `GET /api/v1/alerts/active` - Active alerts
- `POST /api/v1/alerts/acknowledge/{alert_id}` - Acknowledge alert

### Analytics
- `GET /api/v1/analytics/monthly` - Monthly analytics

### Drone 🚁
- `GET /api/v1/drone/status` - Get drone status and flight history
- `POST /api/v1/drone/log-flight` - Log a completed flight
- `POST /api/v1/drone/update-status` - Update drone battery/health status
- `POST /api/v1/drone/toggle-auto-flight` - Enable/disable automatic flights
- `POST /api/v1/drone/upgrade-to-t50` - Upgrade drone to DJI AGRAS T50 specs

## 🎲 Test Data Generation

The project includes an interactive dummy data generator for testing and development.

### Quick Start

```bash
python generate_dummy_data.py
```

### Interactive Options

When you run the generator, you'll be prompted:

```
⚠️  Database Cleanup Options:
   1. Clear all existing data (daily data + alerts)
   2. Keep existing data and add new data
   3. Cancel operation
```

**Option 1 - Fresh Start:**
- Deletes all existing daily data and alerts
- Generates 15 days of fresh, realistic test data
- Perfect for clean slate testing

**Option 2 - Incremental:**
- Keeps existing data
- Adds/updates data for the last 15 days
- Good for testing trends over time

**Option 3 - Cancel:**
- Exits without making changes

### Generated Data

The generator creates realistic agricultural data:
- **50×50 pest density heatmaps** with crop-specific infestations
- **50×50 canopy coverage grids** with stress zones
- **Multi-crop fields** (wheat, corn)
- **Pest hotspots** with gaussian distribution patterns
- **Canopy stress patches** simulating irrigation issues
- **Drone flight records** with realistic telemetry data
- **Recommendation alerts** (5-290 per day based on field conditions)

### Alert Types Generated

1. **Critical Pest Outbreaks** (≥10 pests/cell)
2. **Pest Warnings** (5-9 pests/cell)
3. **Irrigation Alerts** (canopy <50%)
4. **Combined Risk** (high pests + low canopy)
5. **Crop-Specific Outbreaks** (field-wide patterns)

### Automated Usage

For scripts and CI/CD:

```bash
# Clear and generate
Write-Output "1" | python generate_dummy_data.py

# Add to existing
Write-Output "2" | python generate_dummy_data.py
```

## 🧪 Testing

### Backend

```bash
cd backend
pytest tests/ -v
```

### Frontend

```bash
cd frontend
npm run lint
npm run build
```

## 🚢 Deployment

### Using Docker

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Variables

**Backend (.env):**
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=agri_dashboard
DEBUG=False
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
SECRET_KEY=your-secret-key
```

**Frontend (.env):**
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=Agricultural Dashboard
```

## 📖 Documentation

- [Architecture Documentation](./docs/ARCHITECTURE.md) - System design & schemas
- [Backend Guide](./docs/BACKEND_GUIDE.md) - Backend implementation details
- [Deployment Guide](./docs/DEPLOYMENT.md) - Production deployment
- [Drone Feature Guide](./docs/DRONE_FEATURE.md) - DJI AGRAS T50 integration
- [File Structure](./docs/FILE_STRUCTURE.md) - Project organization
- [Alert System](./docs/ALERT_SYSTEM.md) - Alert generation logic
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built for farmers and agronomists
- Powered by AI-driven insights
- Designed with ❤️ for sustainable agriculture

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Email: support@agridashboard.com
- Documentation: [docs.agridashboard.com](https://docs.agridashboard.com)

---

**Built with** 🌱 **for a greener future**
