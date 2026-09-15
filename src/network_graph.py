from pydantic import BaseModel, Field
from enum import Enum


class Connection(BaseModel):
    """Represent the connection beetween."""
    target: str
    max_link_capacity: int = Field(default=1, gt=0)

    def leads_to(self, zone_name: str) -> bool:
        """Check whether this connection leads to the given zone."""
        return self.target == zone_name


class ZoneType(str, Enum):
    """Reppresent the type of zone."""
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Zone(BaseModel):
    """Represents a single zone of the network."""
    name: str
    x: int
    y: int
    color: str = "white"
    zone_type: ZoneType = ZoneType.NORMAL
    max_drones: int = Field(default=1, gt=0)
    connections: list[Connection] = Field(default_factory=list)

    def is_blocked(self) -> bool:
        return self.zone_type == ZoneType.BLOCKED

    def is_restricted(self) -> bool:
        return self.zone_type == ZoneType.RESTRICTED

    def is_priority(self) -> bool:
        return self.zone_type == ZoneType.PRIORITY

    def movement_cost(self) -> int:
        """Return the turn cost to enter this zone."""
        return 2 if self.zone_type == ZoneType.RESTRICTED else 1

    def decision_weight(self) -> float:
        """Restituisce il peso usato da heapq per favorire le zone priority."""
        if self.zone_type == ZoneType.RESTRICTED:
            return 2.0
        elif self.zone_type == ZoneType.PRIORITY:
            return 0.1
        return 1.0

    def get_connection_to(self, target_name: str) -> Connection | None:
        """Return the connection to a given target zone, if any."""
        for c in self.connections:
            if c.leads_to(target_name):
                return c
        return None


class NetworkGraph(BaseModel):
    zones: dict[str, Zone] = Field(default_factory=dict)
    nb_drones: int = 0
    start_node: str = ""
    end_node: str = ""

    def get_zone(self, name: str) -> Zone:
        if name not in self.zones:
            raise KeyError(f"Zone '{name}' does not exist in the network")
        return self.zones[name]

    def neighbors(self, zone_name: str) -> list[Connection]:
        return self.get_zone(zone_name).connections

    def get_connection(self, a: str, b: str) -> Connection | None:
        return self.get_zone(a).get_connection_to(b)

    def is_valid_connection(self, a: str, b: str) -> bool:
        return isinstance(self.get_zone(a).get_connection_to(b), Connection)

    def has_capacity(self, zone_name: str, current_occupancy: int) -> bool:
        if self.is_start_or_end(zone_name):
            return True
        return current_occupancy < self.get_zone(zone_name).max_drones

    def is_blocked(self, zone_name: str) -> bool:
        """Check whether a zone is of type BLOCKED (cannot be entered)."""
        return self.get_zone(zone_name).is_blocked()

    def is_start_or_end(self, zone_name: str) -> bool:
        return zone_name in (self.start_node, self.end_node)
