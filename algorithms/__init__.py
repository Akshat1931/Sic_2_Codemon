"""
algorithms package initialization - exports custom DSA classes.
"""
from .priority_queue import IncidentPriorityQueue
from .greedy_allocator import GreedyResourceAllocator
from .bfs_shelter import ShelterFinder
from .dijkstra_routes import RouteEngine

__all__ = [
    "IncidentPriorityQueue",
    "GreedyResourceAllocator",
    "ShelterFinder",
    "RouteEngine"
]
