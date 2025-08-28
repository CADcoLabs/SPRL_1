@echo off
setlocal enabledelayedexpansion

REM Smart Deploy to Network - Compare and copy only changed files
REM Author: Development Utility  
REM Date: 2025-08-28

echo ====================================
echo   Smart Deploy to Network Utility
echo ====================================
echo.

REM Set source path
set "SOURCE_DIR=%~dp0"

REM Hardcode the network path and deploy directly
set "NETWORK_DIR=P:\X-CAD TRANSFER\Spiral_Plugin"
set "APP_DIR=%NETWORK_DIR%\spiral_stair_app"

echo Source Directory: %SOURCE_DIR%
echo Network Directory: %NETWORK_DIR%
echo.

REM Create network directories if they don't exist
if not exist "%APP_DIR%\modules" mkdir "%APP_DIR%\modules"
if not exist "%APP_DIR%\ui" mkdir "%APP_DIR%\ui" 
if not exist "%APP_DIR%\core" mkdir "%APP_DIR%\core"
if not exist "%APP_DIR%\config" mkdir "%APP_DIR%\config"

set COPIED_COUNT=0
set SKIPPED_COUNT=0
set CHANGES_FOUND=0

REM Initialize array for files to copy (simulate array with variables)
set FILES_TO_COPY_COUNT=0

REM First pass - analyze what needs to be copied
echo Analyzing files for changes...
echo.

REM Compare core files
echo [CORE FILES]
for %%f in ("%SOURCE_DIR%core\*.py") do (
    call :AnalyzeFile "%%f" "%APP_DIR%\core\%%~nxf"
)

REM Compare config files  
echo [CONFIG FILES]
for %%f in ("%SOURCE_DIR%config\*.*") do (
    call :AnalyzeFile "%%f" "%APP_DIR%\config\%%~nxf"
)

REM Compare module files
echo [MODULE FILES]
for %%f in ("%SOURCE_DIR%modules\*.*") do (
    call :AnalyzeFile "%%f" "%APP_DIR%\modules\%%~nxf"
)

REM Compare UI files
echo [UI FILES]
for %%f in ("%SOURCE_DIR%ui\*.*") do (
    call :AnalyzeFile "%%f" "%APP_DIR%\ui\%%~nxf"
)

echo.
if !CHANGES_FOUND! EQU 0 (
    echo No changes detected. All files are up to date.
    echo.
    pause
    goto :EOF
)

echo ====================================
echo FILES TO BE COPIED - SUMMARY
echo ====================================
REM Display the list of files that will be copied
for /L %%i in (1,1,!FILES_TO_COPY_COUNT!) do (
    echo   !FILE_TO_COPY_%%i! [!FILE_TO_COPY_REASON_%%i!]
)
echo.

echo ====================================
echo DEPLOYMENT PREVIEW
echo Files that will be copied: !CHANGES_FOUND!
echo ====================================
echo.
set /p CONFIRM="Do you want to proceed with deployment? (y/N): "

if /i "!CONFIRM!" NEQ "y" (
    echo Deployment cancelled.
    echo.
    pause
    goto :EOF
)

echo.
echo Proceeding with deployment...
echo.

REM Second pass - actually copy the files
REM Compare core files
echo [COPYING CORE FILES]
for %%f in ("%SOURCE_DIR%core\*.py") do (
    call :CompareAndCopy "%%f" "%APP_DIR%\core\%%~nxf"
)

REM Compare config files  
echo [COPYING CONFIG FILES]
for %%f in ("%SOURCE_DIR%config\*.*") do (
    call :CompareAndCopy "%%f" "%APP_DIR%\config\%%~nxf"
)

REM Compare module files
echo [COPYING MODULE FILES]
for %%f in ("%SOURCE_DIR%modules\*.*") do (
    call :CompareAndCopy "%%f" "%APP_DIR%\modules\%%~nxf"
)

REM Compare UI files
echo [COPYING UI FILES]
for %%f in ("%SOURCE_DIR%ui\*.*") do (
    call :CompareAndCopy "%%f" "%APP_DIR%\ui\%%~nxf"
)

echo.
echo ====================================
echo Deployment Summary:
echo Files copied: !COPIED_COUNT!
echo Files skipped (unchanged): !SKIPPED_COUNT!
echo ====================================
echo.
pause
goto :EOF

:AnalyzeFile
set "SOURCE_FILE=%~1"
set "TARGET_FILE=%~2"
set "COPY_NEEDED=0"

REM Check if target file exists
if not exist "%TARGET_FILE%" (
    set "COPY_NEEDED=1"
    set "REASON=NEW FILE"
) else (
    REM Compare file dates/times
    for %%A in ("%SOURCE_FILE%") do set "SOURCE_DATE=%%~tA"
    for %%B in ("%TARGET_FILE%") do set "TARGET_DATE=%%~tB"
    
    REM Compare file sizes
    for %%A in ("%SOURCE_FILE%") do set "SOURCE_SIZE=%%~zA"
    for %%B in ("%TARGET_FILE%") do set "TARGET_SIZE=%%~zB"
    
    if "!SOURCE_SIZE!" NEQ "!TARGET_SIZE!" (
        set "COPY_NEEDED=1"
        set "REASON=SIZE DIFF"
    ) else if "!SOURCE_DATE!" GTR "!TARGET_DATE!" (
        set "COPY_NEEDED=1" 
        set "REASON=NEWER"
    )
)

if "!COPY_NEEDED!"=="1" (
    echo   WILL COPY: %~nx1 [!REASON!]
    set /A CHANGES_FOUND+=1
    REM Store file name for summary
    set /A FILES_TO_COPY_COUNT+=1
    set "FILE_TO_COPY_!FILES_TO_COPY_COUNT!=%~nx1"
    set "FILE_TO_COPY_REASON_!FILES_TO_COPY_COUNT!=!REASON!"
) else (
    echo   UP TO DATE: %~nx1
)

goto :EOF

:CompareAndCopy
set "SOURCE_FILE=%~1"
set "TARGET_FILE=%~2"
set "COPY_NEEDED=0"

REM Check if target file exists
if not exist "%TARGET_FILE%" (
    set "COPY_NEEDED=1"
    set "REASON=NEW FILE"
) else (
    REM Compare file dates/times
    for %%A in ("%SOURCE_FILE%") do set "SOURCE_DATE=%%~tA"
    for %%B in ("%TARGET_FILE%") do set "TARGET_DATE=%%~tB"
    
    REM Compare file sizes
    for %%A in ("%SOURCE_FILE%") do set "SOURCE_SIZE=%%~zA"
    for %%B in ("%TARGET_FILE%") do set "TARGET_SIZE=%%~zB"
    
    if "!SOURCE_SIZE!" NEQ "!TARGET_SIZE!" (
        set "COPY_NEEDED=1"
        set "REASON=SIZE DIFF"
    ) else if "!SOURCE_DATE!" GTR "!TARGET_DATE!" (
        set "COPY_NEEDED=1" 
        set "REASON=NEWER"
    )
)

if "!COPY_NEEDED!"=="1" (
    copy /Y "%SOURCE_FILE%" "%TARGET_FILE%" >nul
    echo   COPIED: %~nx1 [!REASON!]
    set /A COPIED_COUNT+=1
) else (
    echo   SKIP:   %~nx1 [UNCHANGED]
    set /A SKIPPED_COUNT+=1
)

goto :EOF