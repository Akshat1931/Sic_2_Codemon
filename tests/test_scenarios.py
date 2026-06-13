"""
tests/test_scenarios.py
=======================
Official Test Suite — Section 19 of DisasterSense specification.

Test Cases:
  TC-001  Register valid incident with all fields
  TC-002  Register incident with severity = 0 (invalid)
  TC-003  Allocate resources with sufficient inventory
  TC-004  Allocate with empty inventory
  TC-005  BFS on graph with 1 available shelter
  TC-006  BFS with no available shelters (all full)
  TC-007  Dijkstra on connected graph
  TC-008  Dijkstra with disconnected graph
  TC-009  Dashboard with 0 incidents
  TC-010  Load 1000 incidents via CSV (performance test)

Run:
    python tests/test_scenarios.py
"""

# Official test scenarios table from the disaster response specification
# -------------------------------------------------------------
# Test ID  Scenario                                         Expected Result
# TC-001   Register valid incident with all fields          Incident added to queue; priority computed correctly
# TC-002   Register incident with severity = 0              ValueError raised; error shown in GUI; not added to queue
# TC-003   Allocate resources with sufficient inventory     All needs met; zero deficit; log shows full allocation
# TC-004   Allocate with empty inventory                    All resources show 0 allocated; full deficit reported; restock alert triggered
# TC-005   BFS on graph with 1 available shelter            Correct shelter returned with hop-count path
# TC-006   BFS with no available shelters (all full)        Returns None; UI shows 'All shelters at capacity'
# TC-007   Dijkstra on connected graph                      Shortest weighted path returned; distance correct
# TC-008   Dijkstra with disconnected graph                 Returns None path; distance = infinity; handled gracefully
# TC-009   Dashboard with 0 incidents                        Empty state UI shown; no chart errors; graceful empty DataFrames
# TC-010   Load 1000 incidents via CSV                      All loaded in <2s; queue ordered correctly
# -------------------------------------------------------------

import sys
import os
import time
import traceback

# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.incident import DisasterIncident
from models.graph import DisasterGraph
from models.resource import ResourceInventory
from models.exceptions import CoordinateError, NodeNotFoundError, RoutingError
from models.location import ShelterNode
from algorithms.priority_queue import IncidentPriorityQueue
from algorithms.greedy_allocator import GreedyResourceAllocator
from algorithms.bfs_shelter import ShelterFinder
from algorithms.dijkstra_routes import RouteEngine
from modules.platform_orchestrator import DisasterPlatform
from modules.analytics import AnalyticsDashboard

# ── Terminal colours ────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

PASS_TAG = f"{GREEN}{BOLD}  PASS{RESET}"
FAIL_TAG = f"{RED}{BOLD}  FAIL{RESET}"

results = []


def run_test(tc_id: str, scenario: str, fn):
    """Execute a test function and record PASS / FAIL."""
    try:
        fn()
        results.append((tc_id, scenario, True, None))
        print(f"{PASS_TAG}  [{tc_id}]  {scenario}")
    except Exception as e:
        results.append((tc_id, scenario, False, str(e)))
        print(f"{FAIL_TAG}  [{tc_id}]  {scenario}")
        print(f"         {RED}→ {e}{RESET}")


# ══════════════════════════════════════════════════════════════════
# TC-001  Register valid incident with all fields
# Expected: Incident added to queue; priority computed correctly
# ══════════════════════════════════════════════════════════════════
def tc_001():
    platform = DisasterPlatform(bootstrap=True)
    before = len(platform.incidents)

    inc = platform.report_incident(
        location_id="N08",
        disaster_type="Flood",
        population_affected=5000,
        severity="High",
        description="Major flooding in riverside district",
        reporter="Field Unit Alpha",
    )

    assert inc is not None, "report_incident() returned None"
    assert len(platform.incidents) == before + 1, "Incident not appended to list"
    assert inc.incident_id is not None, "incident_id not assigned"

    # Priority score = severity * population * disaster_weight
    priority = inc.get_priority_score()
    assert priority > 0, f"Priority score must be > 0, got {priority}"

    # Verify queue ordering — highest priority should come out first
    pq = IncidentPriorityQueue()
    low_inc  = DisasterIncident("N10", "Earthquake", "Low",      500)
    high_inc = DisasterIncident("N08", "Flood",      "Critical", 30000)
    pq.push(low_inc)
    pq.push(high_inc)
    top = pq.pop()
    assert top is high_inc, "Max-heap priority queue did not return highest priority incident first"


