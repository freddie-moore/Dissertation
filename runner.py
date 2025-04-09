import sys
import argparse
from traciEnvironment import TraciEnvironment
from trafficLightController import TrafficLightController
from trafficRouteGenerator import TrafficRouteGenerator
from Controllers import FixedTimeController, RLController
from utilities import str2bool
import traci

def parse_args():
    parser = argparse.ArgumentParser(description="Traffic Signal Simulation")

    parser.add_argument('--controller', choices=['fixed', 'rl'], required=True,
                        help="Type of controller: 'fixed' or 'rl'")
    parser.add_argument('--green-time', type=int, default=15,
                        help="Green light duration (default: 15)")
    parser.add_argument('--yellow-time', type=int, default=5,
                        help="Yellow light duration (default: 5)")
    parser.add_argument('--num-cars', type=int, default=400,
                        help="Number of cars to simulate (default: 400)")
    parser.add_argument('--arrival-rate', type=float, default=0.5,
                        help="Mean inter-arrival rate between cars (default: 0.5)")
    parser.add_argument("--gui", type=str2bool, default=True,
                        help="Whether the simulation is run with an accompanying GUI (default: True)")

    return parser.parse_args()

def main():
    args = parse_args()

    # Instantiate environment wrapper and helper classes
    route_generator = TrafficRouteGenerator(args.num_cars, args.arrival_rate)
    light_controller = TrafficLightController(args.yellow_time, args.green_time)
    traci_env = TraciEnvironment(True, {i for i in range(0,36)}, route_generator, light_controller)

    # Select controller
    if args.controller == 'fixed':
        controller = FixedTimeController(traci_env)
    elif args.controller == 'rl':
        controller = RLController(traci_env, r"final_models\cipher\model.pth")

    # Run simulation
    step_count = 0
    terminated = truncated = False
    while not (terminated or truncated):
        state = traci_env.get_state()
        phase = controller.get_phase(state)
        _, _, terminated, truncated, step_count = traci_env.run_phase(phase)

    print(f"Execution finished, total time : {step_count}")
    traci.close()
    sys.stdout.flush()

if __name__ == "__main__":
    main()
