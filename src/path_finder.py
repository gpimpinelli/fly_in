import heapq
from .network_graph import NetworkGraph
from .occupancy_tracker import OccupancyTracker

class Pathfinder:

    def __init__(self, graph: NetworkGraph) -> None:
        self.graph = graph

    def find_path(
        self, start: str, goal: str, start_turn: int, occupancy: OccupancyTracker
    ) -> list[tuple[str, int]] | None:
        visited = set()
        queue = [(0.0, start_turn, start, [(start, start_turn)])]

        while queue:
            cost, turn, node, path = heapq.heappop(queue)

            if node == goal:
                return path

            if (node, turn) in visited:
                continue

            visited.add((node, turn))

            next_turn = turn + 1
            future_occupancy = occupancy.zone_count_at(node, next_turn)
            new_path = path + [(node, next_turn)]

            if self.graph.has_capacity(node, future_occupancy):
                heapq.heappush(queue, (cost + 1.0, next_turn, node, new_path))

            for conn in self.graph.neighbors(node):
                target_name = conn.target
                target_zone = self.graph.get_zone(target_name)

                if target_zone.is_blocked():
                    continue

                arrival_turn = turn + target_zone.movement_cost()
                new_cost = cost + target_zone.decision_weight()
                new_path = path + [(target_name, arrival_turn)]

                transit_turn = turn + 1
                drones_in_transit = occupancy.connection_count_at(node, target_name, transit_turn)
                if drones_in_transit >= conn.max_link_capacity:
                    continue

                target_future_occupancy = occupancy.zone_count_at(target_name, arrival_turn)
                if not self.graph.has_capacity(target_name, target_future_occupancy):
                    continue

                new_path = path + [(target_name, arrival_turn)]
                heapq.heappush(queue, (new_cost, arrival_turn, target_name, new_path))

        return None