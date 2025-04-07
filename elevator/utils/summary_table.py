import csv
import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger("ElevatorLogger")
logger.setLevel(logging.DEBUG)


def parse_logs_to_csv(log_file: str, output_csv: str, requests: List[tuple]) -> None:
    """
    Generate summary report for each passenger, and overall simulation summary

    :param log_file: Path to the log file
    :param output_csv: Path to the CSV file to write
    :param requests: List of passenger requests (each a tuple: (time, passenger_id, source, dest))
    """
    passenger_data: Dict[str, Dict[str, Any]] = {}
    assignment_pattern = re.compile(
        r"Time (\d+): Passenger (\w+) assigned to Elevator (\d+)"
    )
    boarding_pattern = re.compile(r"Time (\d+): Passenger (\w+) boarded Elevator (\d+)")
    exiting_pattern = re.compile(
        r"\[Time (\d+)\] Passenger (\w+) exited at floor (\d+)"
    )

    for assigned_time, passenger_id, source, destination in requests:
        passenger_data[passenger_id] = {
            "passenger_id": passenger_id,
            "source": source,
            "destination": destination,
            "assigned_elevator": None,
            "assigned_time": assigned_time,
            "boarding_time": None,
            "exited_time": None,
            "wait_time": None,
            "total_time": None,
        }

    with open(log_file, "r") as file:
        for line in file:
            # Match assigned elevator log
            assignment_match = assignment_pattern.search(line)
            if assignment_match:
                time_str, passenger_id, elevator_id = assignment_match.groups()
                if passenger_id in passenger_data:
                    passenger_data[passenger_id]["assigned_elevator"] = elevator_id
                continue

            boarding_match = boarding_pattern.search(line)
            if boarding_match:
                time_str, passenger_id, elevator_id = boarding_match.groups()
                if passenger_id in passenger_data:
                    passenger_data[passenger_id]["boarding_time"] = int(time_str)
                continue

            exiting_match = exiting_pattern.search(line)
            if exiting_match:
                time_str, passenger_id, floor = exiting_match.groups()
                if passenger_id in passenger_data:
                    passenger_data[passenger_id]["exited_time"] = int(time_str)
                continue

    wait_times: List[int] = []
    total_times: List[int] = []
    for pdata in passenger_data.values():
        if pdata["boarding_time"] is not None and pdata["assigned_time"] is not None:
            pdata["wait_time"] = pdata["boarding_time"] - pdata["assigned_time"]
            wait_times.append(pdata["wait_time"])
        if pdata["exited_time"] is not None and pdata["assigned_time"] is not None:
            pdata["total_time"] = pdata["exited_time"] - pdata["assigned_time"]
            total_times.append(pdata["total_time"])

    with open(output_csv, "w", newline="") as csvfile:
        fieldnames = [
            "passenger_id",
            "source",
            "destination",
            "assigned_elevator",
            "assigned_time",
            "boarding_time",
            "exited_time",
            "wait_time",
            "total_time",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for pdata in passenger_data.values():
            writer.writerow(pdata)

        writer.writerow({})

        if wait_times:
            wait_min = min(wait_times)
            wait_max = max(wait_times)
            wait_mean = sum(wait_times) / len(wait_times)
        else:
            wait_min = wait_max = wait_mean = 0

        if total_times:
            total_min = min(total_times)
            total_max = max(total_times)
            total_mean = sum(total_times) / len(total_times)
        else:
            total_min = total_max = total_mean = 0

        writer.writerow(
            {
                "passenger_id": f"Wait Times: Min={wait_min}, Max={wait_max}, Mean={round(wait_mean)}"
            }
        )
        writer.writerow(
            {
                "passenger_id": f"Total Times: Min={total_min}, Max={total_max}, Mean={round(total_mean)}"
            }
        )

    logger.info(f"Summary written to {output_csv}")
