# Elevator Simulation

## Overview:

This project simulates an elevator system that dynamically assigns elevators to pick up passengers and drop them off at
their destinations. The simulation is implemented in Python using object-oriented programming and leverages the
following key features:

1. Dynamic assignment: A load balancer assigns waiting passengers to elevators based on proximity and current route
   direction.
2. Adaptive zones: Each elevator has a configurable zone, which can be dynamically adjusted based on waiting passengers’
   pickup floors.
3. Route management: Elevators maintain separate lists for pickup floors and destination floors, ensuring that pickups
   and drop-offs are handled in a logical order that minimizes backtracking.
4. Logging: Detailed logging is implemented to track elevator states, assignments, boardings, and drop-offs.

## How to run the Simulation

### Pre-requisites

- Python 3.10 or later
- Required Python packages:
    - pandas

### File Structure

- **`main.py`**: The entry point for running the simulation
- **`elevator/elevator_system/simulate_elevator.py`**: Contains the simulation logic
- **`elevator/elevator_system/passenger.py`**: Contains the `Passenger` class
- **`elevator/elevator_system/elevator.py`**: Contains the `Elevator` class
- **`elevator/elevator_system/load_balancer.py`**: Contains Load Balancer logic
- **`elevator/utils/summary_table.py`**: Contains code for generating summary reports from log files
- **`elevator/utils/get_logger.py`**: Contains centralized logging configuration.
- **`elevator/utils/utils.py`**: General helper functions
- **`elevator/validations/config_validation.py`**: Contains config validation functions
- **`elevator/logs/simulation_logs.txt`**: Contains the simulation logs
- **`elevator/summary/passenger_summary.csv`**: Contains the passenger summary report
- **`elevator/run_config.py`**: Contains runtime configuration such as file paths and simulation config
- **`README.md`**: This file.

### Running the Simulation

1. Clone the Repository using git clone <repository_url>
2. Make sure Python interpreter is configured in your IDE (e.g. PyCharm)
3. Run the Simulation from the command line, python main.py OR Run -> Run if you're using PyCharm
4. Check the Logs and Summary
    - **`elevator/logs/simulation_logs.txt`** to see detailed logs of the simulation (state transitions, passenger
      assignments, pickups, and drop-offs)
    - **`elevator/summary/passenger_summary.csv`** for the final aggregated stats

## Assumptions

1. Each elevator has a fixed capacity
2. Each elevator is assigned pre-defined zone. These zones can be dynamically expanded based on waiting passenger data
3. Simulation uses a greedy approach for route management. It maintains separate lists for pickups and destinations and
   processes pickups in an order determined by the elevator's direction.
4. Simulation operates in time steps, with each tick representing one unit on time
5. Simulation is driven by a hard-coded configuration for passenger requests and zone mapping (as we don't have any past
   data)

## Simplifications and Trade-offs

1. The load balancer assigns the closest available elevator using a greedy strategy, This is simple and fast but not
   produce best results in high-load scenarios
2. The elevator route is managed via separate lists for pickups and drop-offs. This approach simplifies logic but may
   lead to poor outcome if requests are highly dynamic
3. Zones are initially hard-coded but can be expanded based on waiting passenger pickup floors. The trade-off provides
   some flexibility without the complexity of a fully dynamic zoning algorith
   
   3.1 System allows some flexibility in assigning elevators across zones—for example, an elevator primarily assigned to
   zone2 might serve a passenger from zone1 when necessary. This “greedy” approach is a deliberate trade-off. In
   real-world scenarios, the number of requests from a zone might spike, so an elevator servicing multiple zones might
   not be preferable to strictly enforcing zones when capacity is tight. Thus, if there’s a high probability of more
   requests coming from zone1 than from zone2, then having the flexibility to service both can be beneficial but not
   ideal for some scenarios as passenger on zone2 might have wait longer as the assigned elevator to zone will be busy

   3.2 The current algorithm tends to penalize passengers whose journeys begin and end in the same zone. For instance,
   if a passenger is picked up in zone1 and also drops off in zone1, they don’t receive priority over passengers who
   need to travel between different zones. This trade-off was made because, in many practical situations, most people
   are traveling between zones where fewer stops mean faster travel times. If I prioritized same-zone trips equally,
   the elevator might stop too frequently, which could slow down overall transit times for a majority of users moving
   between zones

   3.3 The elevator’s state behavior is somewhat rigid. Once an elevator enters “pickup mode,” it accepts requests for
   passengers traveling within the same zone. However, once it starts boarding (switching to “dropping_off”), it won’t
   pick up additional passengers even if there is spare capacity. I made this choice deliberately to avoid the scenario
   where an elevator continuously picks up and drops off passengers, which could extend its route excessively and delay
   overall service. In a real-world implementation, you might want more dynamic behavior, but this approach strikes a
   balance for this simulation
5. Reporting relies on parsing logs, which is less robust than using a dedicated database or logging system. In
   practice, if developers change logging formats or methods, reporting might break. I chose this approach because I
   don’t have a database for this project, and writing directly to a CSV file during operation could cause performance
   issues or system failures if, for example, file I/O suddenly fails. In real world scenario, it’s preferable to have
   broken reporting (or logs) rather than interrupt core elevator operations
6. The simulation currently focuses solely on the core algorithm and does not handle external factors 
   (such as system-level errors). This simplification was made to concentrate on demonstrating the elevator scheduling
   logic. In a production environment, additional error handling and resilience mechanisms would be necessary

## Further Improvements

1. Machine learning approach to optimize elevator routing and assignment
2. Real time monitoring with alerting for long wait times or capacity issues
3. Use of async to generate passenger summary in real time

## Observation on wait times and total time

1. The minimum wait time is 1 minute, and the maximum is 92 minutes. This significant spread indicates that while some
   passengers are picked up almost immediately, there are outliers experiencing much longer wait times, which was
   somewhat expected because of 3.2 above under ## Simplifications and Trade-offs
2. The total time ranges from 55 minutes to 100 minutes, the variation here suggests that some passengers’ trips are
   significantly longer than others which was somewhat expected as the simulation data inputs were deliberately provided
   in a way which was not favorable for current algorith and because of the trade-offs in section 3.0 above, wait times
   were high that's why the total time was impacted (direct correlation)
3. 92 minutes max wait time suggest, the current greedy approach might not be suitable during peak times, I
   intentionally prioritized cross-zone efficiency under the assumption that most passengers travel between zones. This
   suggest that further tuning might be needed for certain requests under same zone travel. 
