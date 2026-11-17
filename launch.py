"""
1-Click Python Launcher for ICICI Agent Gatekeeper.
Can be executed with: `python launch.py` or by double-clicking this file.
"""

import sys
import os
import time
import webbrowser
import subprocess

def main():
    print("=" * 70)
    print("  ICICI BANK AGENT GATEKEEPER: WEB LAUNCHER")
    print("=" * 70)
    print("\n1. Opening browser to: http://localhost:8501 ...")
    time.sleep(1)
    webbrowser.open("http://localhost:8501")

    print("\n2. Starting local web server...")
    print("   (Keep this window open while using the website!)\n")

    cmd = [
        sys.executable,
        "-m", "streamlit", "run", "app.py",
        "--server.port", "8501",
        "--browser.gatherUsageStats", "false"
    ]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
