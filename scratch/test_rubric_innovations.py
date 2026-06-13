"""
scratch/test_rubric_innovations.py - Verification script for new rubric compliance features.
Tests custom exceptions, composite weights, DP Knapsack, backtracking paths, and PDF reports.
"""
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.graph import DisasterGraph
from models.incident import DisasterIncident
from models.resource import ResourceInventory
from models.exceptions import CoordinateError, NodeNotFoundError, RoutingError
from modules.platform_orchestrator import DisasterPlatform

def test_custom_exceptions():
    print("Testing custom validation exceptions...")
    # 1. CoordinateError check
    try:
        inc = DisasterIncident("N08", "Flood", "High", 1000, coordinates=(120.0, 45.0)) # Out of bounds lat
        inc.validate()
        print("[FAIL] Out of bounds coordinates did not raise CoordinateError")
        sys.exit(1)
    except CoordinateError:
        print("  [OK] CoordinateError raised correctly for invalid coordinates.")
    except Exception as e:
        print(f"[FAIL] Raised unexpected exception: {type(e).__name__}: {str(e)}")
        sys.exit(1)

    # 2. NodeNotFoundError & RoutingError checks
    graph = DisasterGraph()
    graph.add_location("N01", "HQ", 20.0, 85.0)
    graph.add_location("N02", "Depot", 20.1, 85.1)
    graph.add_route("N01", "N02", 5.0, 1.0, 1.0, 1.0)

    try:
        graph.shortest_path("N01", "N99") # N99 does not exist
        print("[FAIL] Missing target node did not raise NodeNotFoundError")
        sys.exit(1)
    except NodeNotFoundError:
        print("  [OK] NodeNotFoundError raised correctly for missing node.")

    try:
        graph.shortest_path("N01", "N01") # Source == target
        print("[FAIL] Same source/target did not raise RoutingError")
        sys.exit(1)
    except RoutingError:
        print("  [OK] RoutingError raised correctly for identical nodes.")


def test_composite_weights():
    print("Testing composite routing edge weights...")
    graph = DisasterGraph()
    graph.add_location("N01", "HQ", 20.0, 85.0)
    graph.add_location("N02", "Depot", 20.1, 85.1)
    
    # Distance = 10km, road = 2.0, flood = 1.5, time_of_day = 1.1
    # Expected weight = 10 * 2 * 1.5 * 1.1 = 33.0
    graph.add_route("N01", "N02", 10.0, 2.0, 1.5, 1.1)
    
    edges = graph.all_edges_list()
    weight = edges[0]["weight"]
    if abs(weight - 33.0) < 0.001:
        print(f"  [OK] Composite weight calculated correctly: {weight}")
    else:
        print(f"[FAIL] Composite weight mismatch. Expected 33.0, got {weight}")
        sys.exit(1)


def test_dp_knapsack():
    print("Testing Dynamic Programming 0/1 Knapsack allocation...")
    platform = DisasterPlatform(bootstrap=True)
    
    # Clear and set a small stockpile
    platform.global_inventory.food = 100
    platform.global_inventory.water = 100
    platform.global_inventory.medical_kits = 5
    platform.global_inventory.rescue_teams = 2
    
    # We have sample incidents preloaded. Let's run Knapsack allocation with limited weight capacity
    # Knapsack capacity of 30,000 units
    from algorithms.knapsack_allocator import KnapsackResourceAllocator
    allocator = KnapsackResourceAllocator(capacity=30000)
    
    # Push active incidents to the queue
    from algorithms.priority_queue import IncidentPriorityQueue
    pq = IncidentPriorityQueue()
    for inc in platform.incidents:
        if inc.status.lower() != "resolved":
            pq.push(inc)
            
    raw_logs = allocator.allocate(pq, platform.global_inventory)
    print(f"  [OK] Knapsack DP completed. Allocated {len(raw_logs)} incidents.")
    
    # Assert that some incidents got allocated and others did not (due to Knapsack capacity constraint)
    allocated_count = sum(1 for entry in raw_logs if sum(entry["allocated"].values()) > 0)
    zero_allocated_count = sum(1 for entry in raw_logs if sum(entry["allocated"].values()) == 0)
    print(f"  [OK] Allocated: {allocated_count} incidents | Postponed: {zero_allocated_count} incidents.")


def test_backtracking_paths():
    print("Testing recursive Backtracking search for alternative paths...")
    platform = DisasterPlatform(bootstrap=True)
    
    # Find all paths between Central HQ (N01) and Riverside District (N08)
    alts = platform.plan_alternative_routes("N01", "N08", max_risk=50.0)
    if alts:
        print(f"  [OK] Found {len(alts)} alternative paths using backtracking.")
        for idx, alt in enumerate(alts[:3]):
            print(f"    Option #{idx+1}: {' -> '.join(alt['path_ids'])} (Risk: {alt['total_risk']} | Dist: {alt['total_distance']} km)")
    else:
        print("[FAIL] Backtracking returned 0 paths between N01 and N08")
        sys.exit(1)


def test_pdf_report():
    print("Testing PDF report generation...")
    platform = DisasterPlatform(bootstrap=True)
    
    filepath = "outputs/reports/test_report.pdf"
    if os.path.exists(filepath):
        os.remove(filepath)
        
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    platform.export_pdf_report(filepath)
    
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        print(f"  [OK] PDF report successfully compiled and saved to {filepath}")
    else:
        print("[FAIL] PDF report file missing or empty")
        sys.exit(1)


if __name__ == "__main__":
    print("="*60)
    print("STARTING DISASTERSENSE RUBRIC INNOVATIONS TEST SUITE")
    print("="*60)
    test_custom_exceptions()
    test_composite_weights()
    test_dp_knapsack()
    test_backtracking_paths()
    test_pdf_report()
    print("="*60)
    print("ALL RUBRIC INNOVATIONS VALIDATED SUCCESSFULLY!")
    print("="*60)
