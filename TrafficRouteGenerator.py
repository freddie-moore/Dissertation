import random
import numpy as np

class TrafficRouteGenerator:
    def __init__(self, num_cars, arrival_rate):
        # Define route probabilities
        self.routes = {
            "ne": 0.4 / 3, "ns": 0.4 / 3, "nw": 0.4 / 3,  # 40% for 'n' routes
            "en": 0.3 / 3, "es": 0.3 / 3, "ew": 0.3 / 3,  # 30% for 'e' routes
            "se": 0.15 / 3, "sn": 0.15 / 3, "sw": 0.15 / 3,  # 15% for 's' routes
            "wn": 0.15 / 3, "we": 0.15 / 3, "ws": 0.15 / 3   # 15% for 'w' routes
        }
        
        self.route_ids = list(self.routes.keys())
        self.pedestrian_routes = {"ns", "sn", "ew", "we"}
        
        # Default values
        self.num_cars = num_cars
        self.arrival_rate = arrival_rate
        self.output_file = "sumo_files/input_routes.rou.xml"

    
    def set_seed(self, iteration_count=None):
        """Set random seed based on iteration count"""
        if iteration_count is not None:
            random.seed(iteration_count % 10)
        return self
            
    def generate_arrival_times(self):
        """Generate arrival times using exponential distribution"""
        return np.cumsum(np.random.exponential(1 / self.arrival_rate, size=self.num_cars))
    
    def write_route_definitions(self, file):
        """Write route definitions to file"""
        file.write("""<routes>
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
    
    def write_pedestrian_flows(self, file):
        """Write pedestrian flow definitions to file"""
        for id in self.pedestrian_routes:
            file.write(f"""
            <personFlow id="p_{id}" begin="0" end="{self.num_cars}" period="50">
                <walk route="{id}"/>
            </personFlow>
                         """)
    
    def write_vehicle_definitions(self, file, arrival_times):
        """Write vehicle definitions to file and return emergency vehicle count"""
        type1_id = 0
        emv_id = 0
        routes_taken = []
        
        for i, arrival_time in enumerate(arrival_times):
            route = random.choice(self.route_ids)
            routes_taken.append(route)
            
            if random.random() > 0.98:
                emv_id += 1
                file.write(f"<vehicle id=\"emv_{emv_id}\" type=\"rescue\" route=\"{route}\" depart=\"{arrival_time}\" />\n")
            else:
                type1_id += 1
                file.write(f"<vehicle id=\"type1_{type1_id}\" type=\"type1\" route=\"{route}\" depart=\"{arrival_time}\" />\n")
        
        return emv_id, routes_taken
    
    def generate_routes(self):
        # Generate arrival times
        arrival_times = self.generate_arrival_times()
        
        routes_taken = []
        with open(self.output_file, "w") as routes_file:
            # Write route definitions
            self.write_route_definitions(routes_file)
            
            # Write pedestrian flows
            self.write_pedestrian_flows(routes_file)
            
            # Write vehicle definitions
            emv_id, routes_taken = self.write_vehicle_definitions(routes_file, arrival_times)
            
            # Close routes tag
            routes_file.write("</routes>")
        
        return emv_id, routes_taken


if __name__ == "__main__":
    generator = TrafficRouteGenerator()
    emv_count, _ = generator.generate_routes()
    print(f"Generated routes with {emv_count} emergency vehicles")