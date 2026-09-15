*This project has been created as part of the 42 curriculum by gipimpin.*

# Fly-in — Drone Routing Simulator

## Description

**Fly-in** is a turn-based drone routing simulator written in Python.
The goal is to route a fleet of drones from a shared start hub to a shared end hub across a network of connected zones, minimising the total number of simulation turns while respecting strict movement and capacity constraints.

The network is described by a plain-text map file. Each zone has a type that determines how drones can traverse it, a maximum occupancy limit, and a set of bidirectional connections to neighbouring zones. Each connection has its own capacity, capping the number of drones that may cross it simultaneously.

The simulator solves the routing problem offline before execution: a time-expanded Dijkstra algorithm pre-computes a collision-free path for every drone, reserves its slots, and passes the complete plan to the simulation engine. The engine then replays the plan turn by turn, printing each drone's movement as it happens.

An optional Pygame visualiser allows the user to step through the simulation interactively on a full-screen map.

---

## Zone Types

| Type | Keyword | Movement cost | Pathfinder weight | Notes |
|---|---|---|---|---|
| Normal | `normal` | 1 turn | 1.0 | Default zone type |
| Priority | `priority` | 1 turn | 0.1 | Preferred by the pathfinder |
| Restricted | `restricted` | 2 turns | 2.0 | Drone is in transit for 1 extra turn |
| Blocked | `blocked` | — | — | Impassable; drones cannot enter |

Start and end hubs are always traversable and have unlimited drone capacity.

---

## Map File Format

Map files are plain-text files. Lines starting with `#` and blank lines are ignored.
Every other line must follow one of these formats:

```
nb_drones: <positive integer>

start_hub: <name> <x> <y> [color=<color>]
hub:       <name> <x> <y> [color=<color> zone=<type> max_drones=<n>]
end_hub:   <name> <x> <y> [color=<color>]

connection: <zone_a>-<zone_b> [max_link_capacity=<n>]
```

**Rules:**
- Exactly one `start_hub` and one `end_hub` must be defined.
- Zone names must not contain `#` or `-`.
- `max_drones` defaults to `1`; `max_link_capacity` defaults to `1`.
- Duplicate zone names and duplicate connections are rejected with a clear error message indicating the line number.

**Example — `maps/easy/01_linear_path.txt`:**

```
# Easy Level 1: Simple linear path
nb_drones: 2

start_hub: start      0 0 [color=green]
hub:       waypoint1  1 0 [color=blue]
hub:       waypoint2  2 0 [color=blue]
end_hub:   goal       3 0 [color=red]

connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

---

## Instructions

### Requirements

- Python 3.12+
- [`uv`](https://github.com/astral-sh/uv) (recommended) **or** a standard virtual environment

### Installation

```bash
# With uv (recommended)
make install

# Without uv
python3 -m venv .venv
source .venv/bin/activate
pip install pydantic pygame
```

### Running the simulator

```bash
# Default map (maps/easy/01_linear_path.txt), text output only
uv run python -m src

# Custom map
uv run python -m src --path_map maps/medium/02_circular_loop.txt

# With the interactive Pygame visualiser
uv run python -m src --path_map maps/hard/01_maze_nightmare.txt --visual

# Using the Makefile shortcut (visual mode, default map)
make run
```

### Running linters

```bash
make lint         # flake8 + mypy (standard)
make lint-strict  # flake8 + mypy --strict
```

### Cleaning build artefacts

```bash
make clean
```

---

## Simulation Output Format

Each line of output represents one simulation turn and lists every drone that moved during that turn:

```
D<ID>-<zone>              # drone moved instantly to a normal/priority zone
D<ID>-<zone_a>_<zone_b>  # drone is in transit toward a restricted zone
```

Drones that do not move in a given turn are omitted.
Once a drone reaches the end hub it is considered delivered and is no longer tracked.

**Example — `maps/easy/01_linear_path.txt` (2 drones, 4 turns):**

```
D1-waypoint1
D1-waypoint2 D2-waypoint1
D1-goal D2-waypoint2
D2-goal

Simulation complete in 4 turns.
```

**Example — `maps/easy/02_simple_fork.txt` (4 drones, 4 turns):**

```
D1-junction D2-junction
D1-path_a D2-path_b D3-junction D4-junction
D1-goal D2-goal D3-path_a D4-path_b
D3-goal D4-goal

