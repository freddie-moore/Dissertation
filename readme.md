# Dissertation Traffic Signal Control

This repository contains the implementation of traffic signal control models for a dissertation project. It includes a Reinforcement Learning (RL) model using Deep Q-Networks (DQN) and a Linear Dynamic Optimization (LDO) model using a rolling horizon approach. The RL model is implemented in the `ReinforcementLearning` directory, while the LDO model is in the `LinearOptimization` directory. The project uses Python and relies on the SUMO (Simulation of Urban MObility) environment for traffic simulations.

## Repository Structure

- **ReinforcementLearning/**: Contains the RL model implementation, including training, validation, and testing scripts.
  - `trainingLoop.py`: Script to train the DQN model.
  - `runner.py`: Script to run the trained model on validation data.
  - `model.py`, `Controllers.py`, `traciEnvironment.py` etc.: Supporting modules for the RL environment and logic.
  - `sumo_files/`: SUMO configuration files.
  - `final_models/`: Directory for storing trained models.
- **LinearOptimization/**: Contains the LDO model implementation.
  - `RollingHorizon.py`: Script to run the rolling horizon optimization model.
  - `model.mod`, `data.dat`: Optimization model and data files.
- **Tests/**: Pytest files (`test_traci_environment.py`, `test_traffic_light_controller.py`, `test_utilities.py`) for validating the RL components.

## Installation

1. **Set up a virtual environment**:
```bash
python -m venv venv
venv\Scripts\activate
```

2. **Install requirements**:
```bash
pip install -r requirements.txt
```

3. **Install SUMO**:
    The RL model requires SUMO. Install it following the official [Sumo Documentation](https://sumo.dlr.de/docs/Installing.html).

## Training the Model

To train the DQN model, use the `trainingLoop.py` script in the ReinforcementLearning directory. The script accepts several parameters for configuring the environment and DQN hyperparameters.

```bash
cd ReinforcementLearning
python trainingLoop.py --num-cars 100
```


Further parameters are available and can be discovered by running:
```bash
python .\trainingLoop.py --help
```

## Model Evaluation

### RL Model Evaluation
To evaluate the trained RL model on validation data, use the runner.py script in the ReinforcementLearning directory:

```bash
cd ReinforcementLearning
python runner.py --controller rl --num-cars 100 --gui True
```

Further parameters are available and can be discovered by running:
```bash
python .\runner.py --help
```

### LDO Model Comparison

To run the Linear Dynamic Optimization model, use the RollingHorizon.py script in the LinearOptimization directory. This script automatically loads the data used in the last run of runner.py and requires no additional parameters.

```bash
cd LinearOptimization
python RollingHorizon.py
```

## Running Tests

The repository includes pytest tests to validate the RL components. Tests are located in the ReinforcementLearning directory.

To run all tests:
```bash
cd ReinforcementLearning
pytest .\tests\
```

### Test Files
- `test_traci_environment.py`: Tests for the SUMO environment integration.
- `test_traffic_light_controller.py`: Tests for the traffic light controller logic.
- `test_utilities.py`: Tests for utility functions.
Ensure all dependencies are installed and SUMO is configured before running tests.
