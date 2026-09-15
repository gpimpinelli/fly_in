from .map_parser import MapParser, parse_arg
from .path_finder import Pathfinder
from .simulator import Simulator


def main() -> None:
    """Entry point: parse arguments, build graph, run simulation."""
    try:
        args = parse_arg()
        parser = MapParser(args.path_map)
        graph = parser.build_graph()
        pathfinder = Pathfinder(graph)
        sim = Simulator(graph, pathfinder)
        turn_log = sim.run()
        print(f"\nSimulation complete in {len(turn_log)} turns.")
        if args.visual:
            from .visualizer import Visualizer
            vis = Visualizer(sim.graph, sim.master_plan)
            vis.run()
    except Exception as e:
        print(f"{e}")


if __name__ == "__main__":
    main()
