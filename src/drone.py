from dataclasses import dataclass, field


@dataclass
class Drone:
    drone_id: str
    current_zone: str
    path: list[str] = field(default_factory=list)
    in_transit_turns: int = 0
    is_delivered: bool = False