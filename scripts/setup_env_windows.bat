@echo off

echo =============================================
echo  Drowsiness Detection - Windows Setup Script
echo =============================================

REM Go up one level to the project root
cd /d "%~dp0.."

REM Check if Python 3.11 is installed
py -3.11 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Python 3.11 not found. Trying default Python...
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python is not installed or not added to PATH.
        goto end
    )
    python -m venv venv
) else (
    echo [INFO] Python 3.11 found. Using it to create virtual environment...
    py -3.11 -m venv venv
)

REM Check if venv was created
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment creation failed.
    goto end
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call "venv\Scripts\activate"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    goto end
)

REM Install required packages
if exist requirements.txt (
    echo [INFO] Installing packages from requirements.txt...
    python -m pip install --upgrade pip 
    pip install -r requirements.txt
) else (
    echo [WARNING] requirements.txt not found. Skipping package installation.
)

REM Show installed packages
echo [INFO] Installed packages:
pip list

echo.
echo [SUCCESS] Virtual environment setup complete!
echo [INFO] To deactivate the environment, type: deactivate

REM === Step 2: React Frontend Setup ===

REM === Node.js Setup Check ===
node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not added to PATH.
    echo [INFO] Please install Node.js first from https://nodejs.org/en/download and rerun this script.
    g
)

echo [INFO] Setting up React dashboard...

cd dashboard
if exist package.json (
    echo [INFO] Installing frontend dependencies...
    npm install

    echo [INFO] Building React dashboard...
    npm run build

    echo [INFO] Optionally install static server...
    npm install -g serve
) else (
    echo [ERROR] React dashboard 'package.json' not found. Skipping frontend setup.
)

cd ..

REM === Done ===
echo.
echo [SUCCESS] Setup complete!
echo [INFO] To run backend: venv\Scripts\activate && uvicorn main:app --host 0.0.0.0 --port 8000
echo [INFO] To serve frontend: cd dashboard && npx serve -s dist -l 3000

deactivate

:end
pause
