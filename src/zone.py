from dataclasses import dataclass, field

@dataclass
class Zone:
    name: str
    x: int
    y: int
    color: str = "white"
    zone_type: str = "normal"
    max_drones: float = float('inf') 
    connections: list[Connection] = field(default_factory=list)

    @property
    def neighbors(self) -> list[str]:
        return [connection.target_zone for connection in self.connections]