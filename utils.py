import matplotlib.pyplot as plt
import torch
from memory import Transition
import torch.nn as nn
import numpy as np

def plot_durations(y_values, y_title, show_result=False):
    plt.figure(1)
    durations_t = torch.tensor(y_values, dtype=torch.float)
    plt.clf()
    plt.title('Result' if show_result else 'Training...')
    plt.xlabel('Episode')
    plt.ylabel(y_title)
    plt.plot(durations_t.numpy())

    if len(durations_t) >= 100:
        means = durations_t.unfold(0, 100, 1).mean(1).view(-1)
        means = torch.cat((torch.zeros(99), means))
        plt.plot(means.numpy())

    min_val, min_idx = durations_t.min().item(), durations_t.argmin().item()
    plt.annotate(
        f'{min_val:.2f}',
        xy=(min_idx, min_val),
        xytext=(min_idx, min_val + 5),
        arrowprops=dict(facecolor='black', arrowstyle='->'),
        fontsize=10,
        color='red'
    )
    plt.savefig(y_title)
    plt.pause(0.001)



def plot_density(binary_array):
    plt.figure()
    plt.clf()
    plt.title('Density of 1s Over Time')
    plt.xlabel('Index')
    plt.ylabel('Density of 1s')
    
    # Compute cumulative density of 1s
    cumulative_ones = np.cumsum(binary_array)
    density = cumulative_ones / (np.arange(1, len(binary_array) + 1))
    
    plt.plot(density, label='Density of 1s', color='blue')
    
    plt.ylim(0, 1)  # Since density is between 0 and 1
    plt.legend()
    plt.grid()
    plt.savefig('density_plot.png')