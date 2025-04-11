import re

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

time_steps = int(400 / 5)
num_lanes = 12

regular_actor_arrivals = []
emv_arrivals = []

for i in range(num_lanes):
    regular_actor_arrivals.append([0] * time_steps)
    emv_arrivals.append([0] * time_steps)

def extract_vehicle_data(file_path=r"C:\Users\fredd\OneDrive\Documents\Dissertation\Dissertation\ReinforcementLearning\sumo_files\input_routes.rou.xml"):
    pattern = re.compile(r'<vehicle[^>]+type="(\w+)"[^>]+route="(\w+)"[^>]+depart="([\d\.]+)"')

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            match = pattern.search(line)
            
            if match:
                vehicle_type = match.group(1)
                route = match.group(2)
                depart_time = round(float(match.group(3)) / 5)
                lane = lane_array_indices[route]

                if vehicle_type == "rescue":
                    emv_arrivals[lane][depart_time] = 1
                else:
                    regular_actor_arrivals[lane][depart_time] = 1
            else:
                pass

    ## writing pedestrian data
    interval = int(50 / 5)
    stop = int(100 / 5)
    ped_arrivals = [0] * time_steps
    # Need to write based on interval and stop
    for i in range(0, stop, interval):
        ped_arrivals[i] = 1

    num_ped_lanes = 4
    for i in range(0, num_ped_lanes):
        regular_actor_arrivals.append(ped_arrivals)

    return regular_actor_arrivals, emv_arrivals
               

if __name__ == "__main__":
    extract_vehicle_data()