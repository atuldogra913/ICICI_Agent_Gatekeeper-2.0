@echo off
title ICICI Bank Agent Gatekeeper - Library Installer
color 0B
echo ======================================================================
echo   ICICI BANK AGENT GATEKEEPER: PYTHON DEPENDENCY INSTALLER
echo   Academic Project Environment Setup
echo ======================================================================
echo.
echo Installing required libraries: streamlit, pandas...
echo.

py -m pip install --upgrade pip
py -m pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Trying fallback direct python path...
    "%LOCALAPPDATA%\Python\pythoncore-3.15-64\python.exe" -m pip install -r requirements.txt
)

echo.
echo ======================================================================
echo   Installation check:
echo ======================================================================
py -m streamlit --version
echo.
echo Setup complete! You can now launch the app using run_app.bat.
pause
