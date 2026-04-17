@echo off

echo ================================
echo   FITAI DJANGO START SCRIPT
echo ================================

REM 1. Check Python
python --version
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    pause
    exit /b
)

REM 2. Create venv if not exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM 3. Activate venv
call .venv\Scripts\activate

REM 4. Upgrade pip
python -m pip install --upgrade pip

REM 5. Install requirements
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo requirements.txt not found!
    pause
    exit /b
)

REM 6. Django check
echo Running Django check...
python manage.py check

REM 7. Migrations
echo Applying migrations...
python manage.py migrate

REM 8. Start server
echo Starting Django server...
python manage.py runserver

pause