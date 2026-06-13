"""
modules/resource_manager.py - Coordinates resource inventory and allocations.
"""
from models.resource import ResourceInventory
from algorithms.greedy_allocator import GreedyResourceAllocator
from algorithms.priority_queue import IncidentPriorityQueue

class ResourceAllocator:
    """
    Module B: Resource Allocation.
    Manages global stockpiles and coordinates the GreedyResourceAllocator algorithm
    over active disaster incidents.
    """
    def __init__(self, initial_stockpile: dict = None):
        if initial_stockpile is None:
            initial_stockpile = {"food": 120000, "water": 200000, "medical_kits": 2000, "rescue_teams": 50}
        
        self.inventory = ResourceInventory(
            food=initial_stockpile.get("food", 0),
            water=initial_stockpile.get("water", 0),
            medical_kits=initial_stockpile.get("medical_kits", 0),
            rescue_teams=initial_stockpile.get("rescue_teams", 0)
        )
        self.allocation_log: list[dict] = []

    def allocate_greedy(self, incident_manager) -> list[dict]:
        """Wrapper for backward compatibility."""
        return self.allocate_resources(incident_manager, "greedy")

    def allocate_resources(self, incident_manager, strategy: str = "greedy") -> list[dict]:
        """
        Gathers active unallocated or deficit incidents, puts them in a max-heap Priority Queue,
        and runs the selected allocator algorithm (Greedy or DP Knapsack).
        """
        if strategy == "knapsack":
            from algorithms.knapsack_allocator import KnapsackResourceAllocator
            allocator = KnapsackResourceAllocator()
        else:
            from algorithms.greedy_allocator import GreedyResourceAllocator
            allocator = GreedyResourceAllocator()
            
        pq = IncidentPriorityQueue()
        
        for incident in incident_manager.incidents:
            if incident.status.lower() != "resolved":
                if incident.allocated_resources is None:
                    pq.push(incident)
                else:
                    needed = allocator._compute_needs(incident)
                    has_deficit = False
                    for resource, qty in needed.items():
                        if getattr(incident.allocated_resources, resource, 0) < qty:
                            has_deficit = True
                            break
                    if has_deficit:
                        pq.push(incident)
                
        if pq.is_empty():
            return []

        new_allocations = allocator.allocate(pq, self.inventory)
        
        # Enforce logging and updating
        for entry in new_allocations:
            self.log_allocation(entry)
            
        return new_allocations

    def compute_deficit(self, needed: dict, allocated: dict) -> dict:
        """Helper to compute deficit resource count."""
        return {k: needed[k] - allocated.get(k, 0) for k in needed}

    def log_allocation(self, entry: dict):
        """Appends allocation results to history log."""
        self.allocation_log.append(entry)
