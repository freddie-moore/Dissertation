import random
import numpy as np

random.seed(10)

def generate_routes(num_cars):
    

    routes = {
        "ne": 0.4 / 3, "ns": 0.4 / 3, "nw": 0.4 / 3,  # 40% for 'n' routes
        "en": 0.3 / 3, "es": 0.3 / 3, "ew": 0.3 / 3,  # 30% for 'e' routes
        "se": 0.15 / 3, "sn": 0.15 / 3, "sw": 0.15 / 3,  # 15% for 's' routes
        "wn": 0.15 / 3, "we": 0.15 / 3, "ws": 0.15 / 3   # 15% for 'w' routes
    }

    route_ids = list(routes.keys())
    pedestrian_routes = {"ns", "sn", "ew", "we"}

    n = num_cars
    arrival_rate = random.randrange(1,5)
    arrival_times = np.cumsum(np.random.exponential(1 / arrival_rate, size=n))

    with open("input_routes.rou.xml", "w") as routes:
        routes.write("""<routes>
            <vType id="type1" accel="0.8" decel="4.5" sigma="0.5" length="5" maxSpeed="70"/>
            <vType id="rescue" vClass="emergency" speedFactor="1.5" guiShape="emergency">
                <param key="has.bluelight.device" value="true"/>
            </vType>
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
        
        # for id in pedestrian_routes:
        #     routes.write(f"""
        #     <personFlow id="p_{id}" begin="0" end="{n}" period="50">
        #         <walk route="{id}"/>
        #     </personFlow>
        #                  """)
            
        type1_id = 0
        emv_id = 0
        for i, arrival_time in enumerate(arrival_times):
            route = "ns"
            type1_id += 1
            routes.write(f"<vehicle id=\"type1_{type1_id}\" type=\"type1\" route=\"{route}\" depart=\"0\" />\n")

        routes.write("</routes>")

        return type1_id, emv_id


if __name__ == "__main__":
    generate_routes()