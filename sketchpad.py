import random

a = []
num_lanes = 12

for i in range(0,num_lanes):
    arrivals = []
    for i in range(0, 50, 5):
        if random.random() < 0.5:
            arrivals.append(2)
        else:
            arrivals.append(0)
    a.append(arrivals)

print(f"A = {a};")