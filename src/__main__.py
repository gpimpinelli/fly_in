from .map_parser import MapParser, parse_arg


def main():
    args = parse_arg()
    parser = MapParser(args.path_map)
    graph = parser.build_graph()
    print(graph)
    

if __name__ == "__main__":
    main()
