from pydantic import BaseModel, Field
from enum import Enum


class Connection(BaseModel):
    target: str
    max_link_capacity: int = Field(default=1, gt=0)


class ZoneType(str, Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Zone(BaseModel):
    name: str
    x: int
    y: int
    color: str = "white"
    zone_type: ZoneType = ZoneType.NORMAL
    max_drones: int = Field(default=1, gt=0)
    connections: list[Connection] = Field(default_factory=list)


class NetworkGraph(BaseModel):
    zones: dict[str, Zone] = Field(default_factory=dict)
    nb_drones: int = 0
    start_node: str = ""
    end_node: str = ""