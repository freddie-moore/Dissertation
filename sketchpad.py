from itertools import combinations

conflicting_routes = {
    "N_E": {"NPed", "EPed", "E_S", "E_W", "S_E", "S_N", "W_E", "W_N"},
    "N_S": {"NPed", "SPed", "E_S", "E_W", "S_W", "W_E", "W_N", "W_S"},
    "N_W": {"NPed", "WPed", "E_W", "S_W"},
    "E_N": {"NPed", "EPed", "S_N", "W_N"},
    "E_W": {"EPed", "WPed", "N_W", "N_S", "S_N", "S_W", "W_N", "N_E"},
    "E_S": {"EPed", "SPed", "N_S", "N_E", "S_N", "S_W", "W_S", "W_E"},
    "W_S": {"WPed", "SPed", "N_S", "E_S"},
    "W_E": {"WPed", "EPed", "S_W", "S_N", "S_E", "N_S", "N_E", "E_S"},
    "W_N": {"WPed", "NPed", "N_S", "N_E", "E_N", "E_W", "S_N", "S_W"},
    "S_N": {"SPed", "NPed", "N_W", "E_W", "E_S", "E_N", "W_N", "W_E"},
    "S_W": {"SPed", "WPed", "W_N", "W_E", "N_W", "N_S", "E_W", "E_S"},
    "S_E": {"SPed", "EPed", "N_E", "W_E"},
    "NPed": {"N_E", "N_S", "N_W"},
    "EPed": {"E_N", "E_S", "E_W"},
    "WPed": {"W_N", "W_E", "W_S"},
    "SPed": {"S_N", "S_E", "S_W"}
}

def is_valid_set(route_set):
    for route in route_set:
        for other_route in route_set:
            if route != other_route and other_route in conflicting_routes[route]:
                return False
    return True

all_routes = list(conflicting_routes.keys())
valid_sets = {
    1: [],
    2: [],
    3: [],
    4: []
}

for r in range(1, len(all_routes) + 1):
    for subset in combinations(all_routes, r):
        if is_valid_set(subset):
            valid_sets[len(subset)].append(set(subset))

for key, value in valid_sets.items():
    print(f"Phases with {key} traffic lights : {len(value)}")

phases = valid_sets[4]

# lane_count = dict()

# for i in range(1,5):
#     phases = valid_sets[i]
#     for phase in phases:
#         for light in phase:
#             if light in lane_count.keys():
#                 lane_count[light] += 1
#             else:
#                 lane_count[light] = 1

#     print(lane_count)

order = {"N_W": 0,"N_S": 1,"N_E": 2, "E_N": 4,"E_W": 5,"E_S": 6,"S_E": 8,"S_N": 9,"S_W": 10,"W_S": 12,"W_E": 13,"W_N": 14,"NPed":16,"EPed":17,"SPed":18,"WPed": 19}
right_turns = {"N_E", "E_S", "S_W", "W_N"}
from copy import deepcopy
base = list("rrrrrrrrrrrrrrrrrrrr")
print(base)
for phase in phases:
    light_config = deepcopy(base)
    for light in phase:
        index = order[light]
        light_config[index] = "y"
        if light in right_turns:
            light_config[index+1] = "y"
    light_config = "".join(light_config)
    print(f'<phase duration="100" state="{light_config}"/>')
    light_config = light_config.replace("y","g")
    print(f'<phase duration="100" state="{light_config}"/>')
    # if light_config.count("g") != 4:
    #     print("err")

