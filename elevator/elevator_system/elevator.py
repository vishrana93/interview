import logging
from typing import List, Optional, Deque

from elevator.elevator_system.passenger import Passenger
from elevator.run_config import simulation_config

logger = logging.getLogger("ElevatorLogger")


class Elevator:
    def __init__(
        self, eid: int, current_floor: int, zone_start: int, zone_end: int
    ) -> None:
        self.eid: int = eid
        self.current_floor: int = current_floor
        self.original_floor: int = current_floor
        self.zone_start: int = zone_start
        self.zone_end: int = zone_end
        self.capacity: int = simulation_config["max_capacity"]
        self.pickups: List[int] = []
        self.destinations: List[int] = []
        self.direction: Optional[str] = None
        self.state: str = "idle"
        self.passengers: List[Passenger] = []

    def can_accept(self) -> bool:
        """
        Checks the elevator capacity
        """
        return len(self.passengers) < self.capacity

    def update_route(self, new_source: int, new_dest: int) -> None:
        """
        Update the elevators route by adding a pickup floor and a destination
        If idle, set direction based on new_source relative to current_floor
        """
        if self.state == "idle":
            self.direction = "up" if new_source >= self.current_floor else "down"
        # Only add pickup if it's in the direction of travel.
        if self.direction == "up" and (
            new_source >= self.current_floor or new_source < self.current_floor
        ):
            if new_source not in self.pickups:
                self.pickups.append(new_source)
                self.pickups.sort()
        elif self.direction == "down" and (
            new_source <= self.current_floor or new_source > self.current_floor
        ):
            if new_source not in self.pickups:
                self.pickups.append(new_source)
                self.pickups.sort(reverse=True)
        else:
            pass

        if new_dest not in self.destinations:
            self.destinations.append(new_dest)
            (
                self.destinations.sort()
                if self.direction == "up"
                else self.destinations.sort(reverse=True)
            )

        if self.pickups:
            self.state = "moving_to_pickup"

    def adjust_zone(self, waiting_passengers: Deque[Passenger]) -> None:
        """
        Adaptive Zones: Expand zone boundaries based on waiting passengers assigned to this elevator
        """
        for p in waiting_passengers:
            if p.assigned_elevator == self.eid:
                if p.source < self.zone_start:
                    logger.info(
                        f"Elevator {self.eid}: Expanding zone start from {self.zone_start} to {p.source}"
                    )
                    self.zone_start = p.source
                if p.source > self.zone_end:
                    logger.info(
                        f"Elevator {self.eid}: Expanding zone end from {self.zone_end} to {p.source}"
                    )
                    self.zone_end = p.source

    def move(self, current_time: int) -> None:
        """
        Move one step toward the next target
        "moving_to_pickup", move toward the next pickup (based on sorted pickups)
        "dropping_off", move toward the next destination (sorted)
        """
        if self.state == "idle":
            # If idle, return to original floor.
            if self.current_floor < self.original_floor:
                self.current_floor += 1
            elif self.current_floor > self.original_floor:
                self.current_floor -= 1
            return

        if self.state == "moving_to_pickup":
            if self.direction == "up":
                target = max(self.pickups)
            else:
                target = (
                    min(self.pickups)
                    if not min(self.destinations) < min(self.pickups)
                    else max(self.pickups)
                )
            if self.current_floor < target:
                self.current_floor += 1
            elif self.current_floor > target:
                self.current_floor -= 1
            else:
                self.state = "loading"
                logger.info(f"Elevator {self.eid}: Arrived at Pickup floor {target}")
                self.pickups.remove(target)
        elif self.state == "loading":
            # Boarding is handled in the simulation loop
            # After boarding, if there are remaining pickups, remain in moving_to_pickup
            # otherwise, switch to dropping_off if destinations exist.
            if self.destinations:
                self.state = "dropping_off"
            elif self.pickups:
                self.state = "moving_to_pickup"
            else:
                self.state = "idle"
        elif self.state == "dropping_off":
            if self.destinations:
                if self.direction == "up":
                    target = min(self.destinations)
                else:
                    target = max(self.destinations)
                if self.current_floor < target:
                    self.current_floor += 1
                elif self.current_floor > target:
                    self.current_floor -= 1
                else:
                    self.destinations.remove(target)
                    dropped = [
                        p for p in self.passengers if p.dest == self.current_floor
                    ]
                    for p in dropped:
                        p.exit_time = current_time
                        logger.info(
                            f"[Time {current_time}] Passenger {p.id} exited at floor {self.current_floor}"
                        )
                    self.passengers = [
                        p for p in self.passengers if p.dest != self.current_floor
                    ]
                    logger.info(
                        f"Elevator {self.eid}: Dropped off passengers at Floor {self.current_floor}"
                    )
            else:
                if self.pickups:
                    self.state = "moving_to_pickup"
                else:
                    self.state = "idle"
                    self.direction = None

    def __repr__(self) -> str:
        route_info = (
            f"Pickups: {self.pickups}, Dest: {self.destinations}"
            if self.pickups or self.destinations
            else "Route: None"
        )
        return f"<Elevator {self.eid} Floor={self.current_floor} {route_info} Load={len(self.passengers)}/{self.capacity}>"
