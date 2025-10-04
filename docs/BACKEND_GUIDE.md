# Backend API Implementation Guide

## 📁 Complete Backend Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Settings and configuration
│   │   └── database.py         # MongoDB connection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── daily_data.py       # Daily data model
│   │   ├── field_config.py     # Field configuration model
│   │   ├── alert.py            # Alert model
│   │   ├── weekly_aggregate.py # Weekly stats model
│   │   └── monthly_aggregate.py# Monthly stats model
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py       # Main API router
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── ingestion.py   # Data ingestion
│   │           ├── dashboard.py   # Dashboard KPIs
│   │           ├── pests.py       # Pest endpoints
│   │           ├── canopy.py      # Canopy endpoints
│   │           ├── insights.py    # Field insights
│   │           ├── alerts.py      # Alerts
│   │           └── analytics.py   # Analytics
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── heatmap.py          # Heatmap utilities
│   │   └── canopy.py           # Canopy processing
│   └── services/
│       ├── __init__.py
│       └── aggregation.py      # Data aggregation service
├── tests/
│   ├── __init__.py
│   ├── test_heatmap.py
│   └── test_api.py
├── requirements.txt
├── .env.example
├── Dockerfile
└── README.md
```

## 🚀 Running the Backend

### 1. Setup Python Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```powershell
# Copy example env file
cp .env.example .env

# Edit .env with your MongoDB connection
# MONGODB_URL=mongodb://localhost:27017
```

### 3. Start MongoDB

```powershell
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or use MongoDB Atlas (cloud)
```

### 4. Run the API

```powershell
# Development mode (with auto-reload)
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access API Documentation

```
http://localhost:8000/docs        # Swagger UI
http://localhost:8000/redoc       # ReDoc
http://localhost:8000/health      # Health check
```
