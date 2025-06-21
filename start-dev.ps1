#!/usr/bin/env pwsh
# AKF3 Development Server Startup Script
# This script starts both the FastAPI backend and Next.js frontend

Write-Host "🚀 Starting AKF3 Development Servers..." -ForegroundColor Green
Write-Host ""

# Function to check if a port is in use
function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

# Check if ports are available
$backendPort = 8000
$frontendPort = 3000

if (Test-Port $backendPort) {
    Write-Host "⚠️  Port $backendPort is already in use. Backend might already be running." -ForegroundColor Yellow
}

if (Test-Port $frontendPort) {
    Write-Host "⚠️  Port $frontendPort is already in use. Frontend might already be running." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📊 Backend API will be available at: http://localhost:$backendPort" -ForegroundColor Cyan
Write-Host "🌐 Frontend will be available at: http://localhost:$frontendPort" -ForegroundColor Cyan
Write-Host "📚 API Documentation at: http://localhost:$backendPort/docs" -ForegroundColor Cyan
Write-Host ""

# Start backend in a new PowerShell window
Write-Host "🐍 Starting FastAPI Backend..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; Write-Host '🐍 FastAPI Backend Server' -ForegroundColor Blue; uv run uvicorn app.main:app --reload --host 0.0.0.0 --port $backendPort"

# Wait a moment for backend to start
Start-Sleep -Seconds 2

# Start frontend in a new PowerShell window
Write-Host "⚛️  Starting Next.js Frontend..." -ForegroundColor Magenta
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; Write-Host '⚛️  Next.js Frontend Server' -ForegroundColor Magenta; npm run dev"

Write-Host ""
Write-Host "✅ Both servers are starting up!" -ForegroundColor Green
Write-Host "   - Backend: http://localhost:$backendPort" -ForegroundColor White
Write-Host "   - Frontend: http://localhost:$frontendPort" -ForegroundColor White
Write-Host "   - API Docs: http://localhost:$backendPort/docs" -ForegroundColor White
Write-Host ""
Write-Host "💡 To stop the servers, close the individual PowerShell windows or press Ctrl+C in each." -ForegroundColor Yellow
Write-Host "🔄 Both servers support hot-reload for development." -ForegroundColor Yellow 