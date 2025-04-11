import subprocess
import pickle

# Simulation parameters
Total_T = 200  # Total time steps (e.g., 500 seconds with lambda=5 -> 100 steps)
T = 20 # Planning horizon 
K = 10 # Control horizon
E = 16 # Number of total lanes
C = 12 # Number of car lanes

CarLanes = list(range(C))
Lanes = list(range(E))

# Clear log.txt
with open("log.txt", "w") as file:
    pass


# Conver the actual arrival data from last running of SUMO into array format for the LDO model
def extract_vehicle_data():
    # Mapping of route to the lane idx vehicles arrive to
    lane_array_indices = {
        "nw": 0,
        "ns": 1,
        "ne": 2,
        "en": 3,
        "ew": 4,
        "es": 5,
        "se": 6,
        "sn": 7,
        "sw": 8,
        "ws": 9,
        "we": 10,
        "wn": 11
    }
    
    full_A = []
    full_emv_A = []

    # Build arrival arrays of size lanes x time
    for _ in range(E):
        full_A.append([0] * Total_T)
    for _ in range(C):
        full_emv_A.append([0] * Total_T)

    with open("saved_departures.pkl", "rb") as f:
        actual_departures = pickle.load(f)
    
    # Iterate over array of actual arrival times
    for id, data in actual_departures.items():
        departure_time, route = data
        route = lane_array_indices[route]

        # Scale departure time down according to lambda
        departure_time = int(departure_time / 5)

        # Load into appropriate array
        if "type1" in id:
            full_A[route][departure_time] += 1
        elif "emv" in id:
            full_emv_A[route][departure_time] += 1

    # Add pedestrian arrivals
    for t in range(0, departure_time, 2):
        for l in range(C, E):
            full_A[l][t] += 1

    return full_A, full_emv_A

full_A, full_emv_A = extract_vehicle_data()


# Initialize queue lengths
q_prev = [0.0] * E
emv_q_prev = [0.0] * len(CarLanes)
all_q = []
all_emv_q = []

# Write queue sizes and arrivals for the current horizon into .dat file
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
while cur_t < Total_T:
    # Extract A_slice for current horizon and pad with zeros if beyond Total_T
    A_slice = []
    emv_A_slice = []
    for e in range(E):
        A_slice.append([full_A[e][cur_t + t] if cur_t + t < Total_T else 0 for t in range(T)])
    for e in range(C):
        emv_A_slice.append([full_emv_A[e][cur_t + t] if cur_t + t < Total_T else 0 for t in range(T)])
    
    # Write data file
    write_data_file(q_prev, emv_q_prev, A_slice, emv_A_slice, K)
    
    # Run the OPL model with relevant data
    subprocess.run(["oplrun", "model.mod", "data.dat"], check=True)

    # Extract final queue lengths to be fed into next iteration
    with open("log.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    final_line = lines[-1].split(" ")
    q_prev = final_line[0:E]
    emv_q_prev = final_line[E:E+C]

    cur_t += K
    print(f"Completed iteration at time {cur_t}")

# Post-processing to find out time when all queues were cleared
with open("log.txt", 'r') as file:
    lines = file.readlines()

    # Reverse iterate over the lines until we find the last time step queues were all zero
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        if not all(value == '0' for value in line.split()):
            # Return time * lambda, + 100 (constant to account for initial travel times to and from the junction)
            print("Simulation finished at time" , (5*(i+1)) + 120)
            break