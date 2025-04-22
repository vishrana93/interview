import logging
from collections import deque
from typing import List, Optional, Deque
from elevator.elevator_system.passenger import Passenger
from elevator.elevator_system.elevator import Elevator
from elevator.elevator_system.load_balancer import LoadBalancer

logger = logging.getLogger("ElevatorLogger")


def simulate_elevator_system(
    requests: List[tuple], zone_map: dict, max_time: int
) -> None:
    """
    Function to simulate elevator system

    :param requests: Passenger requests, details are extracted from run_config
    :param zone_map: Zone map for the elevators
    :param max_time: Max time for the simulation
    """
    passengers: List[Passenger] = [Passenger(*req) for req in requests]
    waiting_passengers: Deque[Passenger] = deque()

    elevators: List[Elevator] = [
        Elevator(eid, zone[0], zone[0], zone[-1]) for eid, zone in zone_map.items()
    ]
    load_balancer: LoadBalancer = LoadBalancer(elevators)

    for current_time in range(max_time):
        logger.info(f"Time {current_time}: {', '.join(map(str, elevators))}")
        new_arrivals = [p for p in passengers if p.arrival_time == current_time]
        waiting_passengers.extend(new_arrivals)
        for passenger in list(waiting_passengers):
            if not passenger.is_assigned:
                assigned_elevator = load_balancer.assign_elevator(
                    passenger, waiting_passengers
                )
                if assigned_elevator:
                    passenger.is_assigned = True
                    passenger.assigned_elevator = assigned_elevator.eid
                    assigned_elevator.update_route(passenger.source, passenger.dest)
                    if assigned_elevator.state == "idle":
                        assigned_elevator.state = "moving_to_pickup"
                    logger.info(
                        f"Time {current_time}: Passenger {passenger.id} assigned to Elevator {assigned_elevator.eid}"
                    )

        for elevator in elevators:
            elevator.adjust_zone(waiting_passengers)

        for elevator in elevators:
            if elevator.state == "idle":
                assigned_waiters = [
                    p
                    for p in waiting_passengers
                    if p.is_assigned and p.assigned_elevator == elevator.eid
                ]
                if assigned_waiters:
                    pickup_floor = min(
                        [p.source for p in assigned_waiters],
                        key=lambda s: abs(elevator.current_floor - s),
                    )
                    if pickup_floor not in elevator.pickups:
                        elevator.pickups.append(pickup_floor)

                        if elevator.direction is None:
                            elevator.direction = (
                                "up"
                                if pickup_floor >= elevator.current_floor
                                else "down"
                            )
                        (
                            elevator.pickups.sort()
                            if elevator.direction == "up"
                            else elevator.pickups.sort(reverse=True)
                        )
                    elevator.state = "moving_to_pickup"
                    logger.info(
                        f"Time {current_time}: Elevator {elevator.eid} switching to pickup mode with next pickup floor {pickup_floor}."
                    )

        for elevator in elevators:
            if elevator.state == "loading":
                boarding = [
                    p
                    for p in waiting_passengers
                    if p.source == elevator.current_floor
                    and p.assigned_elevator == elevator.eid
                ]
                available = elevator.capacity - len(elevator.passengers)
                for p in boarding[:available]:
                    waiting_passengers.remove(p)
                    elevator.passengers.append(p)
                    p.board_time = current_time
                    logger.info(
                        f"Time {current_time}: Passenger {p.id} boarded Elevator {elevator.eid}"
                    )

                if elevator.pickups:

                    elevator.state = "moving_to_pickup"
                    if all(elevator.current_floor < p for p in elevator.pickups):
                        elevator.direction = "up"
                    else:
                        elevator.direction = "down"
                elif elevator.destinations or elevator.passengers:

                    elevator.state = "dropping_off"
                    if all(elevator.current_floor < d for d in elevator.destinations):
                        elevator.direction = "up"
                    else:
                        elevator.direction = "down"
                else:
                    elevator.state = "idle"

        for elevator in elevators:
            elevator.move(current_time)

        if all(p.exit_time is not None for p in passengers):
            break
