@echo off
setlocal enabledelayedexpansion

REM DeployToNetwork - Deploy modified files to network Spiral_Plugin
REM Author: Development Utility
REM Date: 2025-08-26

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
if not exist "%NETWORK_DIR%\modules" mkdir "%NETWORK_DIR%\modules"
if not exist "%NETWORK_DIR%\ui" mkdir "%NETWORK_DIR%\ui"

REM Copy all Python modules
echo Copying modules...
xcopy "%SOURCE_DIR%modules\*.py" "%NETWORK_DIR%\modules\" /Y /I

REM Copy all UI files
echo Copying UI files...
xcopy "%SOURCE_DIR%ui\*.*" "%NETWORK_DIR%\ui\" /Y /I

echo.
echo Deployment Complete!

echo.
pause