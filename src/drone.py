from pydantic import BaseModel, Field


class Drone(BaseModel):
    """Represents a single drone navigating the zone network."""

    id: str
    current_zone: str
    path: list[str] = Field(default_factory=list)
    in_transit_turns: int = 0
    is_delivered: bool = False
    target_zone: str | None = None

    def is_in_transit(self) -> bool:
        """Check whether the drone is currently mid-flight on a
        multi-turn connection (e.g. toward a restricted zone)."""
        return self.in_transit_turns > 0

    def is_idle(self) -> bool:
        """Check whether the drone is stationary and free to move."""
        return not self.is_in_transit() and not self.is_delivered

    def start_transit(self, target: str, turns: int) -> None:
        """Begin a multi-turn move toward a restricted zone."""
        if self.is_in_transit():
            raise ValueError(f"Drone {self.id} is already in transit.")
        self.target_zone = target
        self.in_transit_turns = turns

    def tick_transit(self) -> None:
        """Advance transit by one turn."""
        if not self.is_in_transit():
            raise ValueError(f"Drone {self.id} is not in transit.")
        self.in_transit_turns -= 1
        if self.in_transit_turns == 0:
            self._complete_transit()

    def _complete_transit(self) -> None:
        """Finalize arrival after transit ends."""
        assert self.target_zone is not None
        self.current_zone = self.target_zone
        self.target_zone = None

    def get_action_target(self) -> str | None:
        """Returns the target to print in this tourn."""
        if self.is_in_transit():
            return f"{self.current_zone}_{self.target_zone}"
        return None

    def move_instant(self, target: str) -> None:
        """Move directly to an adjacent zone costing exactly 1 turn."""
        if self.is_in_transit():
            raise ValueError(f"Drone {self.id} is currently in transit.")
        self.current_zone = target
        self.path.append(target)

    def deliver(self, end_zone: str) -> None:
        """Mark the drone as delivered upon reaching the end zone."""
        if self.current_zone != end_zone:
            raise ValueError(
                f"Drone {self.id} cannot be delivered: "
                f"not at end zone (at '{self.current_zone}')"
            )
        self.is_delivered = True

    def wait(self) -> None:
        """Record a turn spent stationary (no movement)."""
        self.path.append(self.current_zone)
