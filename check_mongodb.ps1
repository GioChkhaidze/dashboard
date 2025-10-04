# MongoDB Database Checker
# Quick script to check MongoDB contents

Write-Host "`n=== MongoDB Database Inspector ===" -ForegroundColor Cyan

# Check if MongoDB container is running (try dev first, then production)
$mongoContainer = $null
$mongoStatus = docker ps --filter "name=agri-mongodb-dev" --format "{{.Status}}"
if ($mongoStatus) {
    $mongoContainer = "agri-mongodb-dev"
    Write-Host "[OK] MongoDB DEV container is running" -ForegroundColor Green
} else {
    $mongoStatus = docker ps --filter "name=agri-mongodb" --format "{{.Status}}"
    if ($mongoStatus) {
        $mongoContainer = "agri-mongodb"
        Write-Host "[OK] MongoDB PRODUCTION container is running" -ForegroundColor Green
    } else {
        Write-Host "`n[ERROR] MongoDB container is not running!" -ForegroundColor Red
        Write-Host "Start dev with: docker-compose -f docker-compose.dev.yml up -d" -ForegroundColor Yellow
        Write-Host "Start prod with: docker-compose up -d" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "Container: $mongoContainer" -ForegroundColor Gray
Write-Host "Status: $mongoStatus`n" -ForegroundColor Gray

# Check collections
Write-Host "Collections in 'agri_dashboard' database:" -ForegroundColor Cyan
docker exec $mongoContainer mongosh agri_dashboard --quiet --eval "printjson(db.getCollectionNames())"

Write-Host "`nDocument counts:" -ForegroundColor Cyan
docker exec $mongoContainer mongosh agri_dashboard --quiet --eval @"
print('daily_data: ' + db.daily_data.countDocuments());
print('field_config: ' + db.field_config.countDocuments());
print('alerts: ' + db.alerts.countDocuments());
print('weekly_aggregates: ' + db.weekly_aggregates.countDocuments());
print('monthly_aggregates: ' + db.monthly_aggregates.countDocuments());
"@

Write-Host "`n=== Database Location ===" -ForegroundColor Cyan
Write-Host "Container path: /data/db" -ForegroundColor Gray
Write-Host "Docker volume: dashboard_mongodb_data" -ForegroundColor Gray
Write-Host "Connection string: mongodb://localhost:27017" -ForegroundColor Gray

Write-Host "`n=== Quick Commands ===" -ForegroundColor Cyan
Write-Host "1. Open MongoDB shell:" -ForegroundColor Yellow
Write-Host "   docker exec -it $mongoContainer mongosh agri_dashboard`n" -ForegroundColor Gray

Write-Host "2. View specific collection:" -ForegroundColor Yellow
Write-Host "   docker exec $mongoContainer mongosh agri_dashboard --eval 'db.daily_data.find().limit(1).pretty()'`n" -ForegroundColor Gray

Write-Host "3. Connect with MongoDB Compass (GUI):" -ForegroundColor Yellow
Write-Host "   Download: https://www.mongodb.com/try/download/compass" -ForegroundColor Gray
Write-Host "   Connection: mongodb://localhost:27017`n" -ForegroundColor Gray

Write-Host "4. View API documentation:" -ForegroundColor Yellow
Write-Host "   http://localhost:8000/docs`n" -ForegroundColor Gray
