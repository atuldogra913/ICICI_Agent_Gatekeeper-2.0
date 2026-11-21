@echo off
title ICICI Bank - Agent Gatekeeper Server
color 0B

echo ======================================================================
echo   AGENT GATEKEEPER: ICICI Bank AI Risk Management System
echo ======================================================================
echo.
echo [1/2] Opening your web browser to: http://localhost:8501 ...
start http://localhost:8501

echo.
echo [2/2] Launching Streamlit Web Server...
echo.
echo **********************************************************************
echo   IMPORTANT: KEEP THIS BLACK WINDOW OPEN!
echo   If you close this window, the website stops running.
echo   To close the website, simply close this window when done.
echo **********************************************************************
echo.

py -m streamlit run app.py --server.port 8501 --browser.gatherUsageStats false
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Trying direct Python path fallback...
    "%LOCALAPPDATA%\Python\pythoncore-3.15-64\python.exe" -m streamlit run app.py --server.port 8501 --browser.gatherUsageStats false
)

pause
