"""
Simulation run configuration file,
any changes in simulation_config should meet all the validations requirements under /validations/config_validations.py
"""

run_config = {
    "simulation_logs_path": "logs/simulation_logs.txt",
    "passenger_logs_path": "summary/passenger_summary.csv",
}

simulation_config = {
    # elevator number: zones/floors it will cover
    "default_zone_mapping": {
        1: list(range(1, 21)),
        2: list(range(21, 41)),
        3: list(range(41, 61)),
    },
    # (time, passenger_id, source, destination)
    "passenger_requests": [
        (0, "p1", 1, 51),
        (0, "p2", 1, 55),
        (5, "p3", 58, 2),
        (3, "p4", 2, 45),
        (6, "p5", 1, 48),
        (12, "p6", 10, 18),
        (15, "p7", 44, 2),
        (16, "p8", 45, 1),
        (20, "p9", 1, 50),
    ],
    "max_time": 10000,
    # Elevator max capacity
    "max_capacity": 4,
}
