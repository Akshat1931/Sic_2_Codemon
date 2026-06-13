"""
modules/platform_orchestrator.py - Triage engine and central platform coordinator.
"""
from models.graph import DisasterGraph
from modules.incident_manager import IncidentManager
from modules.resource_manager import ResourceAllocator
from modules.shelter_manager import ShelterFinder
from modules.route_manager import RouteEngine
from modules.analytics import AnalyticsDashboard
from data.simulation import bootstrap_platform

class DisasterPlatform:
    """
    Central orchestrator tying all functional modules (A, B, C, D, E) together.
    Serves as the core engine for both the Tkinter GUI and FastAPI app.
    """
    def __init__(self, bootstrap: bool = True):
        self.graph = DisasterGraph()
        self.incident_manager = IncidentManager()
        self.resource_allocator = ResourceAllocator()
        
        # Registries and managers wrapping graph/incident properties
        self.shelters = {}  # node_id -> ShelterNode
        self.shelter_finder = ShelterFinder(self.graph, self.shelters)
        self.route_engine = RouteEngine(self.graph)
        self.analytics_dashboard = AnalyticsDashboard()
        
        if bootstrap:
            bootstrap_platform(self)

    # ── Compatibility Aliases for FastAPI / existing API ──────────────────
    @property
    def incidents(self) -> list:
        return self.incident_manager.incidents

    @property
    def dispatch_queue(self):
        return self.incident_manager.dispatch_queue

    @property
    def global_inventory(self):
        return self.resource_allocator.inventory

    @property
    def allocation_log(self) -> list[dict]:
        return self.resource_allocator.allocation_log

    def report_incident(self, location_id: str, disaster_type: str, severity, population_affected: int, description: str = "", reporter: str = "Anonymous"):
        """Registers a new incident on the platform."""
        from models.incident import DisasterIncident
        node = self.graph.nodes.get(location_id)
        if not node:
            raise ValueError(f"Location '{location_id}' not found in graph.")
        coords = (node.lat, node.lng)
        inc = DisasterIncident(location_id, disaster_type, severity, population_affected, description, reporter, coordinates=coords)
        self.incident_manager.register(inc)
        return inc

    def get_incident(self, incident_id: str):
        """Finds incident by ID."""
        return next((i for i in self.incidents if i.incident_id == incident_id), None)

    def resolve_incident(self, incident_id: str) -> bool:
        """Marks an incident as resolved."""
        inc = self.get_incident(incident_id)
        if inc:
            # Transition step-by-step to satisfy StateTransitionError constraints
            if inc.status.lower() == "reported":
                inc.status = "Active"
            if inc.status.lower() == "active":
                inc.status = "Contained"
            if inc.status.lower() == "contained":
                inc.status = "Resolved"
            return True
        return False

    def greedy_allocate_resources(self, strategy: str = "greedy") -> list[dict]:
        """Runs the resource allocation algorithm (Greedy or DP Knapsack) and enriches the results for compatibility."""
        raw_logs = self.resource_allocator.allocate_resources(self.incident_manager, strategy)
        enriched = []
        for entry in raw_logs:
            inc = self.get_incident(entry["incident_id"])
            loc_name = self.graph.nodes[inc.location].name if inc.location in self.graph.nodes else inc.location
            enriched_entry = {
                "incident_id": inc.incident_id,
                "location": loc_name,
                "severity": inc.severity_level_str,
                "priority_index": round(inc.priority_index, 2),
                "allocated": inc.allocated_resources.to_dict() if inc.allocated_resources else entry["allocated"],
                "remaining_stock": self.global_inventory.to_dict(),
                "deficit": entry["deficit"]
            }
            enriched.append(enriched_entry)
            
        # Update resource allocator's log with the enriched versions
        self.resource_allocator.allocation_log.clear()
        self.resource_allocator.allocation_log.extend(enriched)
        return enriched

    def recommend_shelters(self, incident_id: str, max_results: int = 4) -> list[dict]:
        """Finds BFS recommended shelters with path routing details."""
        inc = self.get_incident(incident_id)
        if not inc:
            raise ValueError(f"Incident {incident_id} not found.")
            
        recs = self.shelter_finder.recommend_top3(inc.location)
        results = []
        for r in recs[:max_results]:
            shelter = r["shelter"]
            hops = r["hops"]
            
            # Dijkstra path for distance
            path_ids, cost = self.route_engine.dijkstra(inc.location, shelter.node_id)
            path_names = [self.graph.nodes[nid].name for nid in path_ids if nid in self.graph.nodes]
            
            results.append({
                "shelter_id": shelter.shelter_id,
                "name": shelter.name,
                "node_id": shelter.node_id,
                "bfs_hops": hops,
                "distance_km": round(cost, 2),
                "available_capacity": shelter.available_capacity,
                "occupancy_pct": round(shelter.occupancy_pct, 1),
                "path": path_names,
                "path_ids": path_ids,
                "lat": shelter.lat,
                "lng": shelter.lng,
            })
        return results

    def plan_rescue_route(self, source_id: str, target_id: str) -> dict:
        """Plans the shortest hazard-adjusted route between source and target using Dijkstra."""
        return self.route_engine.get_rescue_route(source_id, target_id)

    def plan_alternative_routes(self, source_id: str, target_id: str, max_risk: float = 35.0) -> list[dict]:
        """Plans alternative paths using backtracking under a risk limit."""
        return self.route_engine.get_alternative_paths(source_id, target_id, max_risk)

    def dequeue_incident(self):
        """Dequeues the oldest reported incident."""
        if self.dispatch_queue:
            inc = self.dispatch_queue.popleft()
            if inc.status == "Reported":
                inc.status = "Active"
            return inc.to_dict()
        return None

    def queue_status(self) -> list[dict]:
        """Returns the list of incidents in the FIFO queue."""
        return [i.to_dict() for i in self.dispatch_queue]

    def generate_map(self, highlight_path=None, highlight_shelters=None) -> str:
        """Generates interactive Folium HTML map."""
        return self.analytics_dashboard.export_folium_map(self.graph, self.incidents, self.shelters, highlight_path, highlight_shelters)

    def get_analytics(self) -> dict:
        """Returns statistical summary dict."""
        return self.analytics_dashboard.show_stats(self.incidents, self.global_inventory)

    def generate_charts(self) -> dict[str, str]:
        """Returns dictionary of base64 PNG charts."""
        return self.analytics_dashboard.render_charts(self.incidents, self.global_inventory)

    def export_pdf_report(self, filepath: str):
        """Generates a PDF incident report."""
        self.incident_manager.export_report_pdf(filepath)
