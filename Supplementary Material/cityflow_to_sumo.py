import json

# This helper file is used to convert a subset of car arrivals from a real world dataset into a format workable with SUMO

# Manually worked out mappings for simplicity
mappings = {
    "road_3_2_2": "ni",
    "road_2_1_1": "ei",
    "road_1_2_0": "si",
    "road_2_3_3": "wi",
    "road_2_2_0": "no",
    "road_2_2_3": "eo",
    "road_2_2_2": "so",
    "road_2_2_1": "wo",
}

# Maps a list of traversed edges to a pre-designated SUMO route name
edges_to_route_mapping = {
    "niso": "ns",
    "niwo": "nw",
    "nieo": "ne",
    "eino": "en",
    "eiso": "es",
    "eiwo": "ew",
    "sino": "sn",
    "sieo": "se",
    "siwo": "sw",
    "wino": "wn",
    "wieo": "we",
    "wiso": "ws"
}

count = 0
lines = []

with open("Supplementary Material\hangzhou_4x4_gudang_18041610_1h.json", "r") as file:
    data = json.load(file)

    for entry in data:
        route = entry["route"]
        arrival = entry["startTime"]

        # Uncomment this line to linearly scale arrival times, in order to simulate higher densities.
        # arrival = int(arrival / 2)
        
        new_route = []
        i = 0

        # As we are only considering a subset of the RTN some edges will be irrelevant for a single intersection,
        # therefore ignore edges in the route that aren't in the mappings dictionary.
        while i < len(route) and route[i] not in mappings.keys():
            i+= 1

        # Take consecutive edges in mappings dictionary until we are no longer considering the predefined subset
        for j in range(i, len(route)):
            if route[i] in mappings.keys():
                new_route.append(mappings[route[i]])
                i += 1
            else:
                break

        # If we were able to extract a route in our predefined subset, format in a SUMO standard.
        if len(new_route) > 1:
            count += 1
            new_route = edges_to_route_mapping["".join(new_route)]
            line = f'<vehicle id="type1_{count}" type="type1" route="{new_route}" depart="{arrival}" />'
            lines.append((line, arrival))

# Sort vehicles in order of arrival to conform to SUMO standards
sorted_data = sorted(lines, key=lambda x: x[1])

# Output new routes file
for line in sorted_data:
    print(line[0])