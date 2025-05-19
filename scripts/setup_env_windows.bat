@echo off

echo =============================================
echo  Drowsiness Detection - Windows Setup Script
echo =============================================

REM Go up one level to the project root
cd /d "%~dp0.."

REM Check if Python 3.10 is installed
py -3.10 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Python 3.10 not found. Trying default Python...
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python is not installed or not added to PATH.
        goto end
    )
    python -m venv venv
) else (
    echo [INFO] Python 3.10 found. Using it to create virtual environment...
    py -3.10 -m venv venv
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
deactivate

:end
pause
