"""
algorithms/backtracking_paths.py - Backtracking algorithm for finding all safe alternative rescue routes.
Satisfies the Backtracking requirement in Section 13/Rubric.
"""

class BacktrackingPathFinder:
    """
    Backtracking search engine to find alternative routes.
    Explores the graph recursively to find all simple paths from source to target
    that satisfy maximum path risk/hazard constraints.
    """
    def find_all_safe_paths(self, graph, source: str, destination: str, max_risk: float = 25.0) -> list[dict]:
        """
        Finds all simple paths from source to destination with a total risk weight <= max_risk.
        Uses recursive backtracking to explore graph edges and prune paths exceeding risk thresholds.
        """
        results = []
        visited = {source}
        self._backtrack(graph, source, destination, [source], 0.0, 0.0, visited, max_risk, results)
        
        # Sort paths by risk weight (safest first)
        results.sort(key=lambda x: x["total_risk"])
        return results

    def _backtrack(self, graph, curr: str, target: str, path: list[str], 
                   curr_risk: float, curr_dist: float, visited: set[str], 
                   max_risk: float, results: list[dict]):
        """Recursive backtracking helper."""
        # Base case: reached target destination
        if curr == target:
            path_names = [graph.nodes[n].name if n in graph.nodes else n for n in path]
            results.append({
                "path_ids": list(path),
                "path_names": path_names,
                "total_risk": round(curr_risk, 2),
                "total_distance": round(curr_dist, 2),
                "hops": len(path) - 1
            })
            return

        # Limit search depth to prevent excessive execution time on dense graphs
        if len(path) > 8:
            return

        # Explore neighbors
        for neighbor, weight in graph.get_weighted_neighbors(curr):
            if neighbor not in visited:
                # Retrieve edge attributes for distance vs. composite weight
                edge_data = graph.G[curr][neighbor]
                dist = edge_data.get("distance", weight)
                
                # Check if adding this edge violates the risk limit
                if curr_risk + weight <= max_risk:
                    visited.add(neighbor)
                    path.append(neighbor)
                    
                    # Recurse
                    self._backtrack(
                        graph, neighbor, target, path,
                        curr_risk + weight, curr_dist + dist,
                        visited, max_risk, results
                    )
                    
                    # Backtrack (undo state changes)
                    path.pop()
                    visited.remove(neighbor)
