@echo off
REM AKF3 Development Server Startup Script
REM This script starts both the FastAPI backend and Next.js frontend

echo.
echo 🚀 Starting AKF3 Development Servers...
echo.

REM Set ports
set BACKEND_PORT=8000
set FRONTEND_PORT=3000

echo 📊 Backend API will be available at: http://localhost:%BACKEND_PORT%
echo 🌐 Frontend will be available at: http://localhost:%FRONTEND_PORT%
echo 📚 API Documentation at: http://localhost:%BACKEND_PORT%/docs
echo.

REM Start backend in a new command window
echo 🐍 Starting FastAPI Backend...
start "AKF3 Backend Server" cmd /k "cd /d %~dp0 && echo 🐍 FastAPI Backend Server && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port %BACKEND_PORT%"

REM Wait a moment for backend to start
timeout /t 2 /nobreak >nul

REM Start frontend in a new command window
echo ⚛️  Starting Next.js Frontend...
start "AKF3 Frontend Server" cmd /k "cd /d %~dp0frontend && echo ⚛️  Next.js Frontend Server && npm run dev"

echo.
echo ✅ Both servers are starting up!
echo    - Backend: http://localhost:%BACKEND_PORT%
echo    - Frontend: http://localhost:%FRONTEND_PORT%
echo    - API Docs: http://localhost:%BACKEND_PORT%/docs
echo.
echo 💡 To stop the servers, close the individual command windows or press Ctrl+C in each.
echo 🔄 Both servers support hot-reload for development.
echo.
pause 