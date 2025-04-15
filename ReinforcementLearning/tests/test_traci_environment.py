import pytest
import random
from unittest.mock import MagicMock, patch, call

# Import the modules to be mocked
import traci
from sumolib import checkBinary

from ..utilities import normalize_array
from ..traciEnvironment import TraciEnvironment


class TestTraciEnvironment:
    @pytest.fixture(autouse=True)
    def setup_traci_mocks(self, monkeypatch):
        # Mock all traci functions called within the traciEnvironment class
        monkeypatch.setattr(traci, "start", lambda args: None)
        monkeypatch.setattr(traci, "load", lambda params: None)

        trafficlight_mock = MagicMock()
        monkeypatch.setattr(traci, "trafficlight", trafficlight_mock)

        vehicle_mock = MagicMock()
        monkeypatch.setattr(traci, "vehicle", vehicle_mock)

        person_mock = MagicMock()
        monkeypatch.setattr(traci, "person", person_mock)

        lane_mock = MagicMock()
        monkeypatch.setattr(traci, "lane", lane_mock)

        simulation_mock = MagicMock()
        monkeypatch.setattr(traci, "simulation", simulation_mock)
        
        # Set default return values for actor fetching methods
        traci.vehicle.getIDList.return_value = []
        traci.person.getIDList.return_value = []
        
        # Return dict of mocks for further customization
        return {
            "trafficlight": trafficlight_mock,
            "vehicle": vehicle_mock,
            "person": person_mock,
            "lane": lane_mock,
            "simulation": simulation_mock
        }

    # Mock env dependencies
    @pytest.fixture
    def mock_route_generator(self):
        mock = MagicMock()
        mock.generate_routes.return_value = (2, None)
        return mock

    @pytest.fixture
    def mock_light_controller(self):
        mock = MagicMock()
        mock.get_array_of_green_lights.return_value = [False, True, False, False]

        return mock

    @pytest.fixture
    def env(self, mock_route_generator, mock_light_controller, monkeypatch):
        # Set params but don't start traci
        def mock_start_traci(self, binary):
            self.sumoBinary = binary
            self.params = [ 
                "-c", "sumo_files/test.sumocfg", 
                "-W", "true",
                "--lateral-resolution", "0.2"
            ]
        
        # Mock the start traci method
        monkeypatch.setattr(TraciEnvironment, "start_traci", mock_start_traci)
        
        actions = {i for i in range(0,4)}

        # Create environment with mock dependencies
        env = TraciEnvironment(
            show_gui=True,
            actions=actions,
            route_generator=mock_route_generator,
            light_controller=mock_light_controller,
            training=False
        )
        
        # Initialize attributes that would normally be set in reset_simulation
        env.current_phase = 0
        env.red_timings = [0] * 4
        env.crossing_active_timings = [0, 0, 0, 0]
        env.step_count = 0
        env.emv_ids = {"emv_0", "emv_1"}
        
        if not env.training:
            env.pedestrian_wait_times = {}
            env.emv_wait_times = {}
            env.veh_wait_times = {}
            
        return env

    # Test resetting simulation parameters and it's return values
    def test_reset_simulation(self, env, monkeypatch):
        # Mock get_state
        monkeypatch.setattr(env, "get_state", lambda: [0, 1, 2, 3])

        # Assert state is returned correctly
        state, _ = env.reset_simulation()
        assert state == [0, 1, 2, 3]
        
        # Assert initialization of attributes
        assert env.current_phase == 0
        assert env.red_timings == [0, 0, 0, 0]
        assert env.crossing_active_timings == [0, 0, 0, 0]
        assert env.step_count == 0
        assert env.emv_ids == {"emv_0", "emv_1"}
        
        # Verify metrics dictionaries are initialized if training is False
        if not env.training:
            assert isinstance(env.pedestrian_wait_times, dict)
            assert isinstance(env.emv_wait_times, dict)
            assert isinstance(env.veh_wait_times, dict)

    # Test queue lengths aspect of state
    def test_get_queue_lengths(self, env, setup_traci_mocks):
        # Mock getLastStepVehicleNumber to always return 1
        lane_mock = setup_traci_mocks["lane"]
        lane_mock.getLastStepVehicleNumber.return_value = 1

        # Verify it returns a list of 12 ones
        assert env.get_queue_lengths() == [1] * 12

    # Test EMV distances aspect of state
    def test_get_emv_distances(self, env, setup_traci_mocks):
        vehicle_mock = setup_traci_mocks["vehicle"]
        
        # Setup mock return values
        vehicle_ids = ["emv1", "emv2", "emv3", "emv4"]
        route_ids = {"emv1": "n2c", "emv2": "e2c", "emv3": "s2c", "emv4": "w2c"}
        
        vehicle_mock.getIDList.return_value = vehicle_ids
        vehicle_mock.getLaneIndex.return_value = 1  # so it's != 0
        vehicle_mock.getLanePosition.return_value = 50  # fixed position
        vehicle_mock.getRouteID.side_effect = lambda vid: route_ids[vid]

        # Mock get_emvs_in_sim to return all 4 EMVs
        env.get_emvs_in_sim = MagicMock(return_value=vehicle_ids)

        # Call the function
        distances = env.get_emv_distances()

        # Expected: [0.1, 0.1, 0.1, 0.1] for ['n', 'e', 's', 'w']
        assert distances == [0.1, 0.1, 0.1, 0.1]

    # Test that get_n_actions returns the correct number of actions
    def test_get_n_actions(self, env):
        assert env.get_n_actions() == 4

    # Test that get_action_space returns the actions list
    def test_get_action_space(self, env):
        assert env.get_action_space() == {0, 1, 2, 3}

    # Test the sample_action_space method
    def test_sample_action_space(self, env, monkeypatch):
        monkeypatch.setattr(random, "randint", lambda a, b: 2)
        assert env.sample_action_space() == 2

    # Test collating and normalizing state information
    def test_get_state(self, env, monkeypatch):
        # Mock necessary state methods
        queue_state = [3, 2, 1, 5, 4, 3, 2, 1, 0, 4, 3, 2]
        phases_state = [False, True, False, False]
        emv_state = [0.5, 0.6, 0, 0]
        pedestrian_state = [2, 0, 1, 0]

        monkeypatch.setattr(env, "get_queue_lengths", lambda: queue_state)
        monkeypatch.setattr(env, "get_phases_array", lambda: phases_state)
        monkeypatch.setattr(env, "get_emv_distances", lambda: emv_state)
        monkeypatch.setattr(env, "get_pedestrian_wait_times", lambda ids: pedestrian_state)
        
        state = env.get_state()
        
        # Generate expected result
        expected_state = [
            *normalize_array(queue_state),
            *phases_state,
            *normalize_array(emv_state),
            *normalize_array(pedestrian_state)
        ]

        assert state == expected_state

    # Test incrementing of crossings over phases
    def test_get_pedestrian_wait_times(self, env, setup_traci_mocks):
        person_mock = setup_traci_mocks["person"]
        
        env.crossing_ids = ["c1", "c2", "c3", "c4"]
        env.crossing_active_timings = [1, 1, 1, 1]

        # Simulate pedestrians
        pedestrian_ids = ["p1", "p2", "p3", "p4"]
        next_edges = {"p1": "c1", "p2": "c2", "p3": "c3", "p4": "c4"}
        person_mock.getWaitingTime.return_value = 10
        person_mock.getNextEdge.side_effect = lambda pid: next_edges[pid]

        new_timings = env.get_pedestrian_wait_times(pedestrian_ids)

        assert new_timings == [2, 2, 2, 2]   

    def test_get_phases_array(self, env):
        expected = [False, True, False, False]
        assert env.get_phases_array() == expected

    # Test get actors in sim correctly seperates a list of actors into 3 groups
    def test_get_actors_in_sim(self, env, setup_traci_mocks):
        # Mock setup
        vehicle_mock = setup_traci_mocks["vehicle"]
        person_mock = setup_traci_mocks["person"]
        vehicle_mock.getIDList.return_value = ["car_1", "emv_0", "car_2", "emv_1"]
        person_mock.getIDList.return_value = ["ped_1", "ped_2"]
        
        vehicles, emvs, peds = env.get_actors_in_sim()
        
        assert vehicles == {"car_1", "car_2"}
        assert emvs == {"emv_0", "emv_1"}
        assert peds == ["ped_1", "ped_2"]

    # Test correct calculation of collision penalty
    def test_calculate_collision_penalty(self, env, setup_traci_mocks):
        simulation_mock = setup_traci_mocks["simulation"]
        
        # Test with no collisions
        simulation_mock.getCollisions.return_value = []
        penalty = env.calculate_collision_penalty()
        assert penalty == 0
        
        # Test with collisions
        simulation_mock.getCollisions.return_value = [1]
        penalty = env.calculate_collision_penalty()
        assert penalty == 300

    # Test environment correctly seperates emvs from a list of vehicle IDs
    def test_get_emvs_in_sim(self, env):
        current_vehicles = {"car_1", "emv_0", "car_2", "emv_1"}

        assert env.get_emvs_in_sim(current_vehicles) == {"emv_0", "emv_1"}

    # Test environment correctly calculates average waiting time
    def test_get_total_waiting_time(self, env, setup_traci_mocks):
        # Set up mock
        vehicle_mock = setup_traci_mocks["vehicle"]
        vehicle_mock.getWaitingTime.return_value = 10

        # Test with vehicles
        wait_time = env.get_total_waiting_time({"veh_1", "veh_2"})
        assert wait_time == 10
        
        # Test with no vehicles
        wait_time = env.get_total_waiting_time(set())
        assert wait_time == 0

    # Test environment correctly calculates average pedestrian waiting time
    def test_get_total_pedestrian_waiting_time(self, env, setup_traci_mocks):
        # Set up mock
        person_mock = setup_traci_mocks["person"]
        person_mock.getWaitingTime.return_value = 10
        
        # Test with pedestrians
        wait_time = env.get_total_pedestrian_waiting_time({"ped_1", "ped_2"})
        assert wait_time == 10
        
        # Test with no pedestrians
        wait_time = env.get_total_pedestrian_waiting_time([])
        assert wait_time == 0

    def test_get_metrics(self, env):
        # Setup dictionaries
        env.veh_wait_times = {"car_1": 10, "car_2": 20}
        env.emv_wait_times = {"emv_0": 5, "emv_1": 5}
        env.pedestrian_wait_times = {"ped_1": 15, "ped_2": 25}
        
        # Test get_metrics
        veh_avg, emv_avg, ped_avg = env.get_metrics()
        
        # Verify averages
        assert veh_avg == 15
        assert emv_avg == 5
        assert ped_avg == 20

    # Test update pedestrian wait times correctly takes the maximum available value
    def test_update_pedestrian_wait_times(self, env, setup_traci_mocks):
        # Setup with one actor already logged
        env.pedestrian_wait_times = {"ped_0": 8}
        
        # Set up person mock with lower wait time
        person_mock = setup_traci_mocks["person"]
        person_mock.getIDList.return_value = {"ped_0", "ped_1"}
        person_mock.getWaitingTime.return_value = 5
        
        env.update_pedestrian_wait_times()
        assert env.pedestrian_wait_times == {"ped_0": 8, "ped_1": 5}

    # Test update emv wait times correctly takes the maximum available value
    def test_update_emv_wait_times(self, env, setup_traci_mocks):
        # Setup with one actor already logged
        env.emv_wait_times = {"emv_0": 8}
        
        # Set up vehicle mock with lower wait time
        vehicle_mock = setup_traci_mocks["vehicle"]
        vehicle_mock.getIDList.return_value = ["emv_0", "emv_1"]
        vehicle_mock.getWaitingTime.return_value = 5
        
        env.update_emv_wait_times()
        assert env.emv_wait_times == {"emv_0": 8, "emv_1": 5}

    # Test update vehicle wait times correctly takes the maximum available value
    def test_update_vehicle_wait_times(self, env, setup_traci_mocks):
        # Setup with one actor already logged
        env.veh_wait_times = {"car_1": 8}
        
        # Set up vehicle mock with lower wait time
        vehicle_mock = setup_traci_mocks["vehicle"]
        vehicle_mock.getIDList.return_value = ["car_1", "car_2"]
        vehicle_mock.getWaitingTime.return_value = 5
        
        env.update_vehicle_wait_times()
        assert env.veh_wait_times == {"car_1": 8, "car_2": 5}