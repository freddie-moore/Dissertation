import libsumo as traci
# import traci
from sumolib import checkBinary
import random

GREEN_TIME = 30
YELLOW_TIME = 6

class TraciEnvironment:
    def __init__(self, binary, actions):
        self.actions = actions

        self.step_count = 0
        self.prev_action = 0
        self.red_timings = [0] * self.get_n_actions()
        self.all_pedestrian_wait_times = dict()
        sumoBinary = checkBinary(binary)

        self.user_defined_edges = ["ni", "ei", "si", "wi"]
        self.params = [ 
             "-c", "test.sumocfg", 
             "-W", "true"
        ]
        
        if sumoBinary == 'sumo-gui':
            self.params.append("--start")

        traci.start([sumoBinary, *self.params])

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
            for i, val in enumerate(arr):
                arr[i] = val / total
        return arr
    
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

    def get_n_actions(self):
        return len(self.actions)
    
    def get_action_space(self):
        return self.actions
    
    def sample_action_space(self):
        return random.randint(0,self.get_n_actions() - 1)
    
    def get_state(self):
        state = []
        state.extend(self.normalize_array(self.get_queue_lengths()))
        state.extend(self.normalize_array(self.red_timings))
        state.extend(self.normalize_array(self.get_waiting_times()))
        state.extend(self.get_pedestrian_wait_times())
        # state.extend(self.get_phases_array())

        return state
    
    # def get_pedestrian_wait_times(self):
    #     waiting_times = []
    #     for i in range(0,4):
    #         waiting_times.append(traci.lane.getWaitingTime(f":0_w{i}_0"))
       
    #     print("ret :", waiting_times)
    #     return waiting_times

    def get_pedestrian_wait_times(self):
        crossings = {':0_c0', ':0_c1', ':0_c2', ':0_c3'}
        pedestrian_flags = []
        pedestrians = traci.person.getIDList()
        for crossing in crossings:
            pedestrian_flag = False
            for ped_id in pedestrians:
                if (traci.person.getWaitingTime(ped_id) > 0) and (traci.person.getNextEdge(ped_id) == crossing):
                     pedestrian_flag = True
                     break
            pedestrian_flags.append(pedestrian_flag)

        return pedestrian_flags
    
    def get_phases_array(self):
        phases_array = [0] * self.get_n_actions()
        phases_array[self.prev_action] = 1
        return phases_array
    
    def run_phase(self, phase):
        yellow_phase = phase * 2
        init_vehicles = set(traci.vehicle.getIDList())
        init_ped = set(traci.person.getIDList())

        initial_wait = self.get_total_waiting_time(init_vehicles)
        initial_ped_wait = self.get_total_pedestrian_waiting_time(init_ped)
        
        if phase != self.prev_action:
            # End previous phase
            traci.trafficlight.setPhase("0", self.prev_action*2)
            for _ in range(YELLOW_TIME):
                self.step_count += 1
                traci.simulationStep()

            # Initial yellow phase
            traci.trafficlight.setPhase("0", yellow_phase)
            for _ in range(YELLOW_TIME):
                self.step_count += 1
                traci.simulationStep()

        # Green phase
        traci.trafficlight.setPhase("0", yellow_phase+1)
        for _ in range(GREEN_TIME):
            self.step_count += 1
            traci.simulationStep()

        self.prev_action = phase
        self.set_red_timings((YELLOW_TIME * 2) + GREEN_TIME)
        
        done = len(traci.simulation.getCollisions()) > 0 or traci.simulation.getMinExpectedNumber() == 0
        rem_vehicles = set(traci.vehicle.getIDList()).intersection(init_vehicles)
        rem_ped = set(traci.person.getIDList()).intersection(init_ped)

        remaining_wait = self.get_total_waiting_time(rem_vehicles)
        remaining_ped_wait = self.get_total_pedestrian_waiting_time(rem_ped)

        reward = -((remaining_wait - initial_wait) + (remaining_ped_wait - initial_ped_wait))

    
        return self.get_state(), reward, done, (self.step_count > 12500), self.step_count

    def get_total_waiting_time(self, vehicles):
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
        if len(pedestrians) > 90:
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
        traci.load(self.params)
        return self.get_state(), None