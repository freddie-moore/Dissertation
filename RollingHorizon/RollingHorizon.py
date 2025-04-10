import subprocess
import numpy as np
from input_routes_to_array import extract_vehicle_data
# Simulation parameters
Total_T = 50  # Total time steps (e.g., 500 seconds with lambda=5 -> 100 steps)
T = 20     # Planning horizon # total window size
K = 10        # Control horizon # window shift size
E = 16        # Number of lanes
C = 12 # number of car lanes
CarLanes = list(range(C))  # Indices 0 to 9
Lanes = list(range(E))

# Generate or load full arrival data (example: random arrivals)
full_A, full_emv_A = extract_vehicle_data()

# Initialize queue lengths
q_prev = [0.0] * E
emv_q_prev = [0.0] * len(CarLanes)
all_q = []
all_emv_q = []

# Function to write .dat file
def write_data_file(initial_q, initial_emv_q, A_slice, emv_A_slice, K):
    with open("data.dat", "w") as f:
        f.write("initial_q = [{}];\n".format(" ".join(map(str, initial_q))))
        f.write("initial_emv_q = [{}];\n".format(" ".join(map(str, initial_emv_q))))
        f.write("A = [\n")
        for e in range(E):
            f.write("  [{}]\n".format(" ".join(map(str, A_slice[e]))))
        f.write("];\n")
        f.write("emv_A = [\n")
        for e in range(C):
            f.write("  [{}]\n".format(" ".join(map(str, emv_A_slice[e]))))
        f.write("];\n")
        f.write("K = {};\n".format(K))

# Rolling horizon loop
cur_t = 0
queue_tracking = []
while cur_t < Total_T:
    # Extract A_slice for current horizon (pad with zeros if beyond Total_T)
    A_slice = []
    emv_A_slice = []
    for e in range(E):
        # print(f"e : {e}")
        # print(f"t : {T}")
        # print(f"cur_t : {cur_t}")
        # print(f"Len full_A[e] : {len(full_A[e])}")
        A_slice.append([full_A[e][cur_t + t] if cur_t + t < Total_T else 0 for t in range(T)])
    for e in range(C):
        emv_A_slice.append([full_emv_A[e][cur_t + t] if cur_t + t < Total_T else 0 for t in range(T)])
    
    # Write data file
    write_data_file(q_prev, emv_q_prev, A_slice, emv_A_slice, K)
    
    # Run OPL model (ensure oplrun is in your PATH or provide full path)
    subprocess.run(["oplrun", "model.mod", "data.dat"], check=True)
    
    # Read queue lengths from solution.txt
    with open("solution.txt", "r") as f:
        lines = f.readlines()
        for t in range(K):
            q_t = [float(val) for val in lines[0].split()]
            all_q.append(q_t)
        for t in range(K):
            emv_q_t = [float(val) for val in lines[1].split()]
            all_emv_q.append(emv_q_t)

    # for time_step in range(len(all_q)):
    #     queue_tracking.append(sum(all_q[time_step]) + sum(all_emv_q[time_step]))
    
    # Advance time
    cur_t += K
    print(f"Completed iteration at time {cur_t}")

print("Rolling horizon simulation completed.")

with open("log.txt", 'r') as file:
    lines = file.readlines()

    # Reverse iterate over the lines
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        if all(value == '0' for value in line.split()):
            print("Ans" , i)
            break

    