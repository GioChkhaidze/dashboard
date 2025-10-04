# 🚀 Deployment & Setup Checklist

## Pre-Deployment Checklist

### ✅ Backend Setup
- [ ] MongoDB instance ready (local/cloud)
- [ ] Environment variables configured
- [ ] Python 3.11+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [x] Database indexes created
- [ ] API endpoints tested

### ✅ Frontend Setup
- [ ] Node.js 18+ installed
- [ ] Dependencies installed (`npm install`)
- [ ] Environment variables configured
- [ ] Build tested (`npm run build`)
- [ ] API base URL configured

### ✅ Infrastructure
- [ ] Docker installed
- [ ] Docker Compose installed
- [ ] Network ports available (80, 8000, 27017)
- [ ] SSL certificates (for production)
- [ ] Domain name configured (for production)

---

## 🏃 Quick Start Guide

### Option 1: Development with Docker (Recommended for Testing)

```powershell
# Clone or navigate to project
cd c:\Users\George\Desktop\work\reboottheearth\dashboard

# Start all services with hot reload
docker-compose -f docker-compose.dev.yml up

# Access:
# - Frontend: http://localhost:5173
# - Backend: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - MongoDB: localhost:27017
```

**Stopping Services:**
```powershell
docker-compose -f docker-compose.dev.yml down
```

---

### Option 2: Production with Docker

```powershell
# Build and start production containers
docker-compose up -d --build

# View logs
docker-compose logs -f

# Access:
# - Frontend: http://localhost
# - Backend: http://localhost:8000
```

**Managing Services:**
```powershell
# Stop services
docker-compose down

# Restart services
docker-compose restart

# View service status
docker-compose ps
```

---

### Option 3: Local Development (Without Docker)

#### Step 1: Start MongoDB

```powershell
# Using Docker for MongoDB only
docker run -d -p 27017:27017 --name mongodb mongo:7.0

# Or install MongoDB locally and start service
```

#### Step 2: Start Backend

```powershell
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# Run the API
python -m app.main
```

Backend will be available at http://localhost:8000

#### Step 3: Start Frontend

```powershell
cd frontend

# Install dependencies
npm install

# Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# Start dev server
npm run dev
```

Frontend will be available at http://localhost:5173

---

## 🔧 Configuration

### Backend Environment Variables

Create `backend/.env`:

```env
# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=agri_dashboard

# API
API_V1_PREFIX=/api/v1
PROJECT_NAME=Agricultural Dashboard API
DEBUG=True

# Security
SECRET_KEY=change-this-to-a-random-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Thresholds
DEFAULT_GRID_SIZE=1.0
PEST_DENSITY_WARNING_THRESHOLD=5.0
PEST_DENSITY_CRITICAL_THRESHOLD=10.0
CANOPY_WARNING_THRESHOLD=60.0
CANOPY_CRITICAL_THRESHOLD=50.0

# Logging
LOG_LEVEL=INFO
```

### Frontend Environment Variables

Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=Agricultural Dashboard
```

---

## 📊 Initial Data Setup

### Option 1: Using API Endpoint (Recommended)

```powershell
# Create a sample data file: sample_data.json
{
  "field_id": "field_001",
  "bounding_boxes": [
    [125, 340, 50, 50],
    [680, 120, 45, 48],
    [340, 560, 52, 49]
  ],
  "canopy_cover": [
    [72.5, 68.3, 75.1, 82.0],
    [70.2, 65.8, 71.5, 78.3],
    [68.9, 64.2, 69.5, 76.1],
    [71.3, 67.5, 73.2, 80.5]
  ],
  "field_dimensions": {
    "width_m": 50,
    "height_m": 50,
    "grid_resolution": 1.0
  }
}

# Send data via curl or PowerShell
curl -X POST http://localhost:8000/api/v1/ingestion/daily `
  -H "Content-Type: application/json" `
  -d "@sample_data.json"
```

### Option 2: Using Python Script

Create `backend/scripts/seed_data.py`:

