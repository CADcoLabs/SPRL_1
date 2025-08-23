@echo off
REM Spiral Stair UI Launcher - Windows Batch File
REM This launcher ensures proper shell environment for AutoCAD COM access

echo Starting Spiral Stair UI...
echo.

REM Try to find Git Bash installation
set GITBASH_PATH=""
if exist "C:\Program Files\Git\bin\bash.exe" (
    set GITBASH_PATH="C:\Program Files\Git\bin\bash.exe"
) else if exist "C:\Program Files (x86)\Git\bin\bash.exe" (
    set GITBASH_PATH="C:\Program Files (x86)\Git\bin\bash.exe"
) else (
    echo ERROR: Git Bash not found. Please install Git for Windows.
    echo Git Bash is required for proper AutoCAD COM interface access.
    echo Download from: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Using Git Bash: %GITBASH_PATH%
echo.

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0
set UNIX_SCRIPT_DIR=%SCRIPT_DIR:\=/%
set UNIX_SCRIPT_DIR=%UNIX_SCRIPT_DIR:C:=/c%

REM Set default value if AUTOCAD_MOCK_MODE is not set
if "%AUTOCAD_MOCK_MODE%"=="" set AUTOCAD_MOCK_MODE=false

REM Launch UI through Git Bash with proper environment and variable inheritance
%GITBASH_PATH% -c "export AUTOCAD_MOCK_MODE='%AUTOCAD_MOCK_MODE%' && cd '%UNIX_SCRIPT_DIR%' && python launch_ui_real_autocad.py"

echo.
echo UI session completed.
pause