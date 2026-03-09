@echo off
REM Vehicle Detection App - Local Development Startup Script

echo.
echo ====================================
echo Vehicle Detection Application
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.10+ is required but not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js 18+ is required but not installed or not in PATH
    pause
    exit /b 1
)

echo [✓] Python and Node.js detected
echo.

REM Create and activate virtual environment
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install backend dependencies
echo.
echo Installing backend dependencies...
pip install -r backend/requirements.txt

REM Start backend in a new window
echo.
echo Starting FastAPI Backend (port 8000)...
start "Vehicle Detection - Backend" cmd /k "python backend/main.py"

REM Wait a bit for backend to start
timeout /t 3 /nobreak

REM Install and start frontend
echo.
echo Installing frontend dependencies...
cd frontend
if not exist node_modules (
    npm install
)

echo.
echo Starting React Frontend (port 3000)...
echo Opening browser...
timeout /t 2 /nobreak

start http://localhost:3000
npm start

cd ..
