# PowerShell script to start all microservices manually
# Windows PowerShell script

Write-Host "🚀 Starting VPBank Microservices..." -ForegroundColor Green

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found! Please create .env file first." -ForegroundColor Red
    exit 1
}

# Set environment variables
$env:TASK_QUEUE_SERVICE_URL = "http://localhost:7862"

Write-Host ""
Write-Host "📋 Services will start in separate windows:" -ForegroundColor Yellow
Write-Host "   1. Task Queue Service (port 7862)"
Write-Host "   2. Voice Bot Service (port 7860)"
Write-Host "   3. Browser Worker Service (background)"
Write-Host ""

# Start Task Queue Service
Write-Host "🌐 Starting Task Queue Service..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\activate; python services/task_queue_service/main.py"
Start-Sleep -Seconds 3

# Start Voice Bot Service
Write-Host "🎤 Starting Voice Bot Service..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\activate; `$env:TASK_QUEUE_SERVICE_URL='http://localhost:7862'; python main_voice.py"
Start-Sleep -Seconds 2

# Start Browser Worker Service
Write-Host "🔨 Starting Browser Worker Service..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\activate; `$env:TASK_QUEUE_SERVICE_URL='http://localhost:7862'; python main_worker.py"

Write-Host ""
Write-Host "✅ All services started!" -ForegroundColor Green
Write-Host "📝 Check the 3 PowerShell windows for logs" -ForegroundColor Yellow
Write-Host ""
Write-Host "🌐 Access points:" -ForegroundColor Cyan
Write-Host "   - Voice Bot: http://localhost:7860"
Write-Host "   - Task Queue API: http://localhost:7862/api/health"
Write-Host ""

