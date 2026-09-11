from .parsing import parse_arg, get_lines, build_network


def main():
    args = parse_arg()
    txt = get_lines(args.path_map)
    print(repr(build_network(txt)))

if __name__ == "__main__":
    main()