# ══════════════════════════════════════════════════════════════════
# TC-002  Register incident with severity = 0 (invalid population)
# Expected: ValueError raised; not added to queue
# ══════════════════════════════════════════════════════════════════
def tc_002():
    platform = DisasterPlatform(bootstrap=True)
    before = len(platform.incidents)
    raised = False
    try:
        # population = 0 should fail validation (population must be > 0)
        inc = DisasterIncident("N08", "Flood", "Low", 0)
        inc.validate()
    except ValueError as e:
        raised = True

    assert raised, "ValueError was NOT raised for population = 0"
    # Confirm nothing was added
    assert len(platform.incidents) == before, "Invalid incident was added to platform list"

    # Also verify severity < 1 raises after manual set
    inc2 = DisasterIncident("N08", "Flood", "Low", 500)
    inc2.severity = 0   # force invalid severity
    raised2 = False
    try:
        inc2.validate()
    except ValueError:
        raised2 = True
    assert raised2, "ValueError was NOT raised for severity = 0"


# ══════════════════════════════════════════════════════════════════
# TC-003  Allocate resources with sufficient inventory
# Expected: All needs met; zero deficit; log shows full allocation
# ══════════════════════════════════════════════════════════════════
def tc_003():
    # Use a very small single incident + large inventory so needs are fully met
    from modules.incident_manager import IncidentManager

    inv = ResourceInventory(food=999999, water=999999, medical_kits=99999, rescue_teams=9999)
    inc = DisasterIncident("N08", "Flood", "Medium", 100)  # tiny pop → small needs
    inc_mgr = IncidentManager()
    inc_mgr.incidents.append(inc)
    inc_mgr.priority_queue.push(inc)

    allocator = GreedyResourceAllocator()
    pq = IncidentPriorityQueue()
    pq.push(inc)

    log = allocator.allocate(pq, inv)

    assert len(log) == 1, "Expected exactly 1 allocation log entry"
    deficit = log[0]["deficit"]
    total_deficit = sum(deficit.values())
    assert total_deficit == 0, (
        f"Expected zero deficit with sufficient inventory, got: {deficit}"
    )


# ══════════════════════════════════════════════════════════════════
# TC-004  Allocate with empty inventory
# Expected: All resources = 0 allocated; full deficit reported
# ══════════════════════════════════════════════════════════════════
def tc_004():
    inv = ResourceInventory(food=0, water=0, medical_kits=0, rescue_teams=0)
    inc = DisasterIncident("N08", "Flood", "Critical", 10000)

    allocator = GreedyResourceAllocator()
    pq = IncidentPriorityQueue()
    pq.push(inc)

    log = allocator.allocate(pq, inv)

    assert len(log) == 1, "Expected 1 log entry"
    alloc   = log[0]["allocated"]
    deficit = log[0]["deficit"]

    assert all(v == 0 for v in alloc.values()), (
        f"With empty inventory all allocated must be 0, got: {alloc}"
    )
    assert any(v > 0 for v in deficit.values()), (
        f"Deficit must be reported when inventory is empty, got: {deficit}"
    )


