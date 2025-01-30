import libsumo as traci
# import traci
from sumolib import checkBinary
import random
from write_routes import generate_routes
from copy import copy
GREEN_TIME = 30
YELLOW_TIME = 6

MAX_VEH_WAIT = 2000
MAX_PED_WAIT = 905
MIN_VEH_WAIT = -10000
MIN_PED_WAIT = -2750

class TraciEnvironment:
    def __init__(self, binary, actions):
        self.actions = actions

        self.step_count = 0
        self.prev_action = 0
        self.red_timings = [0] * self.get_n_actions()
        self.crossing_active_timings = [0] * 4

        self.all_pedestrian_wait_times = dict()
        self.emv_wait_times = dict()

        sumoBinary = checkBinary(binary)
        self.max_veh = float('-inf')
        self.max_ped = float('-inf')
        self.min_veh = float('+inf')
        self.min_ped = float('+inf')

        self.user_defined_edges = ["ni", "ei", "si", "wi"]
        self.params = [ 
             "-c", "test.sumocfg", 
             "-W", "true",
             "--lateral-resolution", "0.2"
        ]
        
        if sumoBinary == 'sumo-gui':
            self.params.append("--start")

        traci.start([sumoBinary, *self.params])
        type1_count, emv_count = generate_routes()
        self.emv_ids = {f"emv_{i}" for i in range(0,emv_count)}

    def get_queue_lengths_by_edge(self, edge_id):
        waiting_times = []
        for i in range(1,4):
            waiting_times.append(traci.lane.getLastStepVehicleNumber(f"{edge_id}_{i}"))
        return waiting_times
    
    def get_queue_lengths(self):
        queues_length = []
        for edge_id in self.user_defined_edges:
            queues_length.extend(self.get_queue_lengths_by_edge(edge_id))
        return queues_length

    
    def normalize_array(self, arr):
        total = sum(arr)
        if total != 0:
            return [val / total for val in arr]
        return arr[:]

    
    def set_red_timings(self, step_count):
        for i in range(0, len(self.red_timings)):
            if i != self.prev_action:
                self.red_timings[i] += step_count
            else:
                self.red_timings[i] = 0

    
    def get_waiting_times_by_edge(self, edge_id):
        waiting_times = []
        # start from 1 to exclude u-turn lane
        for i in range(1,4):
            waiting_times.append(traci.lane.getWaitingTime(f"{edge_id}_{i}"))
        return waiting_times
    
    def get_waiting_times(self):
        waiting_times = []
        for edge_id in self.user_defined_edges:
            waiting_times.extend(self.get_waiting_times_by_edge(edge_id))
        return waiting_times

    def get_emv_waiting_times_by_lane(self, current_vehicles_in_sim):
        cur_emvs = self.get_emvs_in_sim(current_vehicles_in_sim)
        routes = [f"{d}i_{i}" for d in ['n', 'e', 's', 'w'] for i in range(1,4)]

        # Create the dictionary with all values set to -1
        waiting_times = {key: 0 for key in routes}
        for vid in cur_emvs:
            lane = traci.vehicle.getLaneIndex(vid)
            if lane != 0: #todo: TYPICALLY LANE 0 INDICATES VEHICLE IS STUCK ON JUNCTION, HOW WOULD WE RESOLVE THIS
                # dist = traci.vehicle.getLanePosition(vid)
                incoming_edge = traci.vehicle.getRouteID(vid)[:1:]
                route = f"{incoming_edge}i_{lane}"
                wait = traci.vehicle.getWaitingTime(vid)
                waiting_times[route] += wait

        return list(waiting_times.values())
    
    def get_emv_distances(self, current_vehicles_in_sim):
        # current_vehicles_in_sim = set(traci.vehicle.getIDList())
        cur_emvs = self.get_emvs_in_sim(current_vehicles_in_sim)
        routes = [f"{d}i_{i}" for d in ['n', 'e', 's', 'w'] for i in range(1,4)]

        # Create the dictionary with all values set to -1
        distances = {key: 0 for key in routes}
        for vid in cur_emvs:
            lane = traci.vehicle.getLaneIndex(vid)
            if lane != 0: #todo: TYPICALLY LANE 0 INDICATES VEHICLE IS STUCK ON JUNCTION, HOW WOULD WE RESOLVE THIS
                # dist = traci.vehicle.getLanePosition(vid)
                incoming_edge = traci.vehicle.getRouteID(vid)[:1:]
                route = f"{incoming_edge}i_{lane}"
                dist = traci.vehicle.getLanePosition(vid) / 500
                distances[route] = max(distances[route],dist)
                
        
        return list(distances.values())
        

            
    def get_n_actions(self):
        return len(self.actions)
    
    def get_action_space(self):
        return self.actions
    
    def sample_action_space(self):
        return random.randint(0,self.get_n_actions() - 1)
    
    def get_state(self, current_persons_in_sim, current_vehicles_in_sim):
        state = []
        state.extend(self.normalize_array(self.get_queue_lengths()))
        # state.extend(self.normalize_array(self.red_timings))
        # state.extend(self.normalize_array(self.get_waiting_times()))
        # state.extend(self.normalize_array(self.get_pedestrian_wait_times(current_persons_in_sim)))
        state.extend(self.get_emv_distances(current_vehicles_in_sim))
        state.extend(self.normalize_array(self.get_emv_waiting_times_by_lane(current_vehicles_in_sim)))
        # self.get_emv_flags(current_vehicles_in_sim)

        return state

    def print_non_intersection_elements(self, set1, set2):
        """
        Prints all elements that are not in the intersection of two sets.

        Parameters:
        - set1: The first set.
        - set2: The second set.
        """
        # Calculate the intersection of the two sets
        intersection = set1 & set2
        
        # Calculate elements that aren't in the intersection
        non_intersection_elements = (set1 | set2) - intersection
        
        # Print the result
        if(non_intersection_elements):
            print("Elements not in the intersection:", non_intersection_elements)
        else:
            print("All present and okay")

    def update_pedestrian_wait_times(self):
        for ped_id in traci.person.getIDList():
            if ped_id in self.all_pedestrian_wait_times.keys():
                self.all_pedestrian_wait_times[ped_id] = max(
                    traci.person.getWaitingTime(ped_id),
                    self.all_pedestrian_wait_times[ped_id]
                )
            else:
                self.all_pedestrian_wait_times[ped_id] = traci.person.getWaitingTime(ped_id)
        
    def update_emv_wait_times(self, current_vehicles_in_sim):
        cur_emvs = self.get_emvs_in_sim(current_vehicles_in_sim)
        for vid in cur_emvs:
            if vid in self.emv_wait_times.keys():
                self.emv_wait_times[vid] = max(self.emv_wait_times[vid], traci.vehicle.getWaitingTime(vid))
            else:
                self.emv_wait_times[vid] = traci.vehicle.getWaitingTime(vid)

    def get_pedestrian_wait_times(self, current_persons_in_sim):
        crossings = [':0_c0', ':0_c1', ':0_c2', ':0_c3']
        pedestrians = current_persons_in_sim
        for idx, crossing in enumerate(crossings):
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
    

    def get_phases_array(self):
        phases_array = [0] * self.get_n_actions()
        phases_array[self.prev_action] = 1
        return phases_array
    
    

    def run_phase(self, phase):
        yellow_phase = phase * 2

        current_vehicles_in_sim = {vid for vid in traci.vehicle.getIDList() if "emv" not in vid}

        init_vehicles = current_vehicles_in_sim
        # init_ped = set(traci.person.getIDList())
        # init_emvs = self.get_emvs_in_sim(current_vehicles_in_sim)

        initial_wait = self.get_total_waiting_time(init_vehicles)
        # initial_ped_wait = self.get_total_pedestrian_waiting_time(init_ped)
        # initial_emv_wait = self.get_total_waiting_time(init_emvs)
        
        if phase != self.prev_action:
            # End previous phase
            traci.trafficlight.setPhase("0", self.prev_action*2)
            self.step_count += YELLOW_TIME
            traci.simulationStep(self.step_count)

            # Initial yellow phase
            traci.trafficlight.setPhase("0", yellow_phase)
            self.step_count += YELLOW_TIME
            traci.simulationStep(self.step_count)

        # Green phase
        traci.trafficlight.setPhase("0", yellow_phase+1)
        self.step_count += GREEN_TIME
        traci.simulationStep(self.step_count)

        self.prev_action = phase
        self.set_red_timings((YELLOW_TIME * 2) + GREEN_TIME)
        self.update_pedestrian_wait_times()

        current_vehicles_in_sim = {vid for vid in traci.vehicle.getIDList() if "emv" not in vid}
        current_persons_in_sim = set(traci.person.getIDList())
        self.update_emv_wait_times(traci.vehicle.getIDList())

        collisions = len(traci.simulation.getCollisions()) > 0
        if collisions:
            collisions_bonus = 300
        else:
            collisions_bonus = 0

        done = traci.simulation.getMinExpectedNumber() == 0
        
        rem_vehicles = set(current_vehicles_in_sim).intersection(init_vehicles)
        # rem_ped = set(current_persons_in_sim).intersection(init_ped)
        # rem_emvs = self.get_emvs_in_sim(current_vehicles_in_sim).intersection(init_emvs)

        remaining_wait = self.get_total_waiting_time(rem_vehicles)
        # remaining_ped_wait = self.get_total_pedestrian_waiting_time(rem_ped)
        # remaining_emv_wait = self.get_total_waiting_time(rem_emvs, True)

        vehicle_reward = remaining_wait - initial_wait
        # ped_reward = remaining_ped_wait - initial_ped_wait
        # emv_reward = max(remaining_emv_wait - initial_emv_wait, 0)
        # print(f"EMV Reward : {emv_reward}")
        # print(f"EMVs in SIM : {rem_emvs}")
        # if collisions_bonus > 0:
        #     print(f"Vehicle Reward: {vehicle_reward} | Ped Reward: {ped_reward} | Collision Bonus: {collisions_bonus}")
        reward = -(vehicle_reward) - collisions_bonus #+ emv_reward)

        return self.get_state(current_persons_in_sim, current_vehicles_in_sim), reward, done, (self.step_count > 12500 or collisions), (self.step_count, self.get_avg_ped_wait(), self.get_avg_emv_wait())
    
    def get_avg_ped_wait(self):
        if self.all_pedestrian_wait_times:
            return sum(self.all_pedestrian_wait_times.values()) / len(self.all_pedestrian_wait_times)
        else:
            return 0

    def get_avg_emv_wait(self):
        if self.emv_wait_times:
            return sum(self.emv_wait_times.values()) / len(self.emv_wait_times)
        else:
            return 0
    
    def get_emvs_in_sim(self, current_vehicles_in_sim):
        return current_vehicles_in_sim.intersection(self.emv_ids)


    def get_total_waiting_time(self, vehicles, emv_flag=False):
        wait  = 0
        for vehicle_id in vehicles:
            wait += traci.vehicle.getWaitingTime(vehicle_id)
        if len(vehicles) > 0:
            wait = wait / len(vehicles)
        else:
            wait = 0
        
        return wait
    
    def get_total_pedestrian_waiting_time(self, pedestrians):
        wait = 0
        for pedestrian_id in pedestrians:
            wait += traci.person.getWaitingTime(pedestrian_id)
        if len(pedestrians) > 0:
            wait = wait / len(pedestrians)
        else:
            wait = 0

        return wait

    def update_pedestrian_wait_times(self):
        for pedestrian_id in traci.person.getIDList():
            if pedestrian_id in self.all_pedestrian_wait_times:
                self.all_pedestrian_wait_times[pedestrian_id] = max(self.all_pedestrian_wait_times[pedestrian_id], traci.person.getWaitingTime(pedestrian_id))
            else:
                self.all_pedestrian_wait_times[pedestrian_id] = traci.person.getWaitingTime(pedestrian_id)

    def reset(self):
        self.step_count = 0
        self.prev_action = 0
        self.red_timings = [0] * self.get_n_actions()
        self.all_pedestrian_wait_times = dict()
        self.emv_wait_times = dict()
        self.crossing_active_timings = [0] * 4
        traci.load(self.params)
        return self.get_state(set(), set()), None
    
    def normalize_value(self, value, lower_bound, upper_bound):
        if not (lower_bound < value < upper_bound):
            print(f"Normalization Error | {lower_bound} | {value} | {upper_bound}")

        return (value - lower_bound) / (upper_bound - lower_bound)

    def get_max_veh(self):
        return self.max_veh
    
    def get_max_ped(self):
        return self.max_ped

    def get_min_veh(self):
        return self.min_veh

    def get_min_ped(self):
        return self.min_ped  