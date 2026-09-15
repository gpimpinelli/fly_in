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
        """Return True if the drone is mid-flight
         on a multi-turn connection."""
        return self.in_transit_turns > 0

    def start_transit(self, target: str, turns: int) -> None:
        """Begin a multi-turn move toward a restricted zone.

        Args:
            target: Name of the destination zone.
            turns: Number of additional turns required to complete the transit.

        Raises:
            ValueError: If the drone is already in transit.
        """
        if self.is_in_transit():
            raise ValueError(f"Drone {self.id} is already in transit.")
        self.target_zone = target
        self.in_transit_turns = turns

    def tick_transit(self) -> None:
        """Advance the in-flight transit counter by one turn.

        Raises:
            ValueError: If the drone is not currently in transit.
        """
        if not self.is_in_transit():
            raise ValueError(f"Drone {self.id} is not in transit.")
        self.in_transit_turns -= 1
        if self.in_transit_turns == 0:
            self._complete_transit()

    def _complete_transit(self) -> None:
        """Finalize arrival by updating current_zone once transit ends."""
        if self.target_zone is None:
            raise RuntimeError("Cannot complete transit: target_zone is None")
        self.current_zone = self.target_zone
        self.target_zone = None

    def get_action_target(self) -> str | None:
        """Return the transit label for the current turn, or None.

        Returns:
            A string 'origin_destination' while in transit, or None otherwise.
        """
        if self.is_in_transit():
            return f"{self.current_zone}_{self.target_zone}"
        return None

    def move_instant(self, target: str) -> None:
        """Move directly to an adjacent zone in exactly one turn.

        Args:
            target: Name of the destination zone.

        Raises:
            ValueError: If the drone is currently in transit.
        """
        if self.is_in_transit():
            raise ValueError(f"Drone {self.id} is currently in transit.")
        self.current_zone = target
        self.path.append(target)

    def deliver(self, end_zone: str) -> None:
        """Mark the drone as delivered upon reaching the end zone.

        Args:
            end_zone: Name of the expected destination zone.

        Raises:
            ValueError: If the drone is not currently at end_zone.
        """
        if self.current_zone != end_zone:
            raise ValueError(
                f"Drone {self.id} cannot be delivered: "
                f"not at end zone (at '{self.current_zone}')"
            )
        self.is_delivered = True

    def wait(self) -> None:
        """Record a stationary turn by appending the current zone to path."""
        self.path.append(self.current_zone)
