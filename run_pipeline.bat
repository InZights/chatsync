@echo off
setlocal

REM Teams to Slack full pipeline runner (Windows)
REM - If AZURE_CLIENT_ID is set, runs fetch+transform
REM - Otherwise, runs migrate against existing input file

echo ========================================================
echo   TEAMS TO SLACK PIPELINE (Windows)
echo ========================================================
echo.
echo Working directory: %~dp0
echo Date/Time: %DATE% %TIME%
echo --------------------------------------------------------

cd /d "%~dp0"

REM Optional: activate local venv if present
if exist "venv\Scripts\activate.bat" (
    echo [setup] Activating virtual environment...
    call "venv\Scripts\activate.bat"
    echo [setup] Virtual environment activated.
)

echo [setup] Checking environment variables...
if defined SLACK_BOT_TOKEN (
    echo   - SLACK_BOT_TOKEN: detected
) else (
    echo   - SLACK_BOT_TOKEN: not set (upload will stay dry-run if configured)
)
if defined SLACK_WEBHOOK_URL (
    echo   - SLACK_WEBHOOK_URL: detected
) else (
    echo   - SLACK_WEBHOOK_URL: not set (notifications will stay disabled)
)
if defined AZURE_CLIENT_ID (
    echo   - AZURE_CLIENT_ID: detected (fetch mode ON)
) else (
    echo   - AZURE_CLIENT_ID: not set (fetch mode OFF)
)
echo --------------------------------------------------------

set FETCH_MODE=0
if defined AZURE_CLIENT_ID (
    set FETCH_MODE=1
)

if %FETCH_MODE%==1 (
    echo [1/2] Fetching Teams data via Microsoft Graph...
    python scripts\fetch_and_migrate.py
    if errorlevel 1 (
        echo Fetch failed. Aborting pipeline.
        exit /b %errorlevel%
    )
    echo [2/2] Transforming and exporting to Slack format...
    python migrate.py
) else (
    echo [info] AZURE_CLIENT_ID not set. Skipping fetch; running migration on existing data.
    python migrate.py
)

echo --------------------------------------------------------
echo Pipeline completed at %DATE% %TIME%
echo ========================================================
echo.

endlocal