```python
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import init_db, close_db
from app.models.daily_data import DailyData
from app.models.field_config import FieldConfig
from datetime import datetime
import numpy as np

async def seed_data():
    await init_db()
    
    # Create field configuration
    field_config = FieldConfig(
        field_id="field_001",
        name="North Field",
        location={
            "coordinates": [34.0522, -118.2437],
            "address": "Sample Farm"
        },
        dimensions={
            "width_m": 100,
            "height_m": 80,
            "area_hectares": 0.8
        },
        grid_config={
            "cell_size_m": 1.0,
            "grid_width": 100,
            "grid_height": 80
        },
        thresholds={
            "pest_density_warning": 5.0,
            "pest_density_critical": 10.0,
            "canopy_warning": 60.0,
            "canopy_critical": 50.0
        },
        crop_type="corn",
        planting_date="2025-04-15",
        expected_harvest="2025-11-01"
    )
    
    await field_config.insert()
    print("✅ Field configuration created")
    
    # Generate sample daily data for last 7 days
    for days_ago in range(7, 0, -1):
        date = datetime.utcnow() - timedelta(days=days_ago)
        date_str = date.strftime("%Y-%m-%d")
        
        # Generate random data
        num_pests = np.random.randint(300, 400)
        bboxes = [[float(np.random.randint(0, 1000)), 
                   float(np.random.randint(0, 800)), 
                   50.0, 50.0] for _ in range(num_pests)]
        
        canopy = np.random.uniform(60, 85, (80, 100)).tolist()
        
        daily_data = DailyData(
            field_id="field_001",
            date=date_str,
            timestamp=date,
            bounding_boxes=bboxes,
            canopy_cover=canopy,
            field_dimensions={
                "width_m": 100,
                "height_m": 80,
                "grid_resolution": 1.0
            },
            aggregates={
                "pest_count": num_pests,
                "avg_canopy": float(np.mean(canopy)),
                "min_canopy": float(np.min(canopy)),
                "max_canopy": float(np.max(canopy))
            }
        )
        
        await daily_data.insert()
        print(f"✅ Created data for {date_str}")
    
    await close_db()
    print("✅ Seed data completed!")

if __name__ == "__main__":
    asyncio.run(seed_data())
```

Run seeding:
```powershell
cd backend
python scripts/seed_data.py
```

---

## 🧪 Testing the Deployment

### 1. Health Checks

```powershell
# Backend health
curl http://localhost:8000/health

# Expected: {"status":"healthy","service":"agri-dashboard-api"}

# MongoDB connection
curl http://localhost:8000/api/v1/ingestion/status/field_001
```

### 2. API Documentation

Visit http://localhost:8000/docs to see interactive API documentation (Swagger UI)

### 3. Frontend Access

Visit http://localhost:5173 (dev) or http://localhost (production)

You should see:
- Dashboard with KPI cards
- Navigation menu
- Charts (may show "No data" until you ingest data)

---

## 🐛 Troubleshooting

### Backend Issues

**Problem: Module not found errors**
```powershell
# Solution: Reinstall dependencies
cd backend
pip install --force-reinstall -r requirements.txt
```

**Problem: MongoDB connection failed**
```powershell
# Solution: Check MongoDB is running
docker ps | Select-String mongodb

# If not running, start it
docker start mongodb
# Or
docker run -d -p 27017:27017 --name mongodb mongo:7.0
```

**Problem: Port 8000 already in use**
```powershell
# Solution: Find and kill process
netstat -ano | Select-String "8000"
# Note the PID and kill it
Stop-Process -Id <PID> -Force
```

### Frontend Issues

**Problem: CORS errors**
```powershell
# Solution: Check backend CORS_ORIGINS includes frontend URL
# In backend/.env:
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Problem: API calls failing**
```powershell
# Solution: Check VITE_API_BASE_URL in frontend/.env
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Restart frontend after changing .env
npm run dev
```

**Problem: Build fails**
```powershell
# Solution: Clear cache and rebuild
cd frontend
rm -rf node_modules
rm package-lock.json
npm install
npm run build
```

### Docker Issues

**Problem: Container won't start**
```powershell
# Solution: Check logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild containers
docker-compose down
docker-compose up --build
```

**Problem: Permission issues**
```powershell
# Solution: Run Docker as administrator or fix volume permissions
```

---

## 📈 Performance Optimization

### Backend
- [ ] Enable database indexes
- [ ] Configure connection pooling
- [ ] Add Redis caching
- [ ] Enable gzip compression
- [ ] Implement rate limiting

### Frontend
- [ ] Enable code splitting
- [ ] Optimize images
- [ ] Use CDN for assets
- [ ] Enable service worker
- [ ] Implement lazy loading

### Database
- [ ] Create compound indexes
- [ ] Enable query profiling
- [ ] Configure replica sets
- [ ] Implement backup strategy

---

## 🔒 Security Checklist (Production)

- [ ] Change default SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Enable authentication
- [ ] Implement rate limiting
- [ ] Use environment secrets (not .env files)
- [ ] Regular security updates
- [ ] Enable audit logging
- [ ] Implement RBAC
- [ ] Regular backups

---

## 📞 Support & Resources

- **Documentation**: See ARCHITECTURE.md, BACKEND_GUIDE.md, UX_DESIGN.md
- **API Docs**: http://localhost:8000/docs
- **GitHub Issues**: Report bugs and feature requests
- **Email**: support@agridashboard.com

---

## ✅ Final Checklist

### Development Ready
- [ ] MongoDB running
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Can access API docs
- [ ] Can view dashboard
- [ ] Sample data loaded

### Production Ready
- [ ] Environment variables secured
- [ ] SSL certificates installed
- [ ] Domain configured
- [ ] Database backed up
- [ ] Monitoring enabled
- [ ] CI/CD pipeline working
- [ ] Load testing completed
- [ ] Security audit passed

---

**🎉 Your Agricultural Dashboard is now ready to use!**

For farmers, by developers, powered by AI. 🌱
