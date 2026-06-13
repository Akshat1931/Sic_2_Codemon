"""
modules/shelter_manager.py - Shelter recommendation coordinator.
"""
from algorithms.bfs_shelter import ShelterFinder as BFSShelterFinder

class ShelterFinder:
    """
    Module C: Shelter Recommendation.
    Binds the location graph and BFS search to recommend available shelters.
    """
    def __init__(self, graph, shelters):
        self.graph = graph
        self.shelters = shelters  # node_id -> ShelterNode dictionary
        self._engine = BFSShelterFinder()

    def bfs_nearest(self, location_id: str) -> dict:
        """Finds the topologically closest available shelter (minimum hops) using BFS."""
        shelters_list = list(self.shelters.values()) if isinstance(self.shelters, dict) else self.shelters
        return self._engine.bfs_nearest(self.graph, location_id, shelters_list)

    def recommend_top3(self, location_id: str) -> list[dict]:
        """Recommends up to 3 nearest available shelters using BFS."""
        shelters_list = list(self.shelters.values()) if isinstance(self.shelters, dict) else self.shelters
        return self._engine.recommend_top3(self.graph, location_id, shelters_list)
