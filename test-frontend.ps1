# Frontend Connectivity Test
Write-Host "🔍 Testing Frontend Connectivity" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Green

# Test if port 3000 is accessible
Write-Host "Testing localhost:3000..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 10
    Write-Host "✅ Frontend is responding (Status: $($response.StatusCode))" -ForegroundColor Green
    Write-Host "Content-Type: $($response.Headers.'Content-Type')" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Frontend is not accessible: $($_.Exception.Message)" -ForegroundColor Red
}

# Test if port 8000 is accessible
Write-Host "`nTesting localhost:8000 (Backend)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 10
    Write-Host "✅ Backend is responding (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend is not accessible: $($_.Exception.Message)" -ForegroundColor Red
}

# Check if containers are running
Write-Host "`nChecking container status..." -ForegroundColor Yellow
docker-compose -f docker-compose.demo.yml ps

Write-Host "`n🌐 Frontend URLs to try:" -ForegroundColor Green
Write-Host "   http://localhost:3000" -ForegroundColor Cyan
Write-Host "   http://127.0.0.1:3000" -ForegroundColor Cyan
Write-Host "   http://[::1]:3000" -ForegroundColor Cyan

Write-Host "`n🔧 Troubleshooting steps:" -ForegroundColor Yellow
Write-Host "1. Try refreshing the page with Ctrl+F5" -ForegroundColor White
Write-Host "2. Open in an incognito/private browser window" -ForegroundColor White
Write-Host "3. Try a different browser (Chrome, Firefox, Edge)" -ForegroundColor White
Write-Host "4. Check if your antivirus/firewall is blocking port 3000" -ForegroundColor White
Write-Host "5. Try accessing http://127.0.0.1:3000 instead of localhost:3000" -ForegroundColor White
