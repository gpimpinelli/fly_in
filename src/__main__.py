from .utils import parse_arg, get_lines, get_info_zone


def main():
    args = parse_arg()
    txt = get_lines(args.path_map)
    print(txt)
    get_info_zone(txt)

if __name__ == "__main__":
    main()
