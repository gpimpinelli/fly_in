class Drone():
    def __init__(self, drone_id, start_zone) -> None:
        self.drone_id = drone_id
        self.current_zone = start_zone
        self.path: list[str] = []
        self.in_transit_turns = 0
        self.is_delivered = False

    
