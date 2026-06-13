"""
algorithms/base_allocator.py - Abstract Base Class for resource allocation strategies.
Establishes OOP polymorphism for resource allocation.
"""
from abc import ABC, abstractmethod

class ResourceAllocationStrategy(ABC):
    """
    Abstract base class defining the interface for resource allocation strategies.
    Enables polymorphic switching between Greedy and Dynamic Programming allocators.
    """
    @abstractmethod
    def allocate(self, priority_queue, inventory) -> list[dict]:
        """
        Allocates resources from the inventory to incidents in the priority queue.
        Modifies inventory in place and returns a log of allocations.
        """
        pass
