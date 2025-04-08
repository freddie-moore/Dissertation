import torch
from model import DQN

# This class is a simple fixed time controller that will alternate between phases in a cyclical structure
class FixedTimeController():
    def __init__(self, env):
        self.traci_env = env
        self.num_phases = self.traci_env.get_n_actions()
        self.i = 0

    def get_phase(self, state):
        self.i += 1
        return self.i % self.num_phases
        

# This class is a reinforcement learning based controller that will select the best next phase according to a learned policy
class RLController():
    def __init__(self, env, model_path):
        # Set device
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else
            "mps" if torch.backends.mps.is_available() else
            "cpu"
        )

        self.traci_env = env

        # Create the model and load weights
        state, info = self.traci_env.reset_simulation()
        n_actions = self.traci_env.get_n_actions()
        n_observations = len(state)
        self.model = DQN(n_observations, n_actions).to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()


    def get_phase(self, state):
        # Convert the state to a tensor if it's not already
        if not isinstance(state, torch.Tensor):
            state = torch.tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)

        # Infer the action
        with torch.no_grad():
            action = self.model(state).max(1).indices.item()  # Get the index of the highest Q-value

        return action