import logging
from typing import List, Optional, Deque

from elevator.elevator_system.elevator import Elevator
from elevator.elevator_system.elevator import Passenger
from utils.utils import create_zones, find_zone_for_number

logger = logging.getLogger("ElevatorLogger")


class LoadBalancer:
    def __init__(self, elevators: List[Elevator]) -> None:
        self.elevators: List[Elevator] = elevators

    def assign_elevator(
        self, passenger: Passenger, waiting_passengers: Deque[Passenger]
    ) -> Optional[Elevator]:
        """
        Assign the best elevator to the passenger
        Consider elevators that are idle or already moving in the correct direction
        """
        best_elevator: Optional[Elevator] = None
        min_cost: float = float("inf")
        total_range: list = []
        for elevator in self.elevators:
            total_range.append(elevator.zone_start)
            total_range.append(elevator.zone_end)

        zones_mapping = create_zones(
            min(total_range), max(total_range), len(self.elevators)
        )

        for elevator in self.elevators:

            assigned_waiters = sum(
                1 for p in waiting_passengers if p.assigned_elevator == elevator.eid
            )
            if (len(elevator.passengers) + assigned_waiters) >= elevator.capacity:
                continue

            if elevator.state == "idle":
                cost = abs(elevator.current_floor - passenger.source)

            elif elevator.state == "moving_to_pickup":

                if elevator.direction == "up" and (
                    find_zone_for_number(max(elevator.destinations), zones_mapping)
                    == find_zone_for_number(passenger.dest, zones_mapping)
                ):
                    if elevator.pickups:
                        if find_zone_for_number(
                            max(elevator.pickups), zones_mapping
                        ) == find_zone_for_number(passenger.source, zones_mapping):
                            cost = abs(elevator.current_floor - passenger.source)
                        else:
                            continue
                    else:
                        cost = abs(elevator.current_floor - passenger.source)
                elif elevator.direction == "down" and (
                    find_zone_for_number(min(elevator.destinations), zones_mapping)
                    == find_zone_for_number(passenger.dest, zones_mapping)
                ):
                    if elevator.pickups:
                        if find_zone_for_number(
                            max(elevator.pickups), zones_mapping
                        ) == find_zone_for_number(passenger.source, zones_mapping):
                            cost = abs(elevator.current_floor - passenger.source)
                        else:
                            continue
                    else:
                        cost = abs(elevator.current_floor - passenger.source)
                else:
                    continue
            else:
                continue
            if cost < min_cost:
                min_cost = cost
                best_elevator = elevator

        if not best_elevator and not passenger.no_assigned_elevator_logging:
            passenger.no_assigned_elevator_logging = True
            logger.debug(f"No available elevator for Passenger {passenger.id}")
        return best_elevator
