"""
algorithms/bfs_shelter.py - BFS-based shelter recommendation algorithm.
"""
from collections import deque

class ShelterFinder:
    """
    Shelter recommendation engine.
    Explores the location graph level-by-level to recommend the topologically closest available shelters.
    """
    def bfs_nearest(self, graph, start_node, shelters):
        """
        Finds the topologically closest available shelter (minimum hops) using BFS.
        Matches Section 5.3 code snippet.
        """
        visited = set()
        queue = deque([(start_node, [start_node])])
        shelter_ids = {s.node_id for s in shelters if s.is_available()}
        
        while queue:
            node, path = queue.popleft()
            if node in visited:
                continue
            visited.add(node)

            if node in shelter_ids and node != start_node:
                shelter = self._get_shelter(node, shelters)
                return {'shelter': shelter, 'path': path, 'hops': len(path) - 1}

            for neighbor in graph.get_neighbors(node):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
                    
        return None  # No available shelter reachable

    def _get_shelter(self, node_id, shelters):
        """Finds a shelter object by node_id in a list or dict of shelters."""
        if isinstance(shelters, dict):
            return shelters.get(node_id)
        for s in shelters:
            if s.node_id == node_id:
                return s
        return None

    def recommend_top3(self, graph, start_node, shelters) -> list[dict]:
        """
        Traverses the graph using BFS to find the top 3 closest available shelters.
        Returns a list of dicts with shelter details, path, and hops.
        """
        visited = set()
        queue = deque([(start_node, [start_node])])
        shelter_ids = {s.node_id for s in shelters if s.is_available()}
        recommendations = []
        
        while queue and len(recommendations) < 3:
            node, path = queue.popleft()
            if node in visited:
                continue
            visited.add(node)

            if node in shelter_ids and node != start_node:
                shelter = self._get_shelter(node, shelters)
                recommendations.append({
                    "shelter": shelter,
                    "path": path,
                    "hops": len(path) - 1
                })

            for neighbor in graph.get_neighbors(node):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
                    
        return recommendations
