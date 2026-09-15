from .network_graph import NetworkGraph
from .occupancy_tracker import OccupancyTracker
from .path_finder import Pathfinder
from .drone import Drone
from .drone_scheduler import DroneScheduler


class Simulator:
    """Runs the turn-based simulation, moving all drones from
    start to end while respecting capacity and timing rules."""

    def __init__(self, graph: NetworkGraph, pathfinder: Pathfinder) -> None:
        """Initialize the Simulator, spawn drones, and prepare state.

        Args:
            graph: The parsed NetworkGraph describing the map.
            pathfinder: A Pathfinder instance ready to compute routes.
        """
        self.graph = graph
        self.pathfinder = pathfinder
        self.occupancy = OccupancyTracker()
        self.drones: list[Drone] = self._spawn_drones()
        self.turn_log: list[str] = []
        self.master_plan: dict[str, list[tuple[str, int]]] = {}

    def _spawn_drones(self) -> list[Drone]:
        """Create nb_drones drones, all starting in the start zone."""
        start = self.graph.start_node
        return [
            Drone(id=f"D{i + 1}", current_zone=start, path=[start])
            for i in range(self.graph.nb_drones)
        ]

    def run(self) -> list[str]:
        """Run the simulation until all drones are delivered."""
        scheduler = DroneScheduler(self.graph, self.pathfinder, self.occupancy)
        self.master_plan = scheduler.assign_paths(
            self.drones, self.graph.end_node, 0
        )
        turn = 0
        while not self.all_delivered():
            self._simulate_turn(turn)
            turn += 1
        return self.turn_log

    def _simulate_turn(self, turn: int) -> None:
        """Execute one simulation turn and record the output line."""
        moves_this_turn: dict[str, str] = {}

        for drone in self.drones:
            if drone.is_delivered:
                continue

            if drone.is_in_transit():
                drone.tick_transit()
                if drone.current_zone == self.graph.end_node:
                    drone.deliver(drone.current_zone)
                moves_this_turn[drone.id] = drone.current_zone
                continue

            path = self.master_plan.get(drone.id)
            if not path:
                drone.wait()
                continue

            current_step = None
            next_step = None
            for i, (zone, arrival) in enumerate(path):
                if arrival == turn and i + 1 < len(path):
                    current_step = (zone, arrival)
                    next_step = path[i + 1]
                    break

            if current_step is None or next_step is None:
                continue

            curr_zone, curr_turn = current_step
            next_zone, next_arr = next_step

            if curr_zone == next_zone:
                drone.wait()
                continue

            move_cost = next_arr - curr_turn

            if move_cost == 1:
                drone.move_instant(next_zone)
                if next_zone == self.graph.end_node:
                    drone.deliver(next_zone)
                moves_this_turn[drone.id] = next_zone
            else:
                drone.start_transit(next_zone, move_cost - 1)
                target = drone.get_action_target()
                if target is None:
                    raise RuntimeError(
                        f"Drone {drone.id} started "
                        "transit but has no action target"
                    )
                moves_this_turn[drone.id] = target
        line = self.format_turn_output(turn, moves_this_turn)
        if line:
            self.turn_log.append(line)
            print(line)

    def all_delivered(self) -> bool:
        """Return True when every drone has reached the end zone."""
        return all(d.is_delivered for d in self.drones)

    def format_turn_output(self, turn: int, moves: dict[str, str]) -> str:
        """Format one turn line following the output specification.

        Args:
            turn: The current simulation turn number (unused in output).
            moves: Mapping of drone ID to its target zone string this turn.

        Returns:
            A space-separated string of 'DroneID-zone' entries,
            or an empty string if no moves occurred.
        """
        if not moves:
            return ""
        return " ".join(
            f"{drone_id}-{target}" for drone_id, target in moves.items())
