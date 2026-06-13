import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.incident import DisasterIncident

def test_severity_autodetect():
    print("Testing auto-detection of severity...")
    
    # Test case 1: < 1000 -> Low (2)
    inc1 = DisasterIncident("N08", "Flood", "High", 500)
    print(f"  Pop = 500: Severity Level = {inc1.severity_level_str} (Score: {inc1.severity})")
    assert inc1.severity == 2
    assert inc1.severity_level_str == "Low"

    # Test case 2: 1000 to < 5000 -> Medium (3)
    inc2 = DisasterIncident("N08", "Flood", "Low", 1500)
    print(f"  Pop = 1500: Severity Level = {inc2.severity_level_str} (Score: {inc2.severity})")
    assert inc2.severity == 3
    assert inc2.severity_level_str == "Medium"

    # Test case 3: 5000 to < 20000 -> High (4)
    inc3 = DisasterIncident("N08", "Flood", "Critical", 8000)
    print(f"  Pop = 8000: Severity Level = {inc3.severity_level_str} (Score: {inc3.severity})")
    assert inc3.severity == 4
    assert inc3.severity_level_str == "High"

    # Test case 4: >= 20000 -> Critical (5)
    inc4 = DisasterIncident("N08", "Flood", "Low", 25000)
    print(f"  Pop = 25000: Severity Level = {inc4.severity_level_str} (Score: {inc4.severity})")
    assert inc4.severity == 5
    assert inc4.severity_level_str == "Critical"

    # Test case 5: property setter update
    inc4.population_affected = 400
    print(f"  Update Pop to 400: Severity Level = {inc4.severity_level_str} (Score: {inc4.severity})")
    assert inc4.severity == 2
    assert inc4.severity_level_str == "Low"

    print("Auto-detection validated successfully!")

if __name__ == "__main__":
    test_severity_autodetect()
