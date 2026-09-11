from dataclasses import dataclass, field

@dataclass
class NetworkGraph:
    zones: dict[str, 'Zone'] = field(default_factory=dict)
    nb_drones: int = 0
    start_node: str = ""
    end_node: str = ""
