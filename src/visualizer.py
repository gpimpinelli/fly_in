from .drone import Drone
from network_graph import NetworkGraph
from .zone import Zone


class Visualizer:
    """Renders the simulation state, either as colored terminal
    output or as a graphical view."""

    def __init__(self, graph: NetworkGraph) -> None:
        self.graph = graph

    def render_turn(self, turn: int, drones: list[Drone]) -> None:
        """Print colored terminal output for the current turn."""
        ...

    def zone_color(self, zone: Zone) -> str:
        """Return the ANSI color code for a given zone."""
        ...