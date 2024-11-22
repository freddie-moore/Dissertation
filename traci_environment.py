# import libsumo as traci
import traci
from sumolib import checkBinary
import random

GREEN_TIME = 30
YELLOW_TIME = 6

class TraciEnvironment:
    def __init__(self, binary, actions):
        self.step_count = 0
        self.prev_action = 0
        self.actions = actions
        sumoBinary = checkBinary(binary)

        self.user_defined_edges = ["ni", "ei", "si", "wi"]
        traci.start([sumoBinary, "-c", "test.sumocfg",
             "--tripinfo-output", "tripinfo.xml"])

    def get_queue_lengths_by_edge(self, edge_id):
        waiting_times = [0] * 4
        for i in range(0,4):
            waiting_times[i] = traci.lane.getLastStepVehicleNumber(f"{edge_id}_{i}")
        return waiting_times
    
    def get_queue_lengths(self):
        queues_length = []
        for edge_id in self.user_defined_edges:
            queues_length.extend(self.get_queue_lengths_by_edge(edge_id))
        return queues_length

    # def get_queue_lengths(self):
    #     queues_length = [0] * self.get_n_actions()
    #     for i, edge_id in enumerate(self.user_defined_edges):
    #         queue_length = traci.edge.getLastStepVehicleNumber(edge_id)
    #         queues_length[i] = queue_length
    #     return queues_length
    
    def normalize_array(self, arr):
        total = sum(arr)
        if total != 0:
            for i, val in enumerate(arr):
                arr[i] = val / total
        return arr
    
    
    # def get_waiting_times_by_edge(self, edge_id):
        # waiting_times = [0] * self.get_n
        # for i in range(0,4):
        #     waiting_times[i] = traci.lane.getLastStepVehicleNumber(f"{edge_id}_{i}")
        # return waiting_times
    
    def get_waiting_times(self):
        waiting_times = [0] * self.get_n_actions()
        for i, edge_id in enumerate(self.user_defined_edges):
            waiting_time = traci.edge.getWaitingTime(edge_id)
            waiting_times[i] = waiting_time
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
        # state.extend(self.normalize_array(self.get_waiting_times()))
        # state.extend(self.get_phases_array())
        print("State", state)
        return state
    
    def get_phases_array(self):
        phases_array = [0] * self.get_n_actions()
        phases_array[self.prev_action] = 1
        return phases_array
    
    def run_phase(self, phase):
        yellow_phase = phase * 2
        init_vehicles = set(traci.vehicle.getIDList())
        initial_wait = self.get_total_waiting_time(init_vehicles)
        
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
        done = len(traci.simulation.getCollisions()) > 0 or traci.simulation.getMinExpectedNumber() == 0
        rem_vehicles = set(traci.vehicle.getIDList()).intersection(init_vehicles)
        remaining_wait = self.get_total_waiting_time(rem_vehicles)
        reward = -(remaining_wait - initial_wait)

    
        return self.get_state(), reward, done, (self.step_count > 10000), self.step_count

    def get_total_waiting_time(self, vehicles):
        wait  = 0
        for vehicle_id in vehicles:
            wait += traci.vehicle.getWaitingTime(vehicle_id)
        if len(vehicles) > 0:
            wait = wait / len(vehicles)
        else:
            wait = 0
        
        return wait
        
    def reset(self):
        self.step_count = 0
        traci.load(["-c", "test.sumocfg"])
        
        return self.get_state(), None