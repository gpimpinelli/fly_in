import pygame
import random
from .network_graph import NetworkGraph

COLORS = {
    "WHITE": (220, 220, 220),
    "RED": (255, 80, 80),
    "BLUE": (80, 160, 255),
    "GREEN": (80, 220, 120),
    "YELLOW": (255, 220, 50),
    "BLACK": (180, 180, 180)
}


class Visualizer:
    def __init__(
        self,
        graph: NetworkGraph,
        master_plan: dict[str, list[tuple[str, int]]]
    ) -> None:
        """Initialize the Visualizer with the network graph
        and the computed paths."""
        self.graph = graph
        self.master_plan = master_plan
        self.drone_colors = self._assign_drone_colors()

        # Calcola il turno massimo analizzando
        # tutti i turni di arrivo nel master_plan
        self.max_turn = 0
        for path in self.master_plan.values():
            if path:
                self.max_turn = max(self.max_turn, path[-1][1])

    def _assign_drone_colors(self) -> dict[str, tuple[int, int, int]]:
        """Assegna un colore RGB univoco a ciascun drone identificato."""
        random.seed(1)
        colors = {}
        for drone_id in self.master_plan.keys():
            colors[drone_id] = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255)
            )
        return colors

    def _get_drone_state(
        self,
        drone_id: str,
        target_turn: int
    ) -> tuple[str, str, bool]:
        """
        Interpola la posizione del drone nel turno 'target_turn'
        basandosi sul master_plan.
        Ritorna: (zona_precedente, zona_successiva, is_in_flight)
        """
        path = self.master_plan.get(drone_id, [])
        if not path:
            return self.graph.start_node, self.graph.start_node, False

        # Se il turno cercato è oltre la fine del viaggio,
        # il drone è arrivato (fermo)
        if target_turn >= path[-1][1]:
            last_zone = path[-1][0]
            return last_zone, last_zone, False

        # Cerca in quale segmento si trova il drone al turno 'target_turn'
        for i in range(len(path) - 1):
            curr_zone, curr_arrival_turn = path[i]
            next_zone, next_arrival_turn = path[i + 1]

            if curr_arrival_turn <= target_turn < next_arrival_turn:
                # Se è esattamente il turno in cui arriva nella prima zona,
                # non è in volo
                if target_turn == curr_arrival_turn:
                    return curr_zone, curr_zone, False
                # Altrimenti, sta viaggiando verso la next_zone
                # (transito per zone RESTRICTED o BLOCKED superate)
                return curr_zone, next_zone, True

        return self.graph.start_node, self.graph.start_node, False

    def run(self) -> None:
        """Render the map and drone simulation using Pygame."""
        pygame.init()
        pygame.display.set_caption("Fly-in Visualization")

        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        width, height = screen.get_width(), screen.get_height()
        scale = 80

        # Ottieni le zone dall'oggetto NetworkGraph
        zone_dict = self.graph.zones

        min_x = min(zone.x for zone in zone_dict.values())
        min_y = min(zone.y for zone in zone_dict.values())
        max_x = max(zone.x for zone in zone_dict.values())
        max_y = max(zone.y for zone in zone_dict.values())

        map_center_x = (min_x + max_x) / 2
        map_center_y = (min_y + max_y) / 2
        offset_x = (width / 2) - (map_center_x * scale)
        offset_y = (height / 2) - (map_center_y * scale)

        pygame.font.init()
        font_large = pygame.font.SysFont(None, 28)
        font_small = pygame.font.SysFont(None, 20)

        # Fallback sicuro nel caso in cui non trovi l'immagine del drone
        try:
            drone_image = pygame.image.load("drone.png")
            drone_icon = pygame.transform.scale(drone_image, (32, 32))
        except FileNotFoundError:
            drone_icon = pygame.Surface((35, 35), pygame.SRCALPHA)
            pygame.draw.circle(drone_icon, (255, 255, 255), (17, 17), 17)

        current_turn = 0
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        current_turn = min(self.max_turn, current_turn + 1)
                    elif event.key == pygame.K_LEFT:
                        current_turn = max(0, current_turn - 1)
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            screen.fill((30, 30, 30))

            # 1. Disegna le Connessioni (utilizzando l'attributo
            # .target dei Connection)
            for zone in zone_dict.values():
                start_x = (zone.x * scale) + offset_x
                start_y = (zone.y * scale) + offset_y

                for connection in zone.connections:
                    target_zone = zone_dict[connection.target]
                    end_x = (target_zone.x * scale) + offset_x
                    end_y = (target_zone.y * scale) + offset_y

                    pygame.draw.line(
                        screen,
                        (255, 0, 0),
                        (start_x, start_y),
                        (end_x, end_y),
                        connection.max_link_capacity
                    )

                    link_center_x = (start_x + end_x) / 2
                    link_center_y = (start_y + end_y) / 2
                    pygame.draw.circle(
                        screen,
                        (255, 255, 255),
                        (link_center_x, link_center_y),
                        scale / 10
                    )

                    capacity_label = font_small.render(
                        str(connection.max_link_capacity), True, (0, 0, 0))
                    screen.blit(
                        capacity_label,
                        (link_center_x - 4, link_center_y - 7))

            # 2. Disegna le Zone (nodi)
            for zone in zone_dict.values():
                center_x = (zone.x * scale) + offset_x
                center_y = (zone.y * scale) + offset_y

                # Applica il colore testuale estratto da zone.color
                circle_color = COLORS.get(zone.color.upper(), COLORS["WHITE"])
                pygame.draw.circle(
                    screen, circle_color, (center_x, center_y), scale / 3)

                zone_type_letter = zone.zone_type.name[0]
                zone_type_label = font_large.render(
                    zone_type_letter,
                    True,
                    (0, 0, 0),
                    (255, 255, 255)
                )
                drone_label = font_small.render(
                    str(zone.max_drones),
                    True,
                    (0, 0, 0),
                    (255, 255, 255)
                )

                screen.blit(zone_type_label, (center_x - 30, center_y - 15))
                screen.blit(drone_label, (center_x - 27, center_y + 3))

            # 3. Effetto Sciame ed Esecuzione Masterplan
            drone_idx = 0
            for drone_id in self.master_plan.keys():
                # Leggi la posizione interpolata del drone nel turno corrente
                prev_loc, next_loc, in_flight = self._get_drone_state(
                    drone_id, current_turn
                )

                offset_x_drone = (drone_idx * 7) % 25 - 12
                offset_y_drone = (drone_idx * 5) % 25 - 12
                drone_idx += 1

                prev_pos = zone_dict[prev_loc]
                if in_flight:
                    next_pos = zone_dict[next_loc]
                    base_x = ((prev_pos.x + next_pos.x) / 2 * scale) + offset_x
                    base_y = ((prev_pos.y + next_pos.y) / 2 * scale) + offset_y
                else:
                    base_x = (prev_pos.x * scale) + offset_x
                    base_y = (prev_pos.y * scale) + offset_y

                x = base_x + offset_x_drone
                y = base_y + offset_y_drone

                colored_icon = drone_icon.copy()
                colored_icon.fill(
                    self.drone_colors[drone_id],
                    special_flags=pygame.BLEND_MULT
                )
                screen.blit(colored_icon, (x - 15, y - 25))

            # 4. Info Testuali UI
            ui_label = font_large.render(
                f"Turn: {current_turn} / {self.max_turn}",
                True,
                (255, 255, 255))
            screen.blit(ui_label, (20, 20))

            pygame.display.flip()

        pygame.quit()
