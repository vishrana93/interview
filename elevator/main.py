from elevator.elevator_system.simulate_elevator import simulate_elevator_system
from utils.get_logger import get_logger
from utils.summary_table import parse_logs_to_csv
from run_config import run_config, simulation_config
from validations.config_validation import validate_config

logger = get_logger(log_path=run_config["simulation_logs_path"])


def main():

    try:
        validate_config(simulation_config)
        simulate_elevator_system(
            simulation_config["passenger_requests"],
            simulation_config["default_zone_mapping"],
            simulation_config["max_time"],
        )
        parse_logs_to_csv(
            run_config["simulation_logs_path"],
            run_config["passenger_logs_path"],
            simulation_config["passenger_requests"],
        )
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    main()
