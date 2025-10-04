# 🌾 Agricultural Dashboard - Start Script

Write-Host "🌾 Agricultural Dashboard - Quick Start" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check Docker installation
Write-Host "Checking Docker installation..." -ForegroundColor Yellow
$dockerInstalled = Get-Command docker -ErrorAction SilentlyContinue

if (-not $dockerInstalled) {
    Write-Host "❌ Docker is not installed!" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Docker is installed" -ForegroundColor Green
Write-Host ""

# Check Docker Compose
Write-Host "Checking Docker Compose..." -ForegroundColor Yellow
$composeInstalled = Get-Command docker-compose -ErrorAction SilentlyContinue

if (-not $composeInstalled) {
    Write-Host "❌ Docker Compose is not installed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Docker Compose is installed" -ForegroundColor Green
Write-Host ""

# Ask user which environment
Write-Host "Select environment:" -ForegroundColor Cyan
Write-Host "1. Development (with hot reload) - Recommended for testing"
Write-Host "2. Production (optimized build)"
Write-Host "3. Exit"
Write-Host ""

$choice = Read-Host "Enter choice (1, 2, or 3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🚀 Starting Development Environment..." -ForegroundColor Green
        Write-Host ""
        
        # Check if .env files exist
        if (-not (Test-Path "backend\.env")) {
            Write-Host "Creating backend/.env from template..." -ForegroundColor Yellow
            Copy-Item "backend\.env.example" "backend\.env"
        }
        
        if (-not (Test-Path "frontend\.env")) {
            Write-Host "Creating frontend/.env from template..." -ForegroundColor Yellow
            Copy-Item "frontend\.env.example" "frontend\.env"
        }
        
        Write-Host ""
        Write-Host "Starting services with Docker Compose..." -ForegroundColor Yellow
        docker-compose -f docker-compose.dev.yml up
        
        Write-Host ""
        Write-Host "✅ Services started!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Access the application at:" -ForegroundColor Cyan
        Write-Host "  Frontend:  http://localhost:5173" -ForegroundColor White
        Write-Host "  Backend:   http://localhost:8000" -ForegroundColor White
        Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor White
        Write-Host ""
        Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
    }
    "2" {
        Write-Host ""
        Write-Host "🚀 Starting Production Environment..." -ForegroundColor Green
        Write-Host ""
        
        # Check if .env files exist
        if (-not (Test-Path "backend\.env")) {
            Write-Host "Creating backend/.env from template..." -ForegroundColor Yellow
            Copy-Item "backend\.env.example" "backend\.env"
            Write-Host "⚠️  Please edit backend/.env with production settings!" -ForegroundColor Yellow
        }
        
        if (-not (Test-Path "frontend\.env")) {
            Write-Host "Creating frontend/.env from template..." -ForegroundColor Yellow
            Copy-Item "frontend\.env.example" "frontend\.env"
        }
        
        Write-Host ""
        Write-Host "Building and starting services..." -ForegroundColor Yellow
        docker-compose up -d --build
        
        Write-Host ""
        Write-Host "✅ Services started in background!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Access the application at:" -ForegroundColor Cyan
        Write-Host "  Frontend:  http://localhost" -ForegroundColor White
        Write-Host "  Backend:   http://localhost:8000" -ForegroundColor White
        Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor White
        Write-Host ""
        Write-Host "Commands:" -ForegroundColor Yellow
        Write-Host "  View logs:    docker-compose logs -f" -ForegroundColor White
        Write-Host "  Stop:         docker-compose down" -ForegroundColor White
        Write-Host "  Restart:      docker-compose restart" -ForegroundColor White
    }
    "3" {
        Write-Host "Goodbye! 👋" -ForegroundColor Green
        exit 0
    }
    default {
        Write-Host "Invalid choice. Please run the script again." -ForegroundColor Red
        exit 1
    }
}
