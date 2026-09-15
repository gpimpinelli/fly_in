class OccupancyTracker:
    """Tracks how many drones occupy each
    zone/connection at each simulation turn."""

    def __init__(self) -> None:
        """Initialize empty occupancy tables for zones and connections."""
        self._zone_occupancy: dict[tuple[str, int], int] = {}
        self._connection_occupancy: dict[tuple[str, str, int], int] = {}

    def zone_count_at(self, zone_name: str, turn: int) -> int:
        """Return how many drones are reserved in this zone at this turn."""
        return self._zone_occupancy.get((zone_name, turn), 0)

    def reserve_zone(self, zone_name: str, turn: int) -> None:
        """Reserve one drone slot in this zone at this turn."""
        key = (zone_name, turn)
        self._zone_occupancy[key] = self._zone_occupancy.get(key, 0) + 1

    def _connection_key(
        self,
        zone_a: str,
        zone_b: str,
        turn: int
    ) -> tuple[str, str, int]:
        """Normalize connection key since connections are bidirectional."""
        node1, node2 = sorted((zone_a, zone_b))
        return (node1, node2, turn)

    def connection_count_at(self, zone_a: str, zone_b: str, turn: int) -> int:
        """Return how many drones are
        traversing this connection at this turn."""
        key = self._connection_key(zone_a, zone_b, turn)
        return self._connection_occupancy.get(key, 0)

    def reserve_connection(self, zone_a: str, zone_b: str, turn: int) -> None:
        """Reserve one drone slot on this connection at this turn."""
        key = self._connection_key(zone_a, zone_b, turn)
        self._connection_occupancy[key] = self._connection_occupancy.get(
            key, 0) + 1
