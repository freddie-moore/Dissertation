import random
import numpy as np

random.seed(10)

def generate_routes():
    

    routes = {
        "ne": 0.4 / 3, "ns": 0.4 / 3, "nw": 0.4 / 3,  # 40% for 'n' routes
        "en": 0.3 / 3, "es": 0.3 / 3, "ew": 0.3 / 3,  # 30% for 'e' routes
        "se": 0.15 / 3, "sn": 0.15 / 3, "sw": 0.15 / 3,  # 15% for 's' routes
        "wn": 0.15 / 3, "we": 0.15 / 3, "ws": 0.15 / 3   # 15% for 'w' routes
    }

    route_ids = list(routes.keys())

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
        """)
        
        for id in route_ids:
            routes.write(f"""
            <personFlow id="p_{id}" begin="0" end="{n}" period="50">
                <walk route="{id}"/>
            </personFlow>
                         """)
        for i, arrival_time in enumerate(arrival_times):
            route = random.choice(route_ids)
            vehicle_type = "type1"

            routes.write(f"<vehicle id=\"{route}_{i}\" type=\"{vehicle_type}\" route=\"{route}\" depart=\"{arrival_time}\" />\n")

        routes.write("</routes>")


if __name__ == "__main__":
    generate_routes()