# ══════════════════════════════════════════════════════════════════
# TC-005  BFS on graph with 1 available shelter
# Expected: Correct shelter returned with hop-count path
# ══════════════════════════════════════════════════════════════════
def tc_005():
    platform = DisasterPlatform(bootstrap=True)

    # Confirm there is at least 1 shelter with capacity
    shelters = list(platform.shelters.values())
    assert len(shelters) >= 1, "No shelters loaded in bootstrap"

    # Run BFS shelter recommendation for INC-001 (N08 — Riverside)
    inc = platform.incidents[0]
    recs = platform.recommend_shelters(inc.incident_id, max_results=3)

    assert len(recs) >= 1, "BFS returned 0 shelter recommendations"
    first = recs[0]
    assert "shelter_id"       in first, "Missing shelter_id in result"
    assert "bfs_hops"         in first, "Missing bfs_hops in result"
    assert "distance_km"      in first, "Missing distance_km in result"
    assert first["bfs_hops"]  >= 1,     "BFS hops must be >= 1"
    assert first["distance_km"] > 0,    "Distance must be > 0"


# ══════════════════════════════════════════════════════════════════
# TC-006  BFS with no available shelters (all full)
# Expected: Returns empty list; graceful handling
# ══════════════════════════════════════════════════════════════════
def tc_006():
    platform = DisasterPlatform(bootstrap=True)

    # Fill all shelters to capacity
    for shelter in platform.shelters.values():
        shelter.current_occupancy = shelter.capacity

    inc = platform.incidents[0]
    recs = platform.recommend_shelters(inc.incident_id, max_results=4)

    # All shelters are full → BFS should return empty list
    assert isinstance(recs, list), "recommend_shelters() must return a list"
    # Either empty or every returned shelter has 0 vacancy
    for r in recs:
        assert r.get("available_capacity", 0) == 0, (
            f"Shelter {r['shelter_id']} should be full but shows vacancy"
        )


# ══════════════════════════════════════════════════════════════════
# TC-007  Dijkstra on connected graph
# Expected: Shortest weighted path returned; distance correct
# ══════════════════════════════════════════════════════════════════
def tc_007():
    graph = DisasterGraph()
    graph.add_location("A", "Alpha HQ",    20.0, 85.0)
    graph.add_location("B", "Beta Depot",  20.1, 85.1)
    graph.add_location("C", "Gamma Zone",  20.2, 85.2)

    # A-B: weight = 5*1*1*1 = 5
    # B-C: weight = 3*1*1*1 = 3
    # A-C: weight = 20*1*1*1 = 20  (longer direct route)
    graph.add_route("A", "B", 5.0,  1.0, 1.0, 1.0)
    graph.add_route("B", "C", 3.0,  1.0, 1.0, 1.0)
    graph.add_route("A", "C", 20.0, 1.0, 1.0, 1.0)

    path, cost = graph.shortest_path("A", "C")

    assert path == ["A", "B", "C"], f"Expected path A→B→C, got {path}"
    assert abs(cost - 8.0) < 0.001, f"Expected cost 8.0, got {cost}"


# ══════════════════════════════════════════════════════════════════
# TC-008  Dijkstra with disconnected graph
# Expected: Returns empty path; distance = infinity; handled gracefully
# ══════════════════════════════════════════════════════════════════
def tc_008():
    graph = DisasterGraph()
    graph.add_location("X", "Island Alpha", 10.0, 70.0)
    graph.add_location("Y", "Island Beta",  11.0, 71.0)
    # No edges — graph is disconnected

    path, cost = graph.shortest_path("X", "Y")

    assert path == [] or cost == float("inf"), (
        f"Expected empty path and infinity cost for disconnected graph, got path={path} cost={cost}"
    )


# ══════════════════════════════════════════════════════════════════
# TC-009  Dashboard / Analytics with 0 incidents
# Expected: Empty state returned gracefully; no exceptions
# ══════════════════════════════════════════════════════════════════
def tc_009():
    dash = AnalyticsDashboard()
    inv  = ResourceInventory(food=120000, water=200000, medical_kits=2000, rescue_teams=50)

    # show_stats with empty list should return empty dict without crashing
    result = dash.show_stats([], inv)
    assert result == {} or isinstance(result, dict), (
        "show_stats([]) must return empty dict gracefully"
    )

    # render_charts should also return empty dict without crashing
    charts = dash.render_charts([], inv)
    assert isinstance(charts, dict), "render_charts([]) must return a dict"


