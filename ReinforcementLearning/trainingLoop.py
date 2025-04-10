import math
import random
import argparse
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim
from itertools import count

from traciEnvironment import TraciEnvironment
from model import DQN
from memory import ReplayMemory, Transition
from utilities import plot_durations, str2bool
from trafficRouteGenerator import TrafficRouteGenerator
from trafficLightController import TrafficLightController

def parse_args():
    parser = argparse.ArgumentParser(description="Train DQN for SUMO Traffic Signal Control")

    # Env params
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

    # DQN Hyperparams
    parser.add_argument("--batch-size", type=int, default=128,
                        help="the number of transitions sampled from the replay buffer (default 128)")
    parser.add_argument("--gamma", type=float, default=0.99,
                        help="the discount factor (default: 0.99)")
    parser.add_argument("--eps-start", type=float, default=0.9,
                        help="the starting value of epsilon (default: 0.9)")
    parser.add_argument("--eps-end", type=float, default=0.05,
                        help="the final value of epsilon (default: 0.05)")
    parser.add_argument("--eps-decay", type=int, default=1000,
                        help="controls the rate of exponential decay of epsilon, higher means a slower decay (default: 1000)")
    parser.add_argument("--tau", type=float, default=0.005,
                        help="the update rate of the target network (default: 0.005)")
    parser.add_argument("--lr", type=float, default=1e-4,
                        help="the learning rate of the AdamW optimizer (default: 1e-4)")
    parser.add_argument("--episodes", type=int, default=5000,
                        help="the number of episodes to train the agent for")

    return parser.parse_args()

def main():
    args = parse_args()

    # Environment setup
    route_generator = TrafficRouteGenerator(args.num_cars, args.arrival_rate)
    light_controller = TrafficLightController(args.yellow_time, args.green_time)
    env = TraciEnvironment(args.gui, {i for i in range(0,36)}, route_generator, light_controller)

    # Device
    device = torch.device("cuda" if torch.cuda.is_available() else
                          "mps" if torch.backends.mps.is_available() else "cpu")

    # Initial state
    state, info = env.reset_simulation()
    n_actions = env.get_n_actions()
    n_observations = len(state)

    # Networks
    policy_net = DQN(n_observations, n_actions).to(device)
    target_net = DQN(n_observations, n_actions).to(device)
    target_net.load_state_dict(policy_net.state_dict())
    optimizer = optim.AdamW(policy_net.parameters(), lr=args.lr, amsgrad=True)
    memory = ReplayMemory(128)

    steps_done = 0
    episode_durations = []
    veh_waits_arr = []
    emv_waits_arr = []
    ped_waits_arr = []
   
    record = float('+inf')

    def select_action(state):
        nonlocal steps_done
        sample = random.random()
        eps_threshold = args.eps_end + (args.eps_start - args.eps_end) * math.exp(-1. * steps_done / args.eps_decay)
        steps_done += 1
        if sample > eps_threshold:
            with torch.no_grad():
                return policy_net(state).max(1).indices.view(1, 1)
        else:
            return torch.tensor([[env.sample_action_space()]], device=device, dtype=torch.long)

    def optimize_model():
        if len(memory) < args.batch_size:
            return
        transitions = memory.sample(args.batch_size)
        batch = Transition(*zip(*transitions))

        non_final_mask = torch.tensor(tuple(map(lambda s: s is not None, batch.next_state)),
                                      device=device, dtype=torch.bool)
        non_final_next_states = torch.cat([s for s in batch.next_state if s is not None])
        state_batch = torch.cat(batch.state)
        action_batch = torch.cat(batch.action)
        reward_batch = torch.cat(batch.reward)

        state_action_values = policy_net(state_batch).gather(1, action_batch)
        next_state_values = torch.zeros(args.batch_size, device=device)
        with torch.no_grad():
            next_state_values[non_final_mask] = target_net(non_final_next_states).max(1).values
        expected_state_action_values = (next_state_values * args.gamma) + reward_batch

        criterion = nn.SmoothL1Loss()
        loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_value_(policy_net.parameters(), 100)
        optimizer.step()

    # Training loop
    env_time = 0
    for i_episode in range(args.episodes):
        print(f"Episode: {i_episode} | Time: {env_time}")
        state, info = env.reset_simulation()
        state = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)

        for t in count():
            action = select_action(state)
            observation, reward, terminated, truncated, env_time = env.run_phase(action.item())

            reward = torch.tensor([reward], device=device)
            done = terminated or truncated
            next_state = None if done else torch.tensor(observation, dtype=torch.float32, device=device).unsqueeze(0)

            memory.push(state, action, next_state, reward)
            state = next_state

            optimize_model()

            # Soft update
            for key in policy_net.state_dict():
                target_net.state_dict()[key] = \
                    policy_net.state_dict()[key] * args.tau + target_net.state_dict()[key] * (1 - args.tau)

            if terminated or truncated:
                episode_durations.append(env_time)

            if terminated:
                veh_waits, emv_waits, ped_waits = env.get_metrics()
                episode_durations.append(env_time)
                veh_waits_arr.append(veh_waits)
                emv_waits_arr.append(emv_waits)
                ped_waits_arr.append(ped_waits)

                if env_time < record:
                    policy_net.save()
                    record = env_time
                break

    print("Record:", record)

    # Plot metrics
    veh_waits, emv_waits, ped_waits = env.get_metrics()

    plot_durations(episode_durations, "Environment Duration", "Environment Duration Per Episode")
    plot_durations(veh_waits_arr, "Vehicular Wait Times", "Average Vehicle Wait Time Per Episode")
    plot_durations(ped_waits_arr, "Pedestrian Wait Times", "Average Pedestrian Wait Time Per Episode")
    plot_durations(emv_waits_arr, "EMV Wait Times", "Average EMV Wait Time Per Episode")

    plt.ioff()
    plt.show()

if __name__ == "__main__":
    main()
