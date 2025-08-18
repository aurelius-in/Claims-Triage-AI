@echo off
echo 🚀 Claims Triage AI Demo Setup for Windows
echo =============================================

REM Check if Docker is running
echo Checking Docker status...
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)
echo ✅ Docker is running

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose not found. Please install Docker Compose.
    pause
    exit /b 1
)
echo ✅ Docker Compose is available

REM Build and start services
echo Building and starting services...
docker-compose up -d --build

REM Wait for services to be ready
echo Waiting for services to start (45 seconds)...
timeout /t 45 /nobreak >nul

REM Check service status
echo Checking service status...
docker-compose ps

REM Seed data
echo Seeding database with demo data...
docker-compose exec backend python -m backend.scripts.seed_data

echo.
echo 🎉 Demo Setup Complete!
echo ======================
echo Access your application at:
echo   Frontend UI: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo   Grafana: http://localhost:3001 (admin/admin)
echo   Prometheus: http://localhost:9090
echo.
echo Demo Credentials:
echo   Username: admin
echo   Password: admin123
echo.
echo Useful Commands:
echo   View logs: docker-compose logs -f
echo   Stop services: docker-compose down
echo   Restart: docker-compose restart
echo   Seed data: docker-compose exec backend python -m backend.scripts.seed_data
echo.
pause
