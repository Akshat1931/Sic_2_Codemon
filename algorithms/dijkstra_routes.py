"""
algorithms/dijkstra_routes.py - Dijkstra's algorithm for shortest/safest route planning.
"""
import heapq

class RouteEngine:
    """
    Route Engine to calculate the shortest and safest paths between locations.
    Edge weights represent distance adjusted by road condition and flood risks.
    """
    def dijkstra(self, graph, source, destination):
        """
        Finds the shortest weighted path from source to destination.
        Matches Section 5.4 code snippet.
        """
        from models.exceptions import NodeNotFoundError, RoutingError
        if source not in graph.nodes:
            raise NodeNotFoundError(f"Source node '{source}' not found in graph.")
        if destination not in graph.nodes:
            raise NodeNotFoundError(f"Target node '{destination}' not found in graph.")
        if source == destination:
            raise RoutingError("Source and target must differ.")

        dist = {node: float("inf") for node in graph.nodes}
        prev = {node: None for node in graph.nodes}
        dist[source] = 0
        pq = [(0, source)]
        
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            for v, weight in graph.get_weighted_neighbors(u):
                alt = dist[u] + weight
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
                    heapq.heappush(pq, (alt, v))
                    
        return self._reconstruct_path(prev, source, destination), dist[destination]

    def _reconstruct_path(self, prev, src, dst):
        """Reconstructs the path from the prev dictionary (from Section 5.4)."""
        path, node = [], dst
        while node is not None:
            path.append(node)
            node = prev[node]
        # If path only contains destination and it is not source, there is no path
        if len(path) == 1 and path[0] != src:
            return []
        return list(reversed(path))

    def get_rescue_route(self, graph, src, dst) -> dict:
        """Returns details about the shortest route (path node IDs, names, total cost, hops)."""
        path, cost = self.dijkstra(graph, src, dst)
        if not path or cost == float("inf"):
            return {"error": "No route found", "path_ids": [], "total_cost": None, "hops": 0}
            
        path_names = []
        for node_id in path:
            node = graph.nodes.get(node_id)
            path_names.append(node.name if node else node_id)
            
        return {
            "source": graph.nodes[src].name if src in graph.nodes else src,
            "target": graph.nodes[dst].name if dst in graph.nodes else dst,
            "path_ids": path,
            "path_names": path_names,
            "total_cost": round(cost, 2),
            "hops": len(path) - 1
        }

    def visualize_route(self, graph, path) -> list[tuple[float, float]]:
        """Returns GPS coordinates for all nodes in the path to draw on maps."""
        coords = []
        for node_id in path:
            node = graph.nodes.get(node_id)
            if node:
                coords.append((node.lat, node.lng))
        return coords
