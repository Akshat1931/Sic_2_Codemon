# -*- coding: utf-8 -*-
"""
run.py -- Launch DisasterOS Server
Run: python run.py
"""
import sys
import io
import uvicorn

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

if __name__ == "__main__":
    print("\n" + "="*55)
    print("  DisasterOS -- Smart Disaster Response Platform")
    print("  Server: http://localhost:8000")
    print("  Press CTRL+C to stop")
    print("="*55 + "\n")
    uvicorn.run(
        "web_app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
    )

