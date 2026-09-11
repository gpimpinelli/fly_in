from dataclasses import dataclass, field

@dataclass
class Connection:
    target_zone: Zone
    max_link_capacity: float = float('inf')
