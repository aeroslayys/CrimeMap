@echo off
setlocal
cd /d "%~dp0"

if not exist "backend\.venv\Scripts\python.exe" (
  echo.
  echo CrimeMap backend environment is not installed yet.
  echo Follow the Windows first-time setup in README.md.
  echo.
  pause
  exit /b 1
)

"backend\.venv\Scripts\python.exe" "start.py"
if errorlevel 1 (
  echo.
  echo CrimeMap could not start. See the error above.
  echo.
  pause
  exit /b 1
)
endlocal
