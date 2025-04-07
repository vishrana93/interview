from typing import Optional


class Passenger:
    def __init__(self, arrival_time: int, pid: str, source: int, dest: int) -> None:
        self.arrival_time: int = arrival_time
        self.id: str = pid
        self.source: int = source
        self.dest: int = dest
        self.board_time: Optional[int] = None
        self.exit_time: Optional[int] = None
        self.is_assigned: bool = False
        self.assigned_elevator: Optional[int] = None
        self.no_assigned_elevator_logging: bool = False

    def __repr__(self) -> str:
        return f"Passenger {self.id} ({self.source}->{self.dest})"