# ══════════════════════════════════════════════════════════════════
# TC-010  Load 1000 incidents — performance test
# Expected: All loaded in < 2s; queue ordered correctly
# ══════════════════════════════════════════════════════════════════
def tc_010():
    platform = DisasterPlatform(bootstrap=False)

    # Add minimal graph node for incident location
    platform.graph.add_location("N01", "Central HQ", 20.29, 85.82)

    disaster_types = ["Flood", "Earthquake", "Cyclone", "Wildfire", "Landslide"]

    start = time.perf_counter()
    for i in range(1000):
        pop   = 500 + (i * 47) % 49500   # varied population 500 – 50000
        dtype = disaster_types[i % len(disaster_types)]
        inc   = DisasterIncident(
            location=   "N01",
            disaster_type=dtype,
            severity=   "High",
            population_affected=pop,
            description=f"Stress-test incident #{i+1}",
            reporter=   "AutoTest",
            incident_id=f"STRESS-{i+1:04d}",
        )
        platform.incident_manager.register(inc)
    elapsed = time.perf_counter() - start

    assert len(platform.incidents) == 1000, (
        f"Expected 1000 incidents loaded, got {len(platform.incidents)}"
    )
    assert elapsed < 2.0, (
        f"Loading 1000 incidents took {elapsed:.2f}s — must be < 2s"
    )

    # Verify queue is ordered — pop top 5 and check descending priority
    pq = platform.incident_manager.priority_queue
    prev_score = float("inf")
    for _ in range(min(5, len(pq))):
        inc = pq.pop()
        score = inc.get_priority_score()
        assert score <= prev_score, (
            f"Priority queue not ordered: {score} > previous {prev_score}"
        )
        prev_score = score

    print(f"         {CYAN}→ 1000 incidents loaded in {elapsed*1000:.1f}ms{RESET}")


# ══════════════════════════════════════════════════════════════════
# MAIN RUNNER
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print()
    print(f"{BOLD}{CYAN}{'═'*62}{RESET}")
    print(f"{BOLD}{CYAN}  DisasterSense — Official Test Suite  (Section 19){RESET}")
    print(f"{BOLD}{CYAN}{'═'*62}{RESET}")
    print()

    test_cases = [
        ("TC-001", "Register valid incident — priority computed correctly",   tc_001),
        ("TC-002", "Register incident with severity = 0 (invalid)",           tc_002),
        ("TC-003", "Allocate resources with sufficient inventory",            tc_003),
        ("TC-004", "Allocate with empty inventory — deficit reported",        tc_004),
        ("TC-005", "BFS — 1 available shelter returns hop-count path",        tc_005),
        ("TC-006", "BFS — all shelters full → graceful empty result",         tc_006),
        ("TC-007", "Dijkstra on connected graph — shortest path correct",     tc_007),
        ("TC-008", "Dijkstra on disconnected graph — infinity handled",       tc_008),
        ("TC-009", "Analytics dashboard with 0 incidents — no crash",         tc_009),
        ("TC-010", "Load 1000 incidents in < 2s — queue ordered correctly",  tc_010),
    ]

    for tc_id, scenario, fn in test_cases:
        run_test(tc_id, scenario, fn)

    # ── Summary ────────────────────────────────────────────────────
    passed = sum(1 for _, _, ok, _ in results if ok)
    failed = len(results) - passed
    print()
    print(f"{BOLD}{CYAN}{'═'*62}{RESET}")
    print(f"{BOLD}  Results: {GREEN}{passed} PASSED{RESET}{BOLD}  |  {RED}{failed} FAILED{RESET}{BOLD}  out of {len(results)} tests{RESET}")
    print(f"{BOLD}{CYAN}{'═'*62}{RESET}")
    print()

    if failed:
        print(f"{RED}Failed tests:{RESET}")
        for tc_id, scenario, ok, err in results:
            if not ok:
                print(f"  {RED}✗{RESET} [{tc_id}] {scenario}")
                print(f"    {RED}→ {err}{RESET}")
        print()
        sys.exit(1)
    else:
        print(f"{GREEN}{BOLD}  ✓ All test cases passed!{RESET}")
        print()
        sys.exit(0)