Simulation complete in 4 turns.
```

---

## Algorithm Design

### Pathfinding — Time-expanded Dijkstra

The routing problem is solved entirely offline before the simulation begins, inside `DroneScheduler.assign_paths()`.

For each drone in order, `Pathfinder.find_path()` runs a **time-expanded Dijkstra** search on a state space of `(zone, turn)` pairs. This allows the algorithm to reason about both spatial position and time simultaneously, which is necessary to avoid collisions in future turns.

**At each node expansion:**

1. **Zone capacity** — the arrival zone must not already be full at the arrival turn (checked via `OccupancyTracker`).
2. **Link capacity** — the connection being traversed must not be saturated at the crossing turn.
3. **Blocked zones** — zones of type `BLOCKED` are never entered.
4. **Movement cost** — restricted zones cost 2 turns to enter (the drone is marked in-transit for the intermediate turn).
5. **Pathfinder weight** — priority zones receive weight `0.1` so the heap prefers them, effectively routing drones through fast corridors when available.

Once a path is found, all its `(zone, turn)` slots are immediately reserved in the `OccupancyTracker`. The next drone must route around them, naturally producing collision-free schedules.

**Wait steps** are handled by expanding the current node to the next turn without changing zone, provided the zone still has capacity.

### Simulation engine

`Simulator.run()` pre-computes the master plan via the scheduler and then replays it turn by turn:

- Instant moves (cost 1) call `Drone.move_instant()`.
- Multi-turn moves into restricted zones (cost 2) call `Drone.start_transit()`, and `Drone.tick_transit()` on the following turn to complete the arrival.
- Drones with no planned move for the current turn call `Drone.wait()`, which records the stationary turn in their path history.
- Drones that arrive at the end hub are immediately marked as delivered and excluded from further processing.

### Module overview

| Module | Responsibility |
|---|---|
| `map_parser.py` | Parses the map file into a `NetworkGraph` |
| `network_graph.py` | Data model for zones, connections, and the graph |
| `occupancy_tracker.py` | Tracks zone and link reservations per turn |
| `path_finder.py` | Time-expanded Dijkstra pathfinding |
| `drone_scheduler.py` | Assigns collision-free paths to all drones |
| `drone.py` | Drone state machine (transit, move, wait, deliver) |
| `simulator.py` | Turn-by-turn simulation engine |
| `visualizer.py` | Optional Pygame interactive visualiser |

---

## Visual Representation

When launched with `--visual`, the simulator opens a full-screen Pygame window after the text simulation completes.

**Map rendering:**
- Each zone is drawn as a coloured circle using the colour defined in the map file.
- The zone type is indicated by the first letter of its type (`N`, `R`, `P`, `B`) overlaid on the circle.
- The maximum drone capacity is displayed below the type letter.
- Connections are drawn as red lines; a small white dot at the midpoint shows the link's capacity value.

**Drone rendering:**
- Each drone is assigned a unique random colour for easy identification.
- While in transit toward a restricted zone, the drone icon appears midway between the two zones.
- Multiple drones occupying the same zone are spread apart with a small offset to avoid visual overlap.

**Controls:**

| Key | Action |
|---|---|
| `→` | Advance one turn |
| `←` | Go back one turn |
| `Esc` / close window | Exit |

The turn counter in the top-left corner shows the current turn and the total number of turns in the simulation.

---

## Performance Benchmarks

| Difficulty | Map | Drones | Target turns | Achieved |
|---|---|---|---|---|
| Easy | Linear path | 2 | 6 | **4** ✅ |
| Easy | Simple fork | 4 | 8 | **4** ✅ |
| Easy | Basic capacity | 4 | 6 | TBD |
| Medium | Dead end trap | 5 | 12 | **8** ✅ |
| Medium | Circular loop | 6 | 15 | TBD |
| Medium | Priority puzzle | 5 | 12 | TBD |
| Hard | Maze nightmare | 8 | 30 | TBD |
| Hard | Capacity hell | 12 | 35 | TBD |
| Hard | Ultimate challenge | 15 | 45 | TBD |

---

## Error Handling

All map parsing errors terminate the program immediately with a message that includes the line number and a human-readable description of the cause. Examples:

```
Line 5: Invalid zone type: 'unknown'
Line 12: Duplicate zone name found: 'waypoint1'
Line 17: Connection links unknown zones: 'zone_x' or 'zone_y'
Error: Impossible to find map file 'maps/missing.txt'
```

---

## Resources

### Pathfinding and graph theory
- Dijkstra, E. W. (1959). *A note on two problems in connexion with graphs.* Numerische Mathematik.
- Hart, P., Nilsson, N., Raphael, B. (1968). *A formal basis for the heuristic determination of minimum cost paths.* IEEE Transactions on Systems Science and Cybernetics.
- [Wikipedia — Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Wikipedia — Multi-agent pathfinding](https://en.wikipedia.org/wiki/Multi-agent_pathfinding)

### Python libraries used
- [Pydantic v2](https://docs.pydantic.dev/) — data validation and modelling for `Drone`, `Zone`, `Connection`, `NetworkGraph`
- [Pygame](https://www.pygame.org/docs/) — graphical visualiser
- [heapq](https://docs.python.org/3/library/heapq.html) — priority queue used by the Dijkstra implementation
- [mypy](https://mypy.readthedocs.io/) — static type checking
- [flake8](https://flake8.pycqa.org/) — code style linting

### AI usage
AI assistance (Antigravity / Claude) was used during this project for the following tasks:

- **Code review** — identifying unused functions across all modules and recommending where and how to integrate them into the existing logic in a semantically meaningful way.
- **Docstring generation** — producing PEP 257-compliant docstrings for all public and private methods across all source files; every generated docstring was reviewed and adjusted manually before being committed.
- **Type error diagnosis** — explaining mypy type errors (e.g., `str | None` assigned to `str`) and discussing the trade-offs between `assert`, `RuntimeError`, and explicit `if` guards in production code.
- **Algorithm explanation** — clarifying the difference between time-expanded and standard graph search, and the implications of reserving occupancy slots sequentially per drone.

All AI-generated content was reviewed, tested, and validated before integration. No AI-generated logic was accepted without being understood and verified against the project's actual behaviour.
