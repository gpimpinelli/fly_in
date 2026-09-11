import argparse
from pathlib import Path
import sys


def parse_arg() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fly-in Drone Simulator")
    parser.add_argument("--path_map", type=str, help="Path map file", default="/home/gipimpin/Desktop/fly_in/maps/easy/01_linear_path.txt")
    parser.add_argument("--visual", action="store_true", help="Active visual mode")
    try:
        return parser.parse_args()
    except SystemExit as e:
        sys.exit(f"Invalid argoment terminal: {e}")


def get_lines(file_path: str) -> list[str]:
    path = Path(file_path)
    
    if not path.exists() or not path.is_file():
        sys.exit(f"Errore: Impossibile trovare il file mappa '{path}'")
    valid_lines = []
    with path.open('r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            line_clean = line.strip()
            if not line_clean or line_clean.startswith('#'):
                continue
            valid_lines.append(line_clean)
    return valid_lines


def get_info_zone(lines: list[str]): # -> dict[Zone]:
    info = []
    i = 0
    while(not lines[i].startswith("start_hub:")):
        i += 1
    info = lines[i].split(" ")
    print(info)
    