import random

T = 100
A = []
EMV_A = []
for i in range(0,4):
    lane_arrivals = []
    for i in range(0,T):
        if random.random() > 0.5:
            lane_arrivals.append(0)
        else:
            lane_arrivals.append(1)
    A.append(lane_arrivals)

print(A)

for i in range(0,4):
    lane_arrivals = []
    for i in range(0,T):
        if random.random() > 0.02:
            lane_arrivals.append(0)
        else:
            lane_arrivals.append(1)
    EMV_A.append(lane_arrivals)

print(EMV_A)
