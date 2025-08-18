# Quick Demo Setup for Claims Triage AI
Write-Host "🚀 Quick Demo Setup - Claims Triage AI" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Check Docker
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Start essential services only
Write-Host "Starting essential services..." -ForegroundColor Yellow
docker-compose -f docker-compose.demo.yml up -d postgres redis

Write-Host "Waiting for database to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "Starting backend..." -ForegroundColor Yellow
docker-compose -f docker-compose.demo.yml up -d backend

Write-Host "Waiting for backend to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "Starting frontend..." -ForegroundColor Yellow
docker-compose -f docker-compose.demo.yml up -d frontend

Write-Host "Waiting for frontend to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# Check status
Write-Host "Checking service status..." -ForegroundColor Yellow
docker-compose -f docker-compose.demo.yml ps

Write-Host ""
Write-Host "🎉 Quick Demo Setup Complete!" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green
Write-Host "Access your application at:" -ForegroundColor Cyan
Write-Host "  Frontend UI: http://localhost:3000" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Demo Credentials:" -ForegroundColor Cyan
Write-Host "  Username: admin" -ForegroundColor White
Write-Host "  Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor Cyan
Write-Host "  View logs: docker-compose -f docker-compose.demo.yml logs -f" -ForegroundColor White
Write-Host "  Stop services: docker-compose -f docker-compose.demo.yml down" -ForegroundColor White
Write-Host "  Restart: docker-compose -f docker-compose.demo.yml restart" -ForegroundColor White
