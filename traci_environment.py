# import libsumo as traci
import traci
from sumolib import checkBinary
import random
from write_routes import generate_routes
from copy import copy
from base3experimentaiton import get_idx_to_end_phase, get_idx_to_start_phase, get_idx_of_green_phase, get_array_of_green_lights
from hardcoded_arrivals import hc_arrivals
GREEN_TIME = 30
YELLOW_TIME = 6

MAX_VEH_WAIT = 2000
MAX_PED_WAIT = 905
MIN_VEH_WAIT = -10000
MIN_PED_WAIT = -2750

class TraciEnvironment:
    def __init__(self, binary, actions, collect_metrics=False):
        self.actions = actions

        self.step_count = 0
        self.iteration_count = 0
        self.current_phase = 0
        self.red_timings = [0] * self.get_n_actions()
        self.crossing_active_timings = [0] * 4

        self.all_pedestrian_wait_times = dict()
        self.emv_wait_times = dict()
        self.collect_metrics = collect_metrics
        sumoBinary = checkBinary(binary)
        self.max_veh = float('-inf')
        self.max_ped = float('-inf')
        self.min_veh = float('+inf')
        self.min_ped = float('+inf')
        self.v_start_times = dict()
        self.v_travel_times = dict()
        self.user_defined_edges = ["ni", "ei", "si", "wi"]
        self.params = [ 
             "-c", "test.sumocfg", 
             "-W", "true",
             "--lateral-resolution", "0.2"
        ]
        
        if sumoBinary == 'sumo-gui':
            self.params.append("--start")

        if not self.collect_metrics:
            self.arrivals, emv_count, self.arrival_rate = generate_routes(iteration_count=self.iteration_count)
            self.emv_ids = {f"emv_{i}" for i in range(0,emv_count)}
        else:
            self.emv_ids = {0}
            self.arrival_rate = 0
            self.arrivals = hc_arrivals
        traci.start([sumoBinary, *self.params])
        traci.trafficlight.setPhase("0", 11)
        

    def update_travel_times(self):
        for v in traci.simulation.getDepartedIDList():
            self.v_start_times[v] = self.step_count

        for v in traci.simulation.getArrivedIDList():
            self.v_travel_times[v] = self.step_count - self.v_start_times[v]
            del self.v_start_times[v]

    def get_queue_lengths_by_edge(self, edge_id):
        waiting_times = []
        for i in range(1,4):
            waiting_times.append(traci.lane.getLastStepVehicleNumber(f"{edge_id}_{i}"))
        return waiting_times
    
    def get_future_arrivals(self):
        n = 50
        routes = ['ne', 'ns', 'nw', 'en', 'es', 'ew', 'se', 'sn', 'sw', 'wn', 'we', 'ws']
        future_arrivals = dict()
        for route in routes:
            future_arrivals[route] = 0
        for arrival_time, route in self.arrivals:
            if arrival_time < self.step_count:
                pass
            elif arrival_time > self.step_count and arrival_time < (self.step_count + n):
                future_arrivals[route] += 1
            else:
                break

        return [future_arrivals[key] for key in routes]

        





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

    
    # def set_red_timings(self, step_count):
    #     for i in range(0, len(self.red_timings)):
    #         if i != self.prev_action:
    #             self.red_timings[i] += step_count
    #         else:
    #             self.red_timings[i] = 0

    
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

    def get_emv_waiting_times_by_lane(self):
        cur_emvs = self.get_emvs_in_sim(set(traci.vehicle.getIDList()))
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

        return [waiting_times[key] for key in routes]
    
    def get_emv_distances(self):
        # current_vehicles_in_sim = set(traci.vehicle.getIDList())
        cur_emvs = self.get_emvs_in_sim(set(traci.vehicle.getIDList()))
        routes = ['n', 'e', 's', 'w']

        # Create the dictionary with all values set to -1
        distances = {key: 0 for key in routes}
        for vid in cur_emvs:
            lane = traci.vehicle.getLaneIndex(vid)
            if lane != 0: #todo: TYPICALLY LANE 0 INDICATES VEHICLE IS STUCK ON JUNCTION, HOW WOULD WE RESOLVE THIS
                # dist = traci.vehicle.getLanePosition(vid)
                incoming_edge = traci.vehicle.getRouteID(vid)[:1:]
                # route = f"{incoming_edge}i_{lane}"
                dist = traci.vehicle.getLanePosition(vid) / 500
                distances[incoming_edge] = max(distances[incoming_edge],dist)
                
        
        # print("ret :", distances)
        return [distances[key] for key in routes]

    def get_emv_numbers(self):
        cur_emvs = self.get_emvs_in_sim(set(traci.vehicle.getIDList()))
        routes = ['n', 'e', 's', 'w']

        # Create the dictionary with all values set to -1
        distances = {key: 0 for key in routes}
        for vid in cur_emvs:
            lane = traci.vehicle.getLaneIndex(vid)
            if lane != 0: #todo: TYPICALLY LANE 0 INDICATES VEHICLE IS STUCK ON JUNCTION, HOW WOULD WE RESOLVE THIS
                incoming_edge = traci.vehicle.getRouteID(vid)[:1:]
                # route = f"{incoming_edge}i_{lane}"
                distances[incoming_edge] += 1
        
        # print("ret : ", distances)
        return [distances[key] for key in routes]

            
    def get_n_actions(self):
        return len(self.actions)
    
    def get_action_space(self):
        return self.actions
    
    def sample_action_space(self):
        return random.randint(0,self.get_n_actions() - 1)
    
    def get_state(self):
        state = []
        state.extend(self.normalize_array(self.get_queue_lengths()))
        state.extend(self.get_phases_array())
        # state.extend(self.normalize_array(self.get_emv_numbers()))
        # state.extend(self.normalize_array(self.get_emv_distances()))
        # state.extend(self.normalize_array(self.get_pedestrian_wait_times(traci.person.getIDList())))
        # state.extend(self.normalize_array(self.get_future_arrivals()))
        # state.extend(self.normalize_array(self.get_emv_waiting_times_by_lane()))

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
        return get_array_of_green_lights(self.current_phase)
    
    

    def run_phase(self, new_phase):
        # store all vehicles currently in simulation
        all_vehicles_in_sim = set(traci.vehicle.getIDList())

        # extract regular vehicles and calculate total waiting time
        reg_vehicles_in_sim = {vid for vid in all_vehicles_in_sim if "emv" not in vid}
        emv_vehicles_in_sim = {vid for vid in all_vehicles_in_sim if "emv" in vid}
        

        init_vehicles = reg_vehicles_in_sim
        init_emvs = emv_vehicles_in_sim
        init_peds_in_sim = traci.person.getIDList()

        initial_wait = self.get_total_waiting_time(init_vehicles)
        initial_emv_wait = self.get_total_waiting_time(init_emvs)
        init_ped_wait = self.get_total_pedestrian_waiting_time(init_peds_in_sim)
        
        # End previous phase
        end_phase_idx = get_idx_to_end_phase(self.current_phase, new_phase)
        traci.trafficlight.setPhase("0", end_phase_idx)
        if self.collect_metrics == False:
            self.step_count += YELLOW_TIME
            traci.simulationStep(self.step_count)
        else:
            for i in range(0, YELLOW_TIME):
                self.step_count += 1
                traci.simulationStep(self.step_count)
                self.update_travel_times()

    
        # Start next phase
        start_phase_idx = get_idx_to_start_phase(self.current_phase, new_phase)
        traci.trafficlight.setPhase("0", start_phase_idx)
        if self.collect_metrics == False:
            self.step_count += YELLOW_TIME
            traci.simulationStep(self.step_count)
        else:
            for i in range(0, YELLOW_TIME):
                self.step_count += 1
                traci.simulationStep(self.step_count)
                self.update_travel_times()

        # Green phase
        green_phase_idx = get_idx_of_green_phase(new_phase)
        traci.trafficlight.setPhase("0", green_phase_idx)
        if self.collect_metrics == False:
            self.step_count += GREEN_TIME
            traci.simulationStep(self.step_count)
        else:
            for i in range(0, GREEN_TIME):
                self.step_count += 1
                traci.simulationStep(self.step_count)
                self.update_travel_times()

        self.current_phase = new_phase
        # get_array_of_green_lights(self.current_phase, True)
        # self.set_red_timings((YELLOW_TIME * 2) + GREEN_TIME)

        # calculate collisions bonus and stop flags
        collisions = len(traci.simulation.getCollisions()) > 0
        if collisions:
            collisions_bonus = 300
        else:
            collisions_bonus = 0
        done = traci.simulation.getMinExpectedNumber() == 0
        
        # get updated simulation state
        all_vehicles_in_sim = set(traci.vehicle.getIDList())
        reg_vehicles_in_sim = {vid for vid in all_vehicles_in_sim if "emv" not in vid}
        emv_vehicles_in_sim = {vid for vid in all_vehicles_in_sim if "emv" in vid}
        peds_in_sim = traci.person.getIDList()
        
        # plot emv metrics
        self.update_emv_wait_times(all_vehicles_in_sim)
        self.update_pedestrian_wait_times()

        # calculate waiting time for vehicles left in simulation after running phase
        rem_vehicles = set(reg_vehicles_in_sim).intersection(init_vehicles)
        rem_emv_vehicles = set(emv_vehicles_in_sim).intersection(init_emvs)
        rem_peds = set(peds_in_sim).intersection(init_peds_in_sim)

        # calculate reward
        remaining_wait = self.get_total_waiting_time(rem_vehicles)
        remaining_emv_wait = self.get_total_waiting_time(rem_emv_vehicles)
        remaining_ped_wait = self.get_total_pedestrian_waiting_time(rem_peds)

        vehicle_reward = remaining_wait - initial_wait
        emv_reward = remaining_emv_wait - initial_emv_wait

        reward = -(vehicle_reward + emv_reward + remaining_ped_wait) - collisions_bonus

        return self.get_state(), reward, done, (self.step_count > 12500 or collisions), (self.step_count, self.get_avg_ped_wait(), self.get_avg_emv_wait(), collisions, self.arrival_rate)
    
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

    def get_metrics(self):
        return self.v_travel_times
    
    def reset(self):
        self.step_count = 0
        self.current_phase = 0
        self.iteration_count += 1
        self.red_timings = [0] * self.get_n_actions()
        self.all_pedestrian_wait_times = dict()
        self.emv_wait_times = dict()
        self.crossing_active_timings = [0] * 4
        if not self.collect_metrics:
            self.arrivals, emv_count, self.arrival_rate = generate_routes(self.iteration_count)
            self.emv_ids = {f"emv_{i}" for i in range(0,emv_count)} 
        else:
            self.arrivals = hc_arrivals
            self.emv_ids = {0}
            self.arrival_rate = 0
        traci.load(self.params)
        traci.trafficlight.setPhase("0", 11)
        return self.get_state(), None
    
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