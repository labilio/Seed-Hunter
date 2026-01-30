@echo off
setlocal

echo ============================================================
echo Seed Hunter - Development Start Script (Windows)
echo ============================================================

set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"
set "FRONTEND_DIR=%SCRIPT_DIR%web"

:: Check Frontend
if not exist "%FRONTEND_DIR%" (
    echo [ERROR] Frontend directory not found: %FRONTEND_DIR%
    pause
    exit /b 1
)

:: Check Backend
if not exist "%BACKEND_DIR%" (
    echo [ERROR] Backend directory not found: %BACKEND_DIR%
    pause
    exit /b 1
)

:: --- Frontend Setup ---
echo [INFO] Checking Frontend dependencies...
cd /d "%FRONTEND_DIR%"
if not exist "node_modules" (
    echo [INFO] Installing Frontend dependencies...
    call npm install
) else (
    echo [INFO] Frontend dependencies found.
)

:: --- Backend Setup ---
echo [INFO] Checking Backend configuration...
cd /d "%BACKEND_DIR%"

:: Check .env
if not exist ".env" (
    if exist ".env.example" (
        echo [INFO] .env not found. Copying from .env.example...
        copy ".env.example" ".env"
        echo [WARN] Please edit backend/.env and fill in necessary API keys!
    ) else (
        echo [ERROR] .env.example not found!
    )
)

:: Check Python Virtual Environment
if not exist ".venv" (
    echo [INFO] Creating Python virtual environment...
    python -m venv .venv
)

:: Activate venv and install requirements
echo [INFO] Installing/Checking Backend requirements...
call .venv\Scripts\activate
pip install -r requirements.txt

:: --- Start Services ---
echo [INFO] Starting services...

:: Start Backend in new window
start "Seed Hunter Backend" cmd /k "cd /d %SCRIPT_DIR% && call backend\.venv\Scripts\activate && python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

:: Start Frontend in new window
start "Seed Hunter Frontend" cmd /k "cd /d %FRONTEND_DIR% && npm run dev"

echo.
echo [SUCCESS] Services are starting in separate windows.
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000
echo.
echo Press any key to close this launcher...
pause >nul
