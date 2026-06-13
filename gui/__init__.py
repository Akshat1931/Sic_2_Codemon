"""
gui package initialization - exports Tkinter view classes.
"""
from .main_window import MainWindow
from .incident_form import IncidentForm
from .resource_panel import ResourcePanel
from .dashboard_frame import DashboardFrame

__all__ = [
    "MainWindow",
    "IncidentForm",
    "ResourcePanel",
    "DashboardFrame"
]
