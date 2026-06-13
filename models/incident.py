"""
models/incident.py - Disaster incident representation and validation.
"""
from datetime import datetime
import uuid
import math
from config import DISASTER_WEIGHTS, SEVERITY_MAPPING

class StateTransitionError(Exception):
    """Exception raised when an invalid incident state transition is attempted."""
    pass

class DisasterIncident:
    """Represents a reported disaster incident with severity, status, and resource tracking."""
    _counter = 0

    def __init__(self, location: str, disaster_type: str, severity, population_affected: int,
                 description: str = "", reporter: str = "Anonymous", incident_id: str = None,
                 timestamp: str = None, coordinates=None, status: str = "Reported"):
        if incident_id is None:
            DisasterIncident._counter += 1
            self.incident_id = f"INC{DisasterIncident._counter:04d}"
        else:
            self.incident_id = incident_id
            
        self.location = location  # Node ID of location
        self.disaster_type = disaster_type
        
        # Convert severity if it's a string, though it will be overridden by population
        if isinstance(severity, int):
            self.severity = severity
        else:
            sev_key = str(severity).lower()
            self.severity = SEVERITY_MAPPING.get(sev_key, 3)

        self.population_affected = population_affected
        self.description = description
        self.reporter = reporter
        self.timestamp = timestamp or datetime.now().isoformat()
        self.coordinates = coordinates or (0.0, 0.0)
        self.status = status  # Reported, Active, Contained, Resolved
        
        # Allocation properties
        from .resource import ResourceInventory
        self.allocated_resources = None
        self.assigned_shelter = None
        self.rescue_route = []

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, new_status: str):
        valid_statuses = ["reported", "active", "contained", "resolved"]
        new_status_lower = new_status.lower()
        if new_status_lower not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}")
            
        cap_status = new_status_lower.capitalize()

        if not hasattr(self, "_status"):
            self._status = cap_status
            return

        if self._status == cap_status:
            return

        old_status_lower = self._status.lower()
        
        # Enforce transition rules:
        # Reported -> Active
        # Active -> Contained
        # Contained -> Resolved
        allowed = False
        if old_status_lower == "reported" and new_status_lower == "active":
            allowed = True
        elif old_status_lower == "active" and new_status_lower == "contained":
            allowed = True
        elif old_status_lower == "contained" and new_status_lower == "resolved":
            allowed = True
            
        if not allowed:
            raise StateTransitionError(
                f"Invalid state transition from '{self._status}' to '{cap_status}'."
            )
        self._status = cap_status

    @property
    def population_affected(self) -> int:
        return self._population_affected

    @population_affected.setter
    def population_affected(self, val: int):
        self._population_affected = int(val)
        # Auto-detect severity according to population affected:
        # - Population < 1000: Low (Severity score = 2)
        # - 1000 to < 5000: Medium (Severity score = 3)
        # - 5000 to < 20000: High (Severity score = 4)
        # - Population >= 20000: Critical (Severity score = 5)
        if self._population_affected < 1000:
            self.severity = 2
        elif self._population_affected < 5000:
            self.severity = 3
        elif self._population_affected < 20000:
            self.severity = 4
        else:
            self.severity = 5

    # Compatibility properties for index.html/existing API endpoints
    @property
    def incident_id_str(self) -> str:
        return self.incident_id

    @property
    def location_id(self) -> str:
        return self.location

    @location_id.setter
    def location_id(self, val: str):
        self.location = val

    @property
    def severity_level_str(self) -> str:
        # Map integer back to string for frontend compatibility
        inv_map = {1: "Low", 2: "Low", 3: "Medium", 4: "High", 5: "Critical"}
        return inv_map.get(self.severity, "Medium")

    @property
    def severity_score(self) -> int:
        return self.severity

    @property
    def priority_index(self) -> float:
        """Priority score used by the web frontend."""
        # Using the formula from the original app.py to avoid UI discrepancies
        return self.severity * math.log1p(self.population_affected)

    def get_priority_score(self) -> float:
        """Priority score calculated using Section 5.1/5.2 of the PDF."""
        w = DISASTER_WEIGHTS.get(self.disaster_type.lower(), 1.0)
        return self.severity * self.population_affected * w

    def validate(self) -> bool:
        """Validates all fields of the incident according to Section 15 of the PDF."""
        if not self.location or len(self.location) > 100:
            raise ValueError("Location cannot be empty and must be <= 100 characters.")
        
        valid_types = {t.lower() for t in DISASTER_WEIGHTS.keys()}
        if self.disaster_type.lower() not in valid_types:
            raise TypeError("Invalid disaster type selected.")
            
        if not (1 <= self.severity <= 5):
            raise ValueError("Severity must be between 1 and 5.")
            
        if self.population_affected <= 0:
            raise ValueError("Population must be greater than 0.")
            
        from models.exceptions import CoordinateError
        lat, lon = self.coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise CoordinateError("Invalid GPS coordinates.")
            
        valid_statuses = {"reported", "active", "contained", "resolved"}
        if self.status.lower() not in valid_statuses:
            raise ValueError("Invalid status.")
            
        return True

    def to_dict(self):
        return {
            "incident_id": self.incident_id,
            "location_id": self.location,
            "location": self.location,
            "disaster_type": self.disaster_type,
            "severity": self.severity_level_str,  # API expects string like "Critical"
            "severity_score": self.severity,       # Integer score
            "population_affected": self.population_affected,
            "description": self.description,
            "reporter": self.reporter,
            "timestamp": self.timestamp,
            "status": self.status,
            "allocated_resources": self.allocated_resources.to_dict() if self.allocated_resources else None,
            "assigned_shelter": self.assigned_shelter,
            "rescue_route": self.rescue_route,
            "priority_index": round(self.priority_index, 2),
            "priority_score": round(self.get_priority_score(), 2),
            "coordinates": self.coordinates,
        }

    def __repr__(self):
        return f"DisasterIncident({self.incident_id}, {self.disaster_type}, {self.severity_level_str})"
