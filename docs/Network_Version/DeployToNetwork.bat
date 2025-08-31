@echo off
setlocal enabledelayedexpansion

REM DeployToNetwork - Deploy modified files to network Spiral_Plugin
REM Author: Development Utility
REM Date: 2025-08-26
REM Updated: 2025-08-28 - Fixed core and config deployment

echo ====================================
echo   Deploy to Network Utility
echo ====================================
echo.

REM Set source path
set "SOURCE_DIR=%~dp0"

REM Hardcode the network path and deploy directly
set "NETWORK_DIR=P:\X-CAD TRANSFER\Spiral_Plugin"

echo Source Directory: %SOURCE_DIR%
echo Network Directory: %NETWORK_DIR%
echo.

REM Create network directories if they don't exist
if not exist "%NETWORK_DIR%\spiral_stair_app\modules" mkdir "%NETWORK_DIR%\spiral_stair_app\modules"
if not exist "%NETWORK_DIR%\spiral_stair_app\ui" mkdir "%NETWORK_DIR%\spiral_stair_app\ui"
if not exist "%NETWORK_DIR%\spiral_stair_app\core" mkdir "%NETWORK_DIR%\spiral_stair_app\core"
if not exist "%NETWORK_DIR%\spiral_stair_app\config" mkdir "%NETWORK_DIR%\spiral_stair_app\config"

REM Copy all core files (CRITICAL - was missing!)
echo Copying core files...
xcopy "%SOURCE_DIR%core\*.py" "%NETWORK_DIR%\spiral_stair_app\core\" /Y /I

REM Copy all config files
echo Copying config files...
xcopy "%SOURCE_DIR%config\*.*" "%NETWORK_DIR%\spiral_stair_app\config\" /Y /I

REM Copy all Python modules
echo Copying modules...
xcopy "%SOURCE_DIR%modules\*.py" "%NETWORK_DIR%\spiral_stair_app\modules\" /Y /I

REM Copy all UI files
echo Copying UI files...
xcopy "%SOURCE_DIR%ui\*.*" "%NETWORK_DIR%\spiral_stair_app\ui\" /Y /I

echo.
echo Deployment Complete!

echo.
pause