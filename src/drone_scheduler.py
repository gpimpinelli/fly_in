from .network_graph import NetworkGraph
from .occupancy_tracker import OccupancyTracker
from .path_finder import Pathfinder
from .drone import Drone


class DroneScheduler:
    """Offline pre-compute scheduler.

    For each drone in order, asks the Pathfinder for the cheapest path that
    avoids already-reserved slots (zone+turn and connection+turn).
    After finding a valid path, reserves all its slots so the next drone
    must route around them automatically.
    """

    def __init__(
        self,
        graph: NetworkGraph,
        pathfinder: Pathfinder,
        occupancy: OccupancyTracker,
    ) -> None:
        """Initialize the scheduler."""
        self.graph = graph
        self.pathfinder = pathfinder
        self.occupancy = occupancy

    def assign_paths(
        self,
        drones: list[Drone],
        goal: str,
        start_turn: int,
    ) -> dict[str, list[tuple[str, int]]]:
        """Assign a collision-free path to each drone.

        Args:
            drones: List of drones to schedule (processed in order).
            goal: Name of the destination zone (graph.end_node).
            start_turn: Turn at which all drones are available (usually 0).

        Returns:
            Dict mapping drone.id -> list of (zone_name, arrival_turn).
            Drones for which no path was found are omitted.
        """
        plan: dict[str, list[tuple[str, int]]] = {}

        for drone in drones:
            path = self.pathfinder.find_path(
                drone.current_zone, goal, start_turn, self.occupancy
            )

            if path is None:
                continue

            plan[drone.id] = path

            for i in range(len(path) - 1):
                curr_zone, curr_turn = path[i]
                next_zone, _next_turn = path[i + 1]

                self.occupancy.reserve_zone(curr_zone, curr_turn)

                if curr_zone != next_zone:
                    if self.graph.get_connection(curr_zone, next_zone) is None:
                        raise ValueError("Invalid connection")
                    self.occupancy.reserve_connection(
                        curr_zone, next_zone, curr_turn + 1
                    )

            last_zone, last_turn = path[-1]
            self.occupancy.reserve_zone(last_zone, last_turn)
        return plan
