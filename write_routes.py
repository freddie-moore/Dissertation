import random
import numpy as np

random.seed(10)

def generate_routes():
    

    route_ids = {
        "ne": 0.4 / 3, "ns": 0.4 / 3, "nw": 0.4 / 3,  # 40% for 'n' routes
        "en": 0.25 / 3, "es": 0.25 / 3, "ew": 0.25 / 3,  # 30% for 'e' routes
        "se": 0.15 / 3, "sn": 0.15 / 3, "sw": 0.15 / 3,  # 15% for 's' routes
        "wn": 0.15 / 3, "we": 0.15 / 3, "ws": 0.15 / 3 ,  # 15% for 'w' routes
    }

    routes_list = list(route_ids.keys())
    print(routes_list)
    weights = list(route_ids.values())

    n = 600 # number of vehicles
    arrival_rate = 1.5
    arrival_times = np.cumsum(np.random.exponential(1 / arrival_rate, size=n))

    with open("input_routes.rou.xml", "w") as routes:
        routes.write("""<routes>
            <vType id="type1" accel="0.8" decel="4.5" sigma="0.5" length="5" maxSpeed="70"/>
            <route id="ne" edges="ni eo"/>
            <route id="ns" edges="ni so"/>
            <route id="nw" edges="ni wo"/>
            <route id="en" edges="ei no"/>
            <route id="es" edges="ei so"/>
            <route id="ew" edges="ei wo"/>
            <route id="sn" edges="si no"/>
            <route id="se" edges="si eo"/>
            <route id="sw" edges="si wo"/>
            <route id="wn" edges="wi no"/>
            <route id="we" edges="wi eo"/>
            <route id="ws" edges="wi so"/>
            <route id="nn" edges="ni no"/>
            <route id="ss" edges="si so"/>
            <route id="ee" edges="ei eo"/>
            <route id="ww" edges="wi wo"/>
        """)

        for i, arrival_time in enumerate(arrival_times):
            route = random.choices(routes_list)[0]
            # route = random.choices(["ns", "ew", "se", "wn"], weights=[30, 20, 15, 15], k=1)[0]
            route = random.choice(routes_list)
            vehicle_type = "type1"
            routes.write(f"<vehicle id=\"{route}_{i}\" type=\"{vehicle_type}\" route=\"{route}\" depart=\"{arrival_time}\" />\n")

        routes.write("</routes>")


if __name__ == "__main__":
    generate_routes()