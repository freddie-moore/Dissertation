import random

a = []
emv_a = []
num_lanes = 12

for i in range(0,num_lanes):
    arrivals = []
    emv_arrivals = []
    for i in range(0, 200, 5):
        if random.random() < 0.5:
            arrivals.append(2)
        else:
            arrivals.append(0)

        if random.random() > 0.99:
            emv_a.append(1)
        else:
            emv_a.append(0)
    a.append(arrivals)

print(f"A = {a};")