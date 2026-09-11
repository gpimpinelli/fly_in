from pydantic import BaseModel, Field


class Connection(BaseModel):
    target: str
    max_link_capacity: int = 1

class Zone(BaseModel):
    name: str
    x: int
    y: int
    color: str = "white"
    zone_type: str = "normal"
    max_drones: float = float('inf')
    connections: list[Connection] = Field(default_factory=list)

class NetworkGraph(BaseModel):
    zones: dict[str, Zone] = Field(default_factory=dict)
    nb_drones: int = 0
    start_node: str = ""
    end_node: str = ""