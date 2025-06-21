# AKF3 Development Server Startup Script
# Starts both backend (FastAPI) and frontend (Next.js) with API integration

Write-Host "Starting AKF3 Universal Knowledge Graph Development Environment" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan

# Check if required ports are available
$backendPort = 8000
$frontendPort = 3000

Write-Host "Checking port availability..." -ForegroundColor Yellow

# Check backend port
$backendProcess = Get-NetTCPConnection -LocalPort $backendPort -ErrorAction SilentlyContinue
if ($backendProcess) {
    Write-Host "WARNING: Port $backendPort is already in use. Attempting to free it..." -ForegroundColor Yellow
    Stop-Process -Id $backendProcess.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# Check frontend port
$frontendProcess = Get-NetTCPConnection -LocalPort $frontendPort -ErrorAction SilentlyContinue
if ($frontendProcess) {
    Write-Host "WARNING: Port $frontendPort is already in use. Attempting to free it..." -ForegroundColor Yellow
    Stop-Process -Id $frontendProcess.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

Write-Host "SUCCESS: Ports are ready!" -ForegroundColor Green

# Set environment variables
$env:PYTHONPATH = $PWD
$env:NEXT_PUBLIC_API_URL = "http://localhost:8000"

Write-Host "Environment configured:" -ForegroundColor Blue
Write-Host "   PYTHONPATH: $env:PYTHONPATH" -ForegroundColor Gray
Write-Host "   API_URL: $env:NEXT_PUBLIC_API_URL" -ForegroundColor Gray

# Start backend server
Write-Host "Starting FastAPI Backend Server (Port $backendPort)..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    $env:PYTHONPATH = $using:PWD
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
} -Name "AKF3-Backend"

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend server
Write-Host "Starting Next.js Frontend Server (Port $frontendPort)..." -ForegroundColor Blue
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD/frontend
    $env:NEXT_PUBLIC_API_URL = $using:env:NEXT_PUBLIC_API_URL
    npm run dev
} -Name "AKF3-Frontend"

# Wait for servers to initialize
Write-Host "Initializing servers..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "SUCCESS: AKF3 Development Environment is Ready!" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "Backend API:     http://localhost:$backendPort" -ForegroundColor White
Write-Host "API Docs:        http://localhost:$backendPort/docs" -ForegroundColor White
Write-Host "Frontend App:    http://localhost:$frontendPort" -ForegroundColor White
Write-Host ""
Write-Host "Features Available:" -ForegroundColor Yellow
Write-Host "   * 87 UKG Pillar Levels" -ForegroundColor Green
Write-Host "   * 13 Mathematical Axes" -ForegroundColor Green
Write-Host "   * Knowledge Graph Visualization" -ForegroundColor Green
Write-Host "   * AI-Powered Agent System" -ForegroundColor Green
Write-Host "   * Real-time API Integration" -ForegroundColor Green
Write-Host "   * Gemini AI Integration (when configured)" -ForegroundColor Green
Write-Host ""
Write-Host "AI Configuration:" -ForegroundColor Magenta
Write-Host "   To enable Gemini AI, set: " -NoNewline -ForegroundColor Gray
Write-Host "GEMINI_API_KEY=your_key" -ForegroundColor White
Write-Host ""
Write-Host "Logs:" -ForegroundColor Yellow
Write-Host "   Backend: " -NoNewline -ForegroundColor Gray
Write-Host "Receive-Job AKF3-Backend" -ForegroundColor White
Write-Host "   Frontend: " -NoNewline -ForegroundColor Gray
Write-Host "Receive-Job AKF3-Frontend" -ForegroundColor White
Write-Host ""
Write-Host "To stop servers: " -NoNewline -ForegroundColor Red
Write-Host "Stop-Job AKF3-Backend,AKF3-Frontend; Remove-Job AKF3-Backend,AKF3-Frontend" -ForegroundColor White
Write-Host ""

# Monitor jobs
Write-Host "Monitoring servers... (Press Ctrl+C to stop)" -ForegroundColor Cyan

try {
    while ($true) {
        $backendState = (Get-Job -Name "AKF3-Backend").State
        $frontendState = (Get-Job -Name "AKF3-Frontend").State
        
        Write-Host "Backend: $backendState | Frontend: $frontendState" -ForegroundColor Gray
        
        if ($backendState -eq "Failed" -or $frontendState -eq "Failed") {
            Write-Host "ERROR: One or more servers failed!" -ForegroundColor Red
            break
        }
        
        Start-Sleep -Seconds 10
    }
}
catch {
    Write-Host "Stopping servers..." -ForegroundColor Yellow
}
finally {
    Stop-Job -Name "AKF3-Backend","AKF3-Frontend" -ErrorAction SilentlyContinue
    Remove-Job -Name "AKF3-Backend","AKF3-Frontend" -ErrorAction SilentlyContinue
    Write-Host "Servers stopped." -ForegroundColor Green
} 