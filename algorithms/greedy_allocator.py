"""
algorithms/greedy_allocator.py - Greedy resource allocation algorithm.

Uses a two-pass approach:
  Pass 1 — Compute total demand across ALL active incidents.
  Pass 2 — Distribute each resource proportionally by priority score,
            capping each incident at its actual need, then deduct from inventory.

This ensures every incident receives a fair share relative to its priority
rather than draining the entire stockpile into the single highest-priority case.
"""

from algorithms.base_allocator import ResourceAllocationStrategy


class GreedyResourceAllocator(ResourceAllocationStrategy):
    """
    Greedy Resource Allocator — Priority-Proportional Distribution.

    Processes incidents in priority order and distributes available resources
    proportionally by priority score. Each incident receives at most its
    computed need, ensuring fairer multi-incident coverage.
    """

    RESOURCES = ["food", "water", "medical_kits", "rescue_teams"]

    def allocate(self, priority_queue, inventory):
        """
        Allocates resources from inventory to incidents via proportional sharing.

        Steps:
          1. Drain the priority queue into a sorted list.
          2. Compute each incident's needs and total demand per resource.
          3. For each resource, calculate each incident's proportional share
             (capped at its own need) and deduct from inventory.
          4. Return an allocation log with allocated amounts and deficits.
        """
        from models.resource import ResourceInventory

        allocation_log = []

        # ── 1. Collect all incidents from priority queue (highest priority first)
        incidents = []
        while not priority_queue.is_empty():
            incidents.append(priority_queue.pop())

        if not incidents:
            return []

        # ── 2. Compute per-incident needs and ensure allocated_resources exists
        needs_list = []
        for inc in incidents:
            needed = self._compute_needs(inc)
            if inc.allocated_resources is None:
                inc.allocated_resources = ResourceInventory()
            # Only count the remaining delta still needed
            delta = {}
            for res in self.RESOURCES:
                already = getattr(inc.allocated_resources, res, 0)
                delta[res] = max(0, needed[res] - already)
            needs_list.append((inc, needed, delta))

        # ── 3. Priority-proportional distribution per resource
        # Calculate each incident's share weight = priority_index
        priority_scores = [max(inc.priority_index, 0.01) for (inc, _, _) in needs_list]
        total_priority = sum(priority_scores)

        allocated_per_incident = [{res: 0 for res in self.RESOURCES} for _ in incidents]

        for res in self.RESOURCES:
            available = getattr(inventory, res, 0)
            if available <= 0:
                continue

            # Total demand across all incidents for this resource
            total_demand = sum(delta[res] for (_, _, delta) in needs_list)
            if total_demand <= 0:
                continue

            remaining = available
            for i, (inc, needed, delta) in enumerate(needs_list):
                if delta[res] <= 0:
                    continue
                # Priority-weighted share of available stock, capped at actual need
                share = (priority_scores[i] / total_priority) * available
                give = min(share, delta[res], remaining)
                give = max(0, int(give))  # round down to integer units
                allocated_per_incident[i][res] = give
                remaining -= give

            # Distribute any remaining units (due to int rounding) to highest-priority incidents
            if remaining > 0:
                for i, (inc, needed, delta) in enumerate(needs_list):
                    still_needed = delta[res] - allocated_per_incident[i][res]
                    if still_needed > 0 and remaining > 0:
                        extra = min(int(remaining), int(still_needed))
                        allocated_per_incident[i][res] += extra
                        remaining -= extra
                        if remaining <= 0:
                            break

            # Deduct total allocated from inventory
            total_given = sum(allocated_per_incident[i][res] for i in range(len(incidents)))
            current = getattr(inventory, res, 0)
            setattr(inventory, res, max(0, current - total_given))

        # ── 4. Apply allocations and build log
        for i, (inc, needed, delta) in enumerate(needs_list):
            alloc = allocated_per_incident[i]
            for res in self.RESOURCES:
                already = getattr(inc.allocated_resources, res, 0)
                setattr(inc.allocated_resources, res, already + alloc[res])

            # Promote to Active
            if inc.status == "Reported":
                inc.status = "Active"

            # Compute deficit against full need
            deficit = {res: needed[res] - getattr(inc.allocated_resources, res, 0) for res in self.RESOURCES}

            allocation_log.append({
                "incident_id": inc.incident_id,
                "allocated": alloc,
                "deficit": deficit,
            })

        return allocation_log

    def _compute_needs(self, incident) -> dict:
        """
        Computes resource needs based on population affected and severity.
        Caps per-capita consumption to keep numbers realistic against the stockpile.
        """
        p = incident.population_affected
        sev = incident.severity  # 2-5

        return {
            "food":         p * 2,               # 2 units per person
            "water":        p * 3,               # 3 litres per person
            "medical_kits": max(1, p // 50),     # 1 kit per 50 people
            "rescue_teams": max(1, sev),         # proportional to severity level
        }
