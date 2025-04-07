from typing import Dict


def create_zones(t1: int, t2: int, div: int) -> Dict[str, range]:
    """
    Func to create zones
    Each zone to have a range of floors it will cover

    :param t1: min floor value
    :param t2: max floor value
    :param div: Division of zones
    :return: A dict with zones and floors range
    """
    total = t2 - t1 + 1
    zone_size = total // div
    zones: Dict[str, range] = {}
    start = t1
    for i in range(1, div + 1):
        # For the last zone, include any remainder.
        end = start + zone_size
        if i == div:
            end = t2 + 1
        zones[f"zone{i}"] = range(start, end)
        start = end
    return zones


def find_zone_for_number(num: int, zones: Dict[str, range]) -> str:
    """
    Find the zone for a given number

    :param num: Num to locate
    :param zones: A dictionary mapping with zone details
    :return: Dict key of zone name
    """
    for zone, r in zones.items():
        if num in r:
            return zone
    return "Not found"
