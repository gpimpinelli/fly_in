class DroneScheduler:
    """Decides, turn by turn, which drones move and along which path,
    resolving conflicts and avoiding deadlocks."""

    def __init__(self, graph: NetworkGraph, pathfinder: Pathfinder, occupancy: OccupancyTracker) -> None:
        self.graph = graph
        self.pathfinder = pathfinder
        self.occupancy = occupancy

    def assign_paths(self, drones: list[Drone], goal: str, start_turn: int) -> dict[str, list[tuple[str, int]]]:
        """Assign a path to each drone, prioritizing to avoid conflicts."""
        map = {}
        for d in drones:
            path = self.pathfinder(d.current_zone, goal, start_turn, self.occupancy)
            if path is None:
                continue
        map_paths[d.id] = path
        
        for i in range(len(path)-1):
            curr_zone = path[i][0]
            curr_turn = path[i][1]

            self.occupancy.reserve_zone(curr_zone, curr_turn)
            next_zone = path[i+1][0]

            if current_zone != next_zone:
                transit_turn = current_turn + 1
                self.occupancy.reserve_connection(current_zone, next_zone, transit_turn)

        self.occupancy.reserve_zone(path[-1][0], path[-1][1])

        return map_paths