import pytest
from trafficLightController import TrafficLightController

class TestTrafficLightController:
    @pytest.fixture
    def controller(self):
        # Create a controller with standard timing settings
        return TrafficLightController(yellow_time=5, green_time=15)
    
    # Test controller initialisation
    def test_initialization(self, controller):
        assert controller.YELLOW_TIME == 5
        assert controller.GREEN_TIME == 15
    
     # Test conversion from base-3 to decimal
    def test_base3_to_decimal(self, controller):
        assert controller.base3_to_decimal([0, 0, 0]) == 0
        assert controller.base3_to_decimal([1, 0, 0]) == 9
        assert controller.base3_to_decimal([1, 1, 0]) == 12
        assert controller.base3_to_decimal([2, 1, 0]) == 21
        assert controller.base3_to_decimal([1, 2, 2]) == 17
    
    # Test conversion from decimal to base-3
    def test_decimal_to_base3(self, controller):
        assert controller.decimal_to_base3(0) == [0] * 20
        assert controller.decimal_to_base3(9, length=3) == [1, 0, 0]
        assert controller.decimal_to_base3(21, length=3) == [2, 1, 0]
        assert controller.decimal_to_base3(17, length=3) == [1, 2, 2]

        # Test padding
        assert controller.decimal_to_base3(17, length=5) == [0, 0, 1, 2, 2]
    
    # Test calculation of intermediary phase for ending current phase
    def test_end_current_phase(self, controller):
        # Test maintaining a green light between phases
        current_phase = controller.base3_to_decimal([2, 0, 0])
        next_phase = controller.base3_to_decimal([2, 2, 0])
        expected = controller.base3_to_decimal([2, 0, 0])
        assert controller.end_current_phase(current_phase, next_phase) == expected
        
        # Test switching to yellow inbetween a green and red signal
        current_phase = controller.base3_to_decimal([2, 0, 0])
        next_phase = controller.base3_to_decimal([0, 0, 0])
        expected = controller.base3_to_decimal([1, 0, 0])
        assert controller.end_current_phase(current_phase, next_phase) == expected
    
    # Test calculation of intermediary phase for starting next phase
    def test_start_new_phase(self, controller):
        # Test maintaining a green light between phsaes
        end_phase = controller.base3_to_decimal([2, 0, 0])
        next_phase = controller.base3_to_decimal([2, 0, 0])
        expected = controller.base3_to_decimal([2, 0, 0])
        assert controller.start_new_phase(end_phase, next_phase) == expected
        
        # Test transitioning from yellow to green
        end_phase = controller.base3_to_decimal([1, 0, 0])
        next_phase = controller.base3_to_decimal([2, 0, 0])
        expected = controller.base3_to_decimal([2, 0, 0])
        assert controller.start_new_phase(end_phase, next_phase) == expected
        
        # Test transitioning from red to green
        end_phase = controller.base3_to_decimal([0, 0, 0])
        next_phase = controller.base3_to_decimal([2, 2, 2])
        expected = controller.base3_to_decimal([1, 1, 1])
        assert controller.start_new_phase(end_phase, next_phase) == expected
    
    # Test fetching the SUMO idx to end a phase
    def test_get_idx_to_end_phase(self, controller):
        # Sample model action values
        current_phase = 0
        next_phase = 1
        
        # Calculate expected value
        current_denary = controller.all_green_phases_dict[current_phase]
        next_denary = controller.all_green_phases_dict[next_phase]
        end_phase_denary = controller.end_current_phase(current_denary, next_denary)
        expected_idx = controller.phases_indices_dict[end_phase_denary]

        assert controller.get_idx_to_end_phase(current_phase, next_phase) == expected_idx
    
    # Test fetching the SUMO idx to start a phase
    def test_get_idx_to_start_phase(self, controller):
        # Sample model action values
        current_phase = 0
        next_phase = 1
        
        # Calculate expected result
        current_denary = controller.all_green_phases_dict[current_phase]
        next_denary = controller.all_green_phases_dict[next_phase]
        end_phase_denary = controller.end_current_phase(current_denary, next_denary)
        start_phase_denary = controller.start_new_phase(end_phase_denary, next_denary)
        expected_idx = controller.phases_indices_dict[start_phase_denary]
        
        assert controller.get_idx_to_start_phase(current_phase, next_phase) == expected_idx
    
    # Test fetching the SUMO idx for a given model action
    def test_get_idx_of_green_phase(self, controller):
        phase = 5
        denary_val = controller.all_green_phases_dict[phase]
        expected_idx = controller.phases_indices_dict[denary_val]
        assert controller.get_idx_of_green_phase(phase) == expected_idx
    
    # Test converting a base 3 representation of a phase to a green light boolean array
    def test_get_array_of_green_lights(self, controller):
        # Convert sample model action to base3
        phase = 3
        denary_val = controller.all_green_phases_dict[phase]
        base3_repr = controller.decimal_to_base3(denary_val)
        
       # Calculated expected result
        expected = []
        for idx, val in enumerate(base3_repr):
            if val == 2:
                expected.append(1)
            else:
                expected.append(0)

        assert controller.get_array_of_green_lights(phase) == expected