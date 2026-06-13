"""
config.py - Global settings and constants for DisasterOS.
"""

# Disaster Type Weight Multipliers (from Section 5.1 & Section 6.1 of PDF)
DISASTER_WEIGHTS = {
    "earthquake": 1.5,
    "flood": 1.3,
    "cyclone": 1.4,
    "tsunami": 1.6,
    "fire": 1.2,
    "wildfire": 1.2,
    "landslide": 1.1,
}

# Severity string to integer score mapping (from Section 15 of PDF)
SEVERITY_MAPPING = {
    "minor": 1,
    "low": 2,
    "medium": 3,
    "moderate": 3,
    "high": 4,
    "critical": 5,
}

# Default initial stockpile quantities matching sample outputs
DEFAULT_STOCKPILE = {
    "food": 120000,
    "water": 200000,
    "medical_kits": 2000,
    "rescue_teams": 50
}
