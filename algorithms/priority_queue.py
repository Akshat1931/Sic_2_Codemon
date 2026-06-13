"""
algorithms/priority_queue.py - Max-heap priority queue for incident triage.
"""
import heapq
from config import DISASTER_WEIGHTS

class IncidentPriorityQueue:
    """
    Max-heap Priority Queue to triage incoming disaster incidents.
    Priority is computed as: Severity (1-5) * Population Affected * Type Weight.
    """
    def __init__(self):
        self._heap = []
        self._counter = 0  # Tie-breaker

    def push(self, incident):
        """Pushes an incident onto the priority queue based on computed priority score."""
        score = self._compute_priority(incident)
        # Python's heapq is a min-heap; we negate the score for max-heap behavior.
        heapq.heappush(self._heap, (-score, self._counter, incident))
        self._counter += 1

    def pop(self):
        """Pops and returns the highest priority incident."""
        if self.is_empty():
            raise IndexError("pop from an empty priority queue")
        neg_score, _, incident = heapq.heappop(self._heap)
        return incident

    def is_empty(self) -> bool:
        """Returns True if the queue is empty."""
        return len(self._heap) == 0

    def __len__(self) -> int:
        return len(self._heap)

    def _compute_priority(self, incident) -> float:
        """Computes the priority score: Severity * Population Affected * Type Weight."""
        w = DISASTER_WEIGHTS.get(incident.disaster_type.lower(), 1.0)
        return incident.severity * incident.population_affected * w
