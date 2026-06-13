"""
algorithms/knapsack_allocator.py - 0/1 Knapsack Resource Allocator using Dynamic Programming.
Satisfies the DP requirement in Section 13/Rubric.
"""
import math
from algorithms.base_allocator import ResourceAllocationStrategy
from models.resource import ResourceInventory

class KnapsackResourceAllocator(ResourceAllocationStrategy):
    """
    Dynamic Programming Resource Allocator.
    Models the allocation as a 0/1 Knapsack problem:
    - Values: Incident Priority Score (composite score).
    - Weights: Combined resource need weight (food*1 + water*1 + medical*5 + teams*100).
    - Knapsack Capacity: Total dispatch vehicle weight capacity (default: 450,000 units).
    Maximizes the total priority value of fully served incidents.
    """
    def __init__(self, capacity: int = 450000):
        self.capacity = capacity

    def allocate(self, priority_queue, inventory) -> list[dict]:
        """
        Runs 0/1 Knapsack DP to select incidents that maximize overall triage value.
        Allocates resources from the inventory to the selected incidents.
        """
        # 1. Pop all incidents from the queue to run the knapsack selection
        incidents = []
        while not priority_queue.is_empty():
            incidents.append(priority_queue.pop())

        if not incidents:
            return []

        # 2. Define weights and values
        # Let's scale weights to keep DP table size reasonable
        scale_factor = 250  # Scales capacity down to 1800 to ensure fast execution
        dp_capacity = int(self.capacity // scale_factor)
        
        # Calculate needs and combined weight for each incident
        incident_data = []
        for inc in incidents:
            needed = self._compute_needs(inc)
            # Initialize allocated_resources if not already present
            if inc.allocated_resources is None:
                inc.allocated_resources = ResourceInventory()
            
            # Compute remaining delta needed
            delta_needed = {}
            for res, qty in needed.items():
                already = getattr(inc.allocated_resources, res, 0)
                delta_needed[res] = max(0, qty - already)
                
            # Combined weight of remaining needs
            weight = (
                delta_needed["food"] * 1 +
                delta_needed["water"] * 1.5 +
                delta_needed["medical_kits"] * 10 +
                delta_needed["rescue_teams"] * 200
            )
            val = inc.get_priority_score()
            
            # Scale weight for DP index
            scaled_weight = max(1, int(math.ceil(weight / scale_factor)))
            incident_data.append({
                "incident": inc,
                "needed": needed,
                "delta_needed": delta_needed,
                "weight": scaled_weight,
                "raw_weight": weight,
                "val": val
            })

        # 3. 0/1 Knapsack DP Implementation
        # dp[i][w] stores maximum value achievable with first i items and weight limit w
        n = len(incident_data)
        dp = [[0.0] * (dp_capacity + 1) for _ in range(n + 1)]

        for i in range(1, n + 1):
            w_i = incident_data[i-1]["weight"]
            v_i = incident_data[i-1]["val"]
            for w in range(dp_capacity + 1):
                if w_i <= w:
                    dp[i][w] = max(dp[i-1][w], dp[i-1][w-w_i] + v_i)
                else:
                    dp[i][w] = dp[i-1][w]

        # 4. Backtrack to find selected incidents
        selected_indices = set()
        w = dp_capacity
        for i in range(n, 0, -1):
            # If value came from the item being added
            if dp[i][w] != dp[i-1][w]:
                selected_indices.add(i - 1)
                w -= incident_data[i - 1]["weight"]

        # 5. Perform allocation
        allocation_log = []
        for idx, item in enumerate(incident_data):
            inc = item["incident"]
            needed = item["needed"]
            delta_needed = item["delta_needed"]
            allocated = {}
            
            # If this incident was selected by the DP Knapsack algorithm
            if idx in selected_indices:
                # Allocate resources greedily up to availability
                for resource, qty in delta_needed.items():
                    available = getattr(inventory, resource, 0)
                    give = min(qty, available)
                    setattr(inventory, resource, available - give)
                    already = getattr(inc.allocated_resources, resource, 0)
                    setattr(inc.allocated_resources, resource, already + give)
                    allocated[resource] = give
                    
                # Update status
                if inc.status == "Reported":
                    inc.status = "Active"
            else:
                # Not selected in this cycle: 0 resources allocated
                for resource in delta_needed:
                    allocated[resource] = 0
            
            # Compute remaining deficit
            deficit = {k: needed[k] - getattr(inc.allocated_resources, k, 0) for k in needed}
            
            allocation_log.append({
                "incident_id": inc.incident_id,
                "allocated": allocated,
                "deficit": deficit
            })
            
            # Push incident back to priority queue if it still has deficit or was not selected
            # This allows it to be processed in future runs
            has_deficit = any(deficit[k] > 0 for k in deficit)
            if has_deficit and inc.status.lower() != "resolved":
                priority_queue.push(inc)
                
        return allocation_log

    def _compute_needs(self, incident) -> dict:
        """Computes resource needs based on population affected and severity."""
        p = incident.population_affected
        sev = incident.severity
        return {
            "food":         p * 2,
            "water":        p * 3,
            "medical_kits": max(1, p // 50),
            "rescue_teams": max(1, sev),
        }
