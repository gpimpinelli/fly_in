import argparse
import re
import sys
from .network_graph import Zone, ZoneType, Connection, NetworkGraph
from pathlib import Path


def parse_arg() -> argparse.Namespace:
    """Parse and return command-line arguments for the simulator."""
    parser = argparse.ArgumentParser(
        description="Fly-in Drone Simulator")
    parser.add_argument(
        "--path_map", type=str, default="maps/easy/01_linear_path.txt")
    parser.add_argument(
        "--visual", action="store_true", help="Active visual mode")
    try:
        return parser.parse_args()
    except SystemExit as e:
        sys.exit(f"Invalid argument terminal: {e}")


class MapParser:
    """Parses a map file into a NetworkGraph."""

    def __init__(self, file_path: str) -> None:
        """Initialize the parser with the path to the map file.

        Args:
            file_path: Relative or absolute path to the map text file.
        """
        self.file_path = file_path

    def build_graph(self) -> NetworkGraph:
        """Read the map file and return a fully constructed NetworkGraph."""
        lines = self._read_lines()
        return self._build_network(lines)

    def _read_lines(self) -> list[tuple[int, str]]:
        """Read the map file and return non-empty, non-comment lines.

        Returns:
            A list of (line_number, content) tuples for valid lines.
        """
        path = Path(self.file_path)
        if not path.exists() or not path.is_file():
            sys.exit(f"Error: Impossible to find map file '{path}'")
        valid_lines: list[tuple[int, str]] = []
        with path.open('r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, start=1):
                line_clean = line.strip()
                if not line_clean or line_clean.startswith('#'):
                    continue
                valid_lines.append((line_number, line_clean))
        return valid_lines

    def _parse_zone(self, key: str, value: str) -> Zone:
        """Parse a zone definition line and return a Zone object.

        Args:
            key: The line key ('start_hub', 'hub', or 'end_hub').
            value: The raw value string following the colon separator.

        Returns:
            A validated Zone instance.

        Raises:
            ValueError: If the zone definition contains syntax errors.
        """
        value = value.strip()
        metadata: dict[str, str] = {}
        match = re.search(r'\[(.*?)\]$', value)

        if match:
            meta_str = match.group(1).strip()
            if not meta_str or "[" in meta_str or "]" in meta_str:
                raise ValueError(f"Syntax bracket error: '{value}'")

            for pair in meta_str.split():
                if "=" not in pair:
                    raise ValueError(f"Attribute invalid: '{pair}'")
                m_key, m_val = pair.split("=", 1)

                if m_key not in ('color', 'zone', 'max_drones'):
                    raise ValueError(f"Invalid key: '{m_key}'")
                if m_key in metadata:
                    raise ValueError(f"Duplicate attribute: '{m_key}'")

                metadata[m_key] = m_val

            value = value[:match.start()].strip()

        base_parts = value.split()
        if len(base_parts) != 3:
            raise ValueError(f"Invalid number of param: '{value}'")

        name, x_str, y_str = base_parts

        if "#" in name or "-" in name:
            raise ValueError(f"Invalid zone name: '{name}'")

        try:
            x_int = int(x_str)
            y_int = int(y_str)
        except ValueError as e:
            raise ValueError("Error: x and y must be integers") from e

        zone_type_str = metadata.pop('zone', 'normal')
        if key in ("start_hub", "end_hub"):
            metadata.pop("max_drones", None)

        try:
            zone_type = ZoneType(zone_type_str)
        except ValueError as e:
            raise ValueError(f"Invalid zone type: '{zone_type_str}'") from e

        color = metadata.get("color", "white")
        max_drones_raw = metadata.get("max_drones")

        if max_drones_raw is not None:
            try:
                max_drones = int(max_drones_raw)
            except ValueError as e:
                raise ValueError(
                    f"max_drones must be an integer, got '{max_drones_raw}'"
                ) from e
        else:
            max_drones = 1

        return Zone(
            name=name,
            x=x_int,
            y=y_int,
            zone_type=zone_type,
            max_drones=max_drones,
            color=color,
        )

    def _parse_connection(self, value: str, graph: 'NetworkGraph') -> None:
        """Parse a connection definition and add it to the graph.

        Args:
            value: The raw value string following the 'connection:' key.
            graph: The NetworkGraph to which the connection is added.

        Raises:
            ValueError:
                If the connection syntax or zone references are invalid.
        """
        value = value.strip()
        metadata: dict[str, str] = {}

        match = re.search(r'\[(.*?)\]$', value)
        if match:
            meta_str = match.group(1).strip()
            if not meta_str or "[" in meta_str or "]" in meta_str:
                raise ValueError(
                    f"Syntax bracket error in connection: '{value}'"
                )

            for pair in meta_str.split():
                if "=" not in pair:
                    raise ValueError(f"Attribute invalid: '{pair}'")
                m_key, m_val = pair.split("=", 1)

                if m_key != 'max_link_capacity':
                    raise ValueError(f"Invalid connection key: '{m_key}'")
                metadata[m_key] = m_val

            value = value[:match.start()].strip()

        parts = value.split("-")
        if len(parts) != 2:
            raise ValueError(f"Invalid connection syntax: '{value}'")

        node1, node2 = parts[0].strip(), parts[1].strip()

        if node1 not in graph.zones or node2 not in graph.zones:
            raise ValueError(
                f"Connection links unknown zones: '{node1}' or '{node2}'"
            )

        for conn in graph.zones[node1].connections:
            if conn.target == node2:
                raise ValueError(
                    f"Duplicate connection found: '{node1}-{node2}'"
                )

        try:
            capacity = int(metadata.get("max_link_capacity", 1))
        except ValueError:
            raise ValueError("max_link_capacity must be an integer")

        if capacity < 1:
            raise ValueError("max_link_capacity must be a positive integer")

        graph.zones[node1].connections.append(
            Connection(target=node2, max_link_capacity=capacity)
        )
        graph.zones[node2].connections.append(
            Connection(target=node1, max_link_capacity=capacity)
        )

    def _build_network(self, lines: list[tuple[int, str]]) -> NetworkGraph:
        """Build and validate a NetworkGraph from parsed lines.

        Args:
            lines: List of (line_number, content) tuples to process.

        Returns:
            A fully populated and validated NetworkGraph.

        Raises:
            ValueError: If mandatory fields are missing or duplicated.
        """
        graph = NetworkGraph()
        nb_drones_found = False

        for line_number, line in lines:
            try:
                if ":" not in line:
                    raise ValueError(f"Line hasn't ':' separator: {line}")

                key, value = line.split(":", 1)
                key = key.strip()

                if key in ("start_hub", "hub", "end_hub"):
                    new_zone = self._parse_zone(key, value)
                    if new_zone.name in graph.zones:
                        raise ValueError(
                            f"Duplicate zone name found: '{new_zone.name}'"
                        )

                    if key == "start_hub":
                        if graph.start_node:
                            raise ValueError("Multiple start_hub defined")
                        graph.start_node = new_zone.name
                    elif key == "end_hub":
                        if graph.end_node:
                            raise ValueError("Multiple end_hub defined")
                        graph.end_node = new_zone.name

                    graph.zones[new_zone.name] = new_zone

                elif key == "connection":
                    self._parse_connection(value, graph)

                elif key == "nb_drones":
                    val_clean = value.strip()
                    if not val_clean.isdigit() or int(val_clean) < 1:
                        raise ValueError(
                            "nb_drones must be a positive integer"
                        )
                    graph.nb_drones = int(val_clean)
                    nb_drones_found = True

                else:
                    raise ValueError(f"Invalid key: '{key}'")

            except ValueError as e:
                raise ValueError(f"Line {line_number}: {e}") from e

        if not nb_drones_found:
            raise ValueError("Map missing 'nb_drones' definition")
        if not graph.start_node:
            raise ValueError("Map missing 'start_hub' definition")
        if not graph.end_node:
            raise ValueError("Map missing 'end_hub' definition")

        return graph
