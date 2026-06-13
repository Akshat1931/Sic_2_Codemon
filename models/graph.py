"""
models/graph.py - Network representation using NetworkX.
"""
import networkx as nx
import heapq
from collections import deque
from .location import GraphNode, ShelterNode

class DisasterGraph:
    """
    Weighted undirected graph representing the geographic locations and navigable routes.
    Wraps NetworkX Graph for structural representation and implements Dijkstra & BFS algorithms.
    """
    def __init__(self):
        self.G = nx.Graph()
        self.nodes = {}  # node_id -> GraphNode / ShelterNode object

    def add_location(self, node_id: str, name: str, lat: float, lon: float, is_shelter: bool = False, capacity: int = 0, description: str = ""):
        """Adds a location node to both our OOP model registry and the NetworkX graph."""
        if is_shelter:
            node = ShelterNode(name, capacity, node_id, lat=lat, lon=lon, description=description)
        else:
            # Determine node type from name
            if "HQ" in name or "Command" in name:
                node_type = "HQ"
            elif "Depot" in name or "Logistics" in name:
                node_type = "Depot"
            elif "Shelter" in name:
                node_type = "Shelter"
            else:
                node_type = "Affected Zone"
            node = GraphNode(node_id, name, lat, lon, node_type, description)
            
        self.nodes[node_id] = node
        
        # Add to NetworkX Graph
        self.G.add_node(
            node_id,
            name=name,
            lat=lat,
            lon=lon,
            is_shelter=is_shelter,
            capacity=capacity,
            occupancy=0,
            loc_type=node.loc_type,
            description=description
        )

    def add_route(self, u: str, v: str, distance_km: float, 
                  road_condition_factor: float = 1.0, 
                  flood_risk_factor: float = 1.0, 
                  time_of_day_factor: float = 1.0):
        """Adds a weighted route edge between u and v in the NetworkX graph with composite weights (Section 9.1)."""
        weight = distance_km * road_condition_factor * flood_risk_factor * time_of_day_factor
        self.G.add_edge(
            u, v, 
            weight=weight, 
            distance=distance_km, 
            road_condition_factor=road_condition_factor,
            flood_risk_factor=flood_risk_factor,
            time_of_day_factor=time_of_day_factor
        )

    def get_neighbors(self, node: str) -> list[str]:
        """Returns neighbor node IDs."""
        return list(self.G.neighbors(node))

    def get_weighted_neighbors(self, node: str) -> list[tuple[str, float]]:
        """Returns list of (neighbor_id, weight) tuples."""
        return [(neighbor, data.get("weight", 1.0)) for neighbor, data in self.G[node].items()]

    def get_available_shelters(self) -> list[str]:
        """Returns node IDs of shelters that are not fully occupied."""
        return [n for n, d in self.G.nodes(data=True)
                if d.get("is_shelter") and d.get("occupancy", 0) < d.get("capacity", 0)]

    # ── Dijkstra's Algorithm from Scratch ──────────────────────────
    def dijkstra(self, source: str, target: str = None) -> tuple[dict, dict]:
        """Returns (dist, prev) dictionaries containing shortest paths from source."""
        from models.exceptions import NodeNotFoundError, RoutingError
        if source not in self.G.nodes:
            raise NodeNotFoundError(f"Source node '{source}' not found in graph.")
        if target and target not in self.G.nodes:
            raise NodeNotFoundError(f"Target node '{target}' not found in graph.")
        if target and source == target:
            raise RoutingError("Source and target must differ.")
            
        dist = {node: float("inf") for node in self.G.nodes}
        prev = {node: None for node in self.G.nodes}
        dist[source] = 0.0
        pq = [(0.0, source)]
        
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            if target and u == target:
                break
            for v, weight in self.get_weighted_neighbors(u):
                alt = dist[u] + weight
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
                    heapq.heappush(pq, (alt, v))
        return dist, prev

    def shortest_path(self, source: str, target: str) -> tuple[list[str], float]:
        """Returns (path_nodes, total_cost)."""
        dist, prev = self.dijkstra(source, target)
        if dist[target] == float("inf"):
            return [], float("inf")
        path = []
        curr = target
        while curr is not None:
            path.append(curr)
            curr = prev[curr]
        path.reverse()
        return path, dist[target]

    # ── BFS from Scratch ───────────────────────────────────────────
    def bfs_nearest_shelters(self, source: str, shelter_ids: set[str], max_results: int = 5) -> list[tuple[str, int]]:
        """BFS from source to find nearest shelter locations in terms of network hops."""
        visited = {source}
        queue = deque([(source, 0)])
        results = []
        
        while queue and len(results) < max_results:
            node, hops = queue.popleft()
            if node in shelter_ids and node != source:
                results.append((node, hops))
            for neighbor in self.get_neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, hops + 1))
        return results

    # ── Serializers ────────────────────────────────────────────────
    def all_nodes_list(self):
        """Returns list of dictionaries representing nodes."""
        return [n.to_dict() for n in self.nodes.values()]

    def all_edges_list(self):
        """Returns list of dictionaries representing unique edges."""
        seen = set()
        edges = []
        for u, neighbors in self.G.adjacency():
            for v, data in neighbors.items():
                key = tuple(sorted([u, v]))
                if key not in seen:
                    seen.add(key)
                    edges.append({
                        "from": u,
                        "to": v,
                        "weight": round(data.get("weight", 1.0), 2),
                        "distance": round(data.get("distance", data.get("weight", 1.0)), 2),
                        "road_condition_factor": data.get("road_condition_factor", 1.0),
                        "flood_risk_factor": data.get("flood_risk_factor", 1.0),
                        "time_of_day_factor": data.get("time_of_day_factor", 1.0)
                    })
        return edges
