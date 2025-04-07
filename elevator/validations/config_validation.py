from typing import Any, Dict, List, Tuple


def validate_config(sim_config: Dict[str, Any]) -> None:
    """
    Validation for simulation config dict

    Validations include:
      1. The "default_zone_mapping" key must exist and be a dictionary where:
         - Each key is an int
         - Each value is a list of ints
         - The union of all these lists forms a continuous range (i.e. no gaps)
      2. The "passenger_requests" key must exist and be a list
         - Each request must be a tuple of exactly 4 elements:
              (time, passenger_id, source, destination)
         - time: int >= 0 (no decimals)
         - passenger_id: unique string
         - source: int >= 0 and within the floors under default_zone_mapping
         - destination: int and within the floors under default_zone_mapping
      3. The "max_time" key must exist and be an int

    :param sim_config: simulation run configuration
    """

    if "default_zone_mapping" not in sim_config:
        raise ValueError("Missing 'default_zone_mapping' in config")
    dzm = sim_config["default_zone_mapping"]
    if not isinstance(dzm, dict):
        raise ValueError("default_zone_mapping must be a dict")

    all_floors = set()
    for key, floor_list in dzm.items():
        if not isinstance(key, int):
            raise ValueError(f"Key '{key}' in default_zone_mapping is not int")
        if not isinstance(floor_list, list):
            raise ValueError(
                f"Value for key {key} in default_zone_mapping must be a list"
            )
        if not all(isinstance(f, int) for f in floor_list):
            raise ValueError(f"Not all floors in the list for key {key} are ints")
        if not floor_list:
            raise ValueError(f"Floor list for key {key} is empty")
        all_floors.update(floor_list)

    if not all_floors:
        raise ValueError("No floors defined in default_zone_mapping")

    min_floor = min(all_floors)
    max_floor = max(all_floors)
    expected_floors = set(range(min_floor, max_floor + 1))
    if all_floors != expected_floors:
        missing = expected_floors - all_floors
        extra = all_floors - expected_floors
        msg = f"Default zone mapping floors are not continuous. Missing: {missing}, Extra: {extra}"
        raise ValueError(msg)

    if "passenger_requests" not in sim_config:
        raise ValueError("Missing passenger_requests in config")
    pr_list = sim_config["passenger_requests"]
    if not isinstance(pr_list, list):
        raise ValueError("passenger_requests must be a list")

    seen_ids = set()
    for idx, req in enumerate(pr_list):
        # Check that each request is a tuple (or set, but we expect tuple per sample)
        if not isinstance(req, tuple):
            raise ValueError(f"Passenger request at index {idx} is not a tuple")
        if len(req) != 4:
            raise ValueError(
                f"Passenger request at index {idx} must have exactly 4 elements"
            )
        time, pid, source, dest = req

        if not isinstance(time, int) or time < 0:
            raise ValueError(
                f"Passenger request {pid}: time must be a non negative integer"
            )
        if not isinstance(pid, str):
            raise ValueError(
                f"Passenger request at index {idx}: passenger id must be a string"
            )
        if pid in seen_ids:
            raise ValueError(f"Duplicate passenger id found: {pid}")
        seen_ids.add(pid)

        if not isinstance(source, int) or source < 0:
            raise ValueError(f"Passenger {pid}: source must be a non-negative integer")
        if source not in all_floors:
            raise ValueError(
                f"Passenger {pid}: source floor {source} is not defined in default_zone_mapping"
            )

        if not isinstance(dest, int):
            raise ValueError(f"Passenger {pid}: destination must be an integer")
        if dest not in all_floors:
            raise ValueError(
                f"Passenger {pid}: destination floor {dest} is not defined in default_zone_mapping"
            )

    if "max_time" not in sim_config:
        raise ValueError("Missing max_time in configuration")
    max_time = sim_config["max_time"]
    if not isinstance(max_time, int):
        raise ValueError("max_time must be an integer")
