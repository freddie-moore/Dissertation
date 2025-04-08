import matplotlib.pyplot as plt
import torch

# Utility function to plot metrics
def plot_durations(y_values, y_title, title):
    if y_values:
        plt.figure(1)
        durations_t = torch.tensor(y_values, dtype=torch.float)
        plt.clf()
        plt.title(title)
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

def normalize_array(arr):
    total = sum(arr)
    if total != 0:
        return [val / total for val in arr]
    return arr[:]

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() == "true":
        return True
    if v.lower() == "false":
        return False