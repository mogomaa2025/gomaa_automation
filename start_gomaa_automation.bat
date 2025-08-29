@echo off
echo ========================================
echo    Gomaa Automation - Starting Up
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    uv venv --python 3.11
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
uv sync
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo ========================================
    echo    Configuration Required
    echo ========================================
    echo.
    echo Please create a .env file with your API keys:
    echo.
    echo GOOGLE_API_KEY=your_gemini_api_key_here
    echo LAMINAR_API_KEY=your_laminar_api_key_here
    echo.
    echo Press any key to create .env file...
    pause >nul
    
    echo GOOGLE_API_KEY=your_gemini_api_key_here > .env
    echo LAMINAR_API_KEY=your_laminar_api_key_here >> .env
    echo.
    echo .env file created! Please edit it with your actual API keys.
    echo.
    pause
)

REM Start the application
echo.
echo ========================================
echo    Starting Gomaa Automation
echo ========================================
echo.
echo Web interface will be available at:
echo   - Local: http://localhost:5000
echo   - Network: http://0.0.0.0:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python professional_ai_automation.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)
