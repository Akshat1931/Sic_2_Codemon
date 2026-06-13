"""
models/location.py - Geographic node and shelter representations.
"""

class GraphNode:
    """Represents a geographic node in the disaster response network."""
    def __init__(self, node_id: str, name: str, lat: float, lon: float, node_type: str, description: str = ""):
        self.node_id = node_id
        self.name = name
        self.lat = lat
        self.lon = lon
        self.node_type = node_type  # HQ, Depot, Shelter, Affected Zone
        self.description = description

    @property
    def lng(self) -> float:
        return self.lon

    @lng.setter
    def lng(self, val: float):
        self.lon = val

    @property
    def loc_type(self) -> str:
        return self.node_type

    @loc_type.setter
    def loc_type(self, val: str):
        self.node_type = val

    def to_dict(self):
        return {
            "node_id": self.node_id,
            "name": self.name,
            "loc_type": self.loc_type,
            "node_type": self.node_type,
            "lat": self.lat,
            "lng": self.lng,
            "lon": self.lon,
            "description": self.description,
        }

    def __repr__(self):
        return f"GraphNode({self.node_id}, {self.name}, {self.node_type})"


class ShelterNode(GraphNode):
    """A safe haven evacuation site with capacity and resource tracking."""
    _counter = 0

    def __init__(self, name: str, capacity: int, node_id: str, supplies = None, lat: float = 0.0, lon: float = 0.0, description: str = ""):
        # Increment counter to auto-generate shelter_id (e.g. SH001)
        ShelterNode._counter += 1
        self.shelter_id = f"SH{ShelterNode._counter:03d}"
        
        # Call base constructor
        super().__init__(node_id, name, lat, lon, "Shelter", description)
        
        self.capacity = capacity
        self.occupancy = 0
        self.location = node_id  # Reference to the location node ID
        
        # Late import to prevent circular dependency
        from .resource import ResourceInventory
        self.supplies = supplies or ResourceInventory(food=100, water=200, medical_kits=50, rescue_teams=5)

    @property
    def current_occupancy(self) -> int:
        return self.occupancy

    @current_occupancy.setter
    def current_occupancy(self, value: int):
        self.occupancy = value

    def is_available(self) -> bool:
        """Checks if the shelter has remaining vacancy."""
        return self.occupancy < self.capacity

    def get_vacancy(self) -> int:
        """Returns the number of remaining vacancies."""
        return max(0, self.capacity - self.occupancy)

    def update_occupancy(self, count: int) -> int:
        """Admit a count of people. Returns number of people actually admitted."""
        admitted = min(count, self.get_vacancy())
        self.occupancy += admitted
        return admitted

    # Aliases to match index.html expectations
    @property
    def available_capacity(self) -> int:
        return self.get_vacancy()

    @property
    def occupancy_pct(self) -> float:
        return (self.occupancy / self.capacity * 100) if self.capacity > 0 else 0.0

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "shelter_id": self.shelter_id,
            "capacity": self.capacity,
            "occupancy": self.occupancy,
            "available_capacity": self.available_capacity,
            "occupancy_pct": round(self.occupancy_pct, 1),
            "supplies": self.supplies.to_dict() if hasattr(self.supplies, "to_dict") else self.supplies,
        })
        return d
