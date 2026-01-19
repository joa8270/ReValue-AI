@echo off
echo ==========================================
echo      MIRRA Environment Restore Tool
echo ==========================================
echo.
echo 1. Restoring Python Backend dependencies...
pip install -r backend/requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Python dependencies failed to install.
    pause
    exit /b %errorlevel%
)

echo.
echo 2. Restoring Frontend dependencies (node_modules)...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Frontend dependencies failed to install.
    pause
    exit /b %errorlevel%
)
cd ..

echo.
echo ==========================================
echo      Restore Complete! (Ready to Work)
echo ==========================================
echo.
echo You can now run: python run.py
echo.
pause
