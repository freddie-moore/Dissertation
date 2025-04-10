# import libsumo as traci
import traci
from sumolib import checkBinary
import random
from utilities import normalize_array, average_dictionary

# Hardcoded durations for the green and yellow timings of a phase
GREEN_TIME = 15
YELLOW_TIME = 5

class TraciEnvironment:
    def __init__(self, show_gui, actions, route_generator, light_controller, collect_metrics=True):
        self.actions = actions
        self.iteration_count = 0
        self.route_generator = route_generator
        self.traffic_light_controller = light_controller
        self.user_defined_edges = ["ni", "ei", "si", "wi"]
        self.crossing_ids = [':0_c0', ':0_c1', ':0_c2', ':0_c3']
        self.collect_metrics = collect_metrics

        if show_gui:
            binary = "sumo-gui"
        else:
            binary= "sumo"
            
        self.start_traci(binary)
        self.reset_simulation()
        

    # Initialize the traci connection and default to all red phase
    def start_traci(self, binary):
        self.sumoBinary = checkBinary(binary)
        self.params = [ 
             "-c", "sumo_files/test.sumocfg", 
             "-W", "true",
             "--lateral-resolution", "0.2"
        ]
        traci.start([self.sumoBinary, *self.params])
        traci.trafficlight.setPhase("0", 443)

    def reset_simulation(self):
        # Reset iteration specific values
        self.current_phase = 0
        self.red_timings = [0] * self.get_n_actions()
        self.crossing_active_timings = [0] * 4
        self.step_count = 0

        # metric tracking dictionaries
        if self.collect_metrics:
            self.pedestrian_wait_times = dict()
            self.emv_wait_times = dict()
            self.veh_wait_times = dict()

        # Generate a new set of routes
        emv_count, _ = self.route_generator.generate_routes()
        self.emv_ids = {f"emv_{i}" for i in range(0,emv_count)}

        # Reload the simulation
        traci.load(self.params)
        traci.trafficlight.setPhase("0", 443)
        return self.get_state(), None

    # Returns an array representing the current queue lengths in each lane
    def get_queue_lengths(self):
        queue_lengths = []
        for edge_id in self.user_defined_edges:
            # start from 1 to exclude u-turn lane
            for i in range(1,4):
                queue_lengths.append(traci.lane.getLastStepVehicleNumber(f"{edge_id}_{i}"))

        return queue_lengths
    
    # Returns an array representing the distance of the nearest EMV from each direction, to the junction centrepoint
    def get_emv_distances(self):
        cur_emvs = self.get_emvs_in_sim(set(traci.vehicle.getIDList()))
        routes = ['n', 'e', 's', 'w']

        distances = {key: 0 for key in routes}
        for vid in cur_emvs:
            lane = traci.vehicle.getLaneIndex(vid)
            if lane != 0:
                incoming_edge = traci.vehicle.getRouteID(vid)[:1:]
                dist = traci.vehicle.getLanePosition(vid) / 500
                distances[incoming_edge] = max(distances[incoming_edge],dist)
                
        return [distances[key] for key in routes]
            
    def get_n_actions(self):
        return len(self.actions)
    
    def get_action_space(self):
        return self.actions
    
    def sample_action_space(self):
        return random.randint(0,self.get_n_actions() - 1)
    
    # Calculate and normalize model state
    def get_state(self):
        state = []
        state.extend(normalize_array(self.get_queue_lengths()))
        state.extend(self.get_phases_array())
        state.extend(normalize_array(self.get_emv_distances()))
        state.extend(normalize_array(self.get_pedestrian_wait_times(traci.person.getIDList())))

        return state

    # Returns an array indicating the number of consecutive phases that a crossing has had a pedestrian present for
    def get_pedestrian_wait_times(self, current_persons_in_sim):
        pedestrians = current_persons_in_sim
        for idx, crossing in enumerate(self.crossing_ids):
            pedestrian_flag = False
            for ped_id in pedestrians:
                if (traci.person.getWaitingTime(ped_id) > 0) and (traci.person.getNextEdge(ped_id) == crossing):
                     pedestrian_flag = True
                     break
                
            if pedestrian_flag:
                self.crossing_active_timings[idx] += 1
            else:
                self.crossing_active_timings[idx] = 0

        return self.crossing_active_timings
    
    # Returns a boolean array indicating whether a given light is currently green or not
    def get_phases_array(self):
        return self.traffic_light_controller.get_array_of_green_lights(self.current_phase)
    
    # returns sets containing the IDs of each class of actors in the simulation
    def get_actors_in_sim(self):
        all_vehicles_in_sim = set(traci.vehicle.getIDList())
        vehicles_in_sim = {vid for vid in all_vehicles_in_sim if "emv" not in vid}
        emv_vehicles_in_sim = {vid for vid in all_vehicles_in_sim if "emv" in vid}
        peds_in_sim = traci.person.getIDList()
    
        return vehicles_in_sim, emv_vehicles_in_sim, peds_in_sim
    
    def run_phase(self, new_phase):
        # get initial simulation actors
        init_vehicles, init_emvs, init_peds_in_sim = self.get_actors_in_sim()

        # calculate waiting times
        initial_wait = self.get_total_waiting_time(init_vehicles)
        initial_emv_wait = self.get_total_waiting_time(init_emvs)
        initial_ped_wait = self.get_total_pedestrian_waiting_time(init_peds_in_sim)
        
        # transition into and run the models selected phase
        self.step_count = self.traffic_light_controller.run_tls_phase(self.current_phase, new_phase, self.step_count)
        self.current_phase = new_phase
        self.update_metrics()

        # check for collisions
        collisions_penalty = self.calculate_collision_penalty()
        done = traci.simulation.getMinExpectedNumber() == 0

        # get updated simulation actors
        reg_vehicles_in_sim, emv_vehicles_in_sim, peds_in_sim = self.get_actors_in_sim()

        # calculate waiting time for vehicles left in simulation after running phase
        rem_vehicles = set(reg_vehicles_in_sim).intersection(init_vehicles)
        rem_emv_vehicles = set(emv_vehicles_in_sim).intersection(init_emvs)
        rem_peds = set(peds_in_sim).intersection(init_peds_in_sim)

        # calculate wait times
        remaining_wait = self.get_total_waiting_time(rem_vehicles)
        remaining_emv_wait = self.get_total_waiting_time(rem_emv_vehicles)
        remaining_ped_wait = self.get_total_pedestrian_waiting_time(rem_peds)

        # Calculate reward
        vehicle_reward = remaining_wait - initial_wait
        emv_reward = remaining_emv_wait - initial_emv_wait
        ped_reward = remaining_ped_wait - initial_ped_wait
        reward = -(vehicle_reward + emv_reward + ped_reward) - collisions_penalty

        return self.get_state(), reward, done, (self.step_count > 12500 or collisions_penalty>0), self.step_count


    # Calculates the collisions penalty to be applied to the agent
    def calculate_collision_penalty(self):
        collisions = len(traci.simulation.getCollisions()) > 0
        if collisions:
            collisions_penalty = 300
        else:
            collisions_penalty = 0
        
        return collisions_penalty
    
    def get_emvs_in_sim(self, current_vehicles_in_sim):
        return current_vehicles_in_sim.intersection(self.emv_ids)

    # Takes a set of vehicle ids and returns the average waiting time
    def get_total_waiting_time(self, vehicles):
        wait  = 0
        for vehicle_id in vehicles:
            wait += traci.vehicle.getWaitingTime(vehicle_id)
        if len(vehicles) > 0:
            wait = wait / len(vehicles)
        else:
            wait = 0
        
        return wait
    
    # Takes a set of pedestrian ids and returns the average waiting tiem
    def get_total_pedestrian_waiting_time(self, pedestrians):
        wait = 0
        for pedestrian_id in pedestrians:
            wait += traci.person.getWaitingTime(pedestrian_id)
        if len(pedestrians) > 0:
            wait = wait / len(pedestrians)
        else:
            wait = 0

        return wait
    
    def update_metrics(self):
        self.update_emv_wait_times()
        self.update_vehicle_wait_times()
        self.update_pedestrian_wait_times()

    def get_metrics(self):
        return average_dictionary(self.veh_wait_times), average_dictionary(self.emv_wait_times), average_dictionary(self.pedestrian_wait_times)
    
    def update_pedestrian_wait_times(self):
        for ped_id in traci.person.getIDList():
            if ped_id in self.pedestrian_wait_times.keys():
                self.pedestrian_wait_times[ped_id] = max(
                    traci.person.getWaitingTime(ped_id),
                    self.pedestrian_wait_times[ped_id]
                )
            else:
                self.pedestrian_wait_times[ped_id] = traci.person.getWaitingTime(ped_id)
        
    def update_emv_wait_times(self):
        cur_emvs = self.get_emvs_in_sim(set(traci.vehicle.getIDList()))
        for vid in cur_emvs:
            if vid in self.emv_wait_times.keys():
                self.emv_wait_times[vid] = max(self.emv_wait_times[vid], traci.vehicle.getWaitingTime(vid))
            else:
                self.emv_wait_times[vid] = traci.vehicle.getWaitingTime(vid)
    
    def update_vehicle_wait_times(self):
        for vid in set(traci.vehicle.getIDList()):
            if vid in self.veh_wait_times.keys():
                self.veh_wait_times[vid] = max(self.veh_wait_times[vid], traci.vehicle.getWaitingTime(vid))
            else:
                self.veh_wait_times[vid] = traci.vehicle.getWaitingTime(vid)
