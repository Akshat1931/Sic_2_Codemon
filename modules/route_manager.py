"""
modules/route_manager.py - Coordinates route planning using Dijkstra.
"""
from algorithms.dijkstra_routes import RouteEngine as DijkstraRouteEngine

class RouteEngine:
    """
    Module D: Rescue Route Planning.
    Coordinates route searches, route reports, and coordinate generation.
    """
    def __init__(self, graph):
        self.graph = graph
        self._engine = DijkstraRouteEngine()
        from algorithms.backtracking_paths import BacktrackingPathFinder
        self._backtracker = BacktrackingPathFinder()

    def dijkstra(self, src: str, dst: str) -> tuple[list[str], float]:
        """Calculates shortest weighted route between src and dst. Returns (path, weight)."""
        return self._engine.dijkstra(self.graph, src, dst)

    def get_rescue_route(self, src: str, dst: str) -> dict:
        """Returns details about the shortest route (path node IDs, names, total cost, hops)."""
        return self._engine.get_rescue_route(self.graph, src, dst)

    def get_alternative_paths(self, src: str, dst: str, max_risk: float = 35.0) -> list[dict]:
        """Finds alternative rescue routes using backtracking and pruning."""
        return self._backtracker.find_all_safe_paths(self.graph, src, dst, max_risk)

    def visualize_route(self, path: list[str]) -> list[tuple[float, float]]:
        """Returns GPS coordinates for all nodes in the path to draw on maps."""
        return self._engine.visualize_route(self.graph, path)
