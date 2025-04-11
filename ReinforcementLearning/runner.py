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
    parser.add_argument("--ped-stop", type=int, default=100,
                        help="How many time steps to simulate pedestrian arrivals for")
    parser.add_argument("--interval", type=int, default=50,
                        help="The time interval between each pedestrian arrival")

    return parser.parse_args()

def main():
    args = parse_args()

    # Instantiate environment wrapper and helper classes
    route_generator = TrafficRouteGenerator(args.num_cars, args.arrival_rate, args.ped_stop, args.interval)
    light_controller = TrafficLightController(args.yellow_time, args.green_time, False)
    traci_env = TraciEnvironment(args.gui, {i for i in range(0,36)}, route_generator, light_controller, False)

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

    light_controller.save_actual_arrivals()
    print(f"Execution finished, total time : {step_count}")

    traci.close()
    sys.stdout.flush()


if __name__ == "__main__":
    main()
