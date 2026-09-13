class Simulator:
    """Runs the turn-based simulation, moving all drones from
    start to end while respecting capacity and timing rules."""

    def __init__(self, graph: NetworkGraph, pathfinder: Pathfinder) -> None:
        self.graph = graph
        self.pathfinder = pathfinder
        self.occupancy = OccupancyTracker()
        self.drones: list[Drone] = self._spawn_drones()
        self.turn_log: list[str] = []
        self.master_plan: dict[str, list[tuple[str, int]]] = {}

    def _spawn_drones(self) -> list[Drone]:
        ...

    def run(self) -> list[str]:
        """Run the simulation until all drones are delivered."""
        scheduler = DroneScheduler(self.graph, self.pathfinder, self.occupancy)
        self.master_plan = scheduler.assign_paths(self.drones, "end", 0)
        turn = 0
        while not self.all_delivered():
            self._simulate_turn(turn)
            turn += 1
        return self.turn_log

    def _simulate_turn(self, turn: int) -> None:
        moves_this_turn = {}

        for d in self.drones:
            if d.is_delivered:
                continue
            
            if d.is_in_transit():
                d.tick_transit()
                print(f"{d.get_action_target()}")

            path = self.master_plan.get(d.drone_id)

            if not path or turn + 1 >= len(path):
                continue

            next_zone = path[turn + 1][0]



    def all_delivered(self) -> bool:
        return all(d.is_delivered for d in self.drones)

    def format_turn_output(self, turn: int, moves: dict[str, str]) -> str:
        ...