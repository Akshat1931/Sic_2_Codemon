"""
app.py - Compatibility entry point for DisasterOS FastAPI application.
Imports the FastAPI app instance from the modularized web_app module.
"""
from web_app import app

__all__ = ["app"]
