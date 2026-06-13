"""
models/resource.py - Resource stockpile representation and operations.
"""

class ResourceInventory:
    """Tracks stockpile of critical disaster response resources."""
    def __init__(self, food: int = 0, water: int = 0, medical_kits: int = 0, rescue_teams: int = 0, location_id: str = ""):
        self.food = food
        self.water = water
        self.medical_kits = medical_kits
        self.rescue_teams = rescue_teams
        self.location_id = location_id

    def allocate(self, needs: "ResourceInventory") -> "ResourceInventory":
        """Deducts resource needs from stockpile. Returns the allocated quantities."""
        allocated = ResourceInventory(
            food=min(self.food, needs.food),
            water=min(self.water, needs.water),
            medical_kits=min(self.medical_kits, needs.medical_kits),
            rescue_teams=min(self.rescue_teams, needs.rescue_teams),
        )
        self.deduct(allocated)
        return allocated

    def deduct(self, other: "ResourceInventory"):
        """Directly subtracts resource quantities, floor-capped at 0."""
        self.food = max(0, self.food - other.food)
        self.water = max(0, self.water - other.water)
        self.medical_kits = max(0, self.medical_kits - other.medical_kits)
        self.rescue_teams = max(0, self.rescue_teams - other.rescue_teams)

    def restock(self, items):
        """Adds resources. Can accept a dictionary or ResourceInventory instance."""
        if isinstance(items, ResourceInventory):
            self.food += items.food
            self.water += items.water
            self.medical_kits += items.medical_kits
            self.rescue_teams += items.rescue_teams
        else:
            self.food += items.get("food", 0)
            self.water += items.get("water", 0)
            self.medical_kits += items.get("medical_kits", 0)
            self.rescue_teams += items.get("rescue_teams", 0)

    def get_deficit(self, needs: "ResourceInventory") -> dict:
        """Returns the resource deficit if stockpile is insufficient to meet needs."""
        return {
            "food": max(0, needs.food - self.food),
            "water": max(0, needs.water - self.water),
            "medical_kits": max(0, needs.medical_kits - self.medical_kits),
            "rescue_teams": max(0, needs.rescue_teams - self.rescue_teams),
        }

    def has_sufficient(self, other: "ResourceInventory") -> bool:
        """Returns True if self has at least as many resources in every category as other."""
        return (self.food >= other.food and
                self.water >= other.water and
                self.medical_kits >= other.medical_kits and
                self.rescue_teams >= other.rescue_teams)

    def total(self) -> int:
        """Returns the total number of items across all categories."""
        return self.food + self.water + self.medical_kits + self.rescue_teams

    def to_dict(self):
        return {
            "food": self.food,
            "water": self.water,
            "medical_kits": self.medical_kits,
            "rescue_teams": self.rescue_teams,
            "location_id": self.location_id,
        }

    def __repr__(self):
        return (f"ResourceInventory(food={self.food}, water={self.water}, "
                f"medical={self.medical_kits}, teams={self.rescue_teams})")
