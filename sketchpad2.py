# conflicting_routes = {
#     "N_E": {"NPed", "EPed", "E_S", "E_W", "S_E", "S_N", "W_E", "W_N"},
#     "N_S": {"NPed", "SPed", "E_S", "E_W", "S_W", "W_E", "W_N", "W_S"},
#     "N_W": {"NPed", "WPed", "E_W", "S_W"},
#     "E_N": {"NPed", "EPed", "S_N", "W_N"},
#     "E_W": {"EPed", "WPed", "N_W", "N_S", "S_N", "S_W", "W_N", "N_E"},
#     "E_S": {"EPed", "SPed", "N_S", "N_E", "S_N", "S_W", "W_S", "W_E"},
#     "W_S": {"WPed", "SPed", "N_S", "E_S"},
#     "W_E": {"WPed", "EPed", "S_W", "S_N", "S_E", "N_S", "N_E", "E_S"},
#     "W_N": {"WPed", "NPed", "N_S", "N_E", "E_N", "E_W", "S_N", "S_W"},
#     "S_N": {"SPed", "NPed", "N_W", "E_W", "E_S", "E_N", "W_N", "W_E"},
#     "S_W": {"SPed", "WPed", "W_N", "W_E", "N_W", "N_S", "E_W", "E_S"},
#     "S_E": {"SPed", "EPed", "N_E", "W_E"},
#     "NPed": {"N_E", "N_S", "N_W"},
#     "EPed": {"E_N", "E_S", "E_W"},
#     "WPed": {"W_N", "W_E", "W_S"},
#     "SPed": {"S_N", "S_E", "S_W"}
# }

conflicting_routes = {
    "N_E": {"E_S", "E_W", "S_E", "S_N", "W_E", "W_N"},
    "N_S": {"E_S", "E_W", "S_W", "W_E", "W_N", "W_S"},
    "N_W": {"E_W", "S_W"},
    "E_N": {"S_N", "W_N"},
    "E_W": {"N_W", "N_S", "S_N", "S_W", "W_N", "N_E"},
    "E_S": {"N_S", "N_E", "S_N", "S_W", "W_S", "W_E"},
    "W_S": {"N_S", "E_S"},
    "W_E": {"S_W", "S_N", "S_E", "N_S", "N_E", "E_S"},
    "W_N": {"N_S", "N_E", "E_N", "E_W", "S_N", "S_W"},
    "S_N": {"N_W", "E_W", "E_S", "E_N", "W_N", "W_E"},
    "S_W": {"W_N", "W_E", "N_W", "N_S", "E_W", "E_S"},
    "S_E": {"N_E", "W_E"}
}

route_indexes = dict()
counter = 0
for key in conflicting_routes.keys():
    route_indexes[key] = counter
    counter += 1

conflict_matrix = []
for route, conflicts in conflicting_routes.items():
    base_list = [0] * 12
    for conflict in conflicts:
        index = route_indexes[conflict]
        base_list[index] = 1
    conflict_matrix.append(base_list)

print(conflict_matrix)
