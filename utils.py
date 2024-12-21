import matplotlib.pyplot as plt
import torch
from memory import Transition
import torch.nn as nn

def plot_durations(episode_durations, pedestrian_waits, show_result=False):
    """
    Plots episode durations on the primary y-axis and additional data on a secondary y-axis.

    Args:
        episode_durations (list): List of episode durations.
        secondary_data (list): List of values to be plotted on the secondary y-axis.
        show_result (bool): Whether to display the final result or training status.
    """
    plt.figure(1)
    plt.clf()

    durations_t = torch.tensor(episode_durations, dtype=torch.float)
    pedestrian_t = torch.tensor(pedestrian_waits, dtype=torch.float)

    fig, ax1 = plt.subplots()
    ax1.set_title('Result' if show_result else 'Training...')
    ax1.set_xlabel('Episode')
    ax1.set_ylabel('Duration', color='blue')
    ax1.plot(durations_t.numpy(), label='Duration', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    # Plot rolling mean of durations if enough data is available
    if len(durations_t) >= 100:
        means = durations_t.unfold(0, 100, 1).mean(1).view(-1)
        means = torch.cat((torch.zeros(99), means))
        ax1.plot(means.numpy(), label='Duration Mean', linestyle='--', color='cyan')

    # Annotate minimum value in durations
    min_val, min_idx = durations_t.min().item(), durations_t.argmin().item()
    ax1.annotate(
        f'{min_val:.2f}',
        xy=(min_idx, min_val),
        xytext=(min_idx, min_val + 5),
        arrowprops=dict(facecolor='black', arrowstyle='->'),
        fontsize=10,
        color='red'
    )

    # Add a secondary y-axis for secondary data
    ax2 = ax1.twinx()
    ax2.set_ylabel('Mean Pedestrian Wait', color='green')
    ax2.plot(pedestrian_t.numpy(), label='Secondary Data', color='green')
    ax2.tick_params(axis='y', labelcolor='green')

    # Save the plot and display a pause for updates
    plt.savefig("training_graph_with_secondary_data")
    plt.pause(0.001)
