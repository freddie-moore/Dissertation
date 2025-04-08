from all_phases_base3 import all_phases_base3
import traci

YELLOW_TIME = 5
GREEN_TIME = 15

def run_tls_phase(current_phase, new_phase, step_count):
    end_phase_idx = get_idx_to_end_phase(current_phase, new_phase)
    traci.trafficlight.setPhase("0", end_phase_idx)
    step_count += YELLOW_TIME
    traci.simulationStep(step_count)

    start_phase_idx = get_idx_to_start_phase(current_phase, new_phase)
    traci.trafficlight.setPhase("0", start_phase_idx)
    step_count += YELLOW_TIME
    traci.simulationStep(step_count)

    green_phase_idx = get_idx_of_green_phase(new_phase)
    traci.trafficlight.setPhase("0", green_phase_idx)
    step_count += GREEN_TIME
    traci.simulationStep(step_count)

    return step_count

def base3_to_decimal(phase):
    """
    Converts a base-3 phase (list of 16 bits) to its decimal equivalent.

    Parameters:
    - phase (list): 16-bit list representing a phase in base-3.

    Returns:
    - int: The decimal equivalent of the base-3 phase.
    """
    decimal_value = 0
    for index, digit in enumerate(reversed(phase)):
        decimal_value += digit * (3 ** index)
    return decimal_value

def decimal_to_base3(number, length=20):
    """
    Converts a decimal number to its base-3 representation with a fixed length.

    Parameters:
    - number (int): Decimal number to be converted.
    - length (int): Desired length of the base-3 representation (default is 16).

    Returns:
    - list: Base-3 representation as a list of digits.
    """
    base3_digits = []
    while number > 0:
        base3_digits.append(number % 3)
        number //= 3
    
    # Ensure the representation has the correct length
    while len(base3_digits) < length:
        base3_digits.append(0)

    return list(reversed(base3_digits))


def sort_phases(yellow_phases):
    """
    Sorts yellow phases based on their base-3 denary values.

    Parameters:
    - yellow_phases (set): Set of unique yellow phases (tuples).

    Returns:
    - list: Sorted list of yellow phases.
    """
    return sorted(yellow_phases, key=base3_to_decimal)


all_phases = sort_phases(all_phases_base3)

phases_indices_dict = {}
all_green_phases_dict = {}
count = 0
for idx, phase in enumerate(all_phases):
    denary = base3_to_decimal(phase)
    if 1 not in phase:
            all_green_phases_dict[count] = denary
            count += 1
    phases_indices_dict[denary] = idx


# for key, value in all_green_phases_dict.items():
#     print(phases_indices_dict[value])


def end_current_phase(cur_phase_denary, next_phase_denary):
    cur_phase = decimal_to_base3(cur_phase_denary)
    next_phase = decimal_to_base3(next_phase_denary)

    ret = []
    for bit1, bit2 in zip(cur_phase, next_phase):
        if bit1 == 2 and bit2 == 2:
            ret.append(2)
        elif bit1 == 2 and bit2 == 0:
            ret.append(1)
        elif bit1 == 1 or bit2 == 1:
            print("CRITICAL 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0ERROR IN END_CURRENT_PHASE")
        else:
            ret.append(0)
        
    return base3_to_decimal(ret)

def start_new_phase(cur_phase_denary, next_phase_denary):
    cur_phase = decimal_to_base3(cur_phase_denary)
    next_phase = decimal_to_base3(next_phase_denary)

    ret = []
    for bit1, bit2 in zip(cur_phase, next_phase):
        if bit1 == 2 and bit2 == 2:
            ret.append(2)
        elif bit1 == 2 and bit2 == 0:
            ret.append(-1)
        elif bit1 == 1 and bit2 == 2:
            ret.append(2)
        elif bit1 == 0 and bit2 == 2:
            ret.append(1)
        else:
            ret.append(0)
        
    return base3_to_decimal(ret)



for phase in all_phases:
    state_string = ""
    for c in phase:
        if c == 2:
            state_string += "g"
        elif c == 1:
            state_string += "y"
        elif c == 0:
            state_string += "r"

# with open('tls.add.xml', 'w') as file:
#         file.write('<tlLogic id="0" type="static" programID="0" offset="0">\n')

#         for phase in all_phases:
#             state_string = ""
#             for c in phase:
#                 if c == 2:
#                     state_string += "g"
#                 elif c == 1:
#                     state_string += "y"
#                 elif c == 0:
#                     state_string += "r"

#             file.write(f'    <phase duration="100" state="{state_string}"/>\n')
#         file.write('</tlLogic>\n')

# phase1 = [2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0]
# phase2 = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0]

# phase1_denary = base3_to_decimal(phase1)
# phase2_denary = base3_to_decimal(phase2)

# transition_denary = end_current_phase(phase1_denary, phase2_denary)
# transition_base3 = decimal_to_base3(transition_denary)


# new_phase_denary = start_new_phase(transition_denary, phase2_denary)
# new_phase_base3 = decimal_to_base3(new_phase_denary)

# print(phase1)
# print(transition_base3)
# print(new_phase_base3)
# print(phase2)

def get_idx_to_end_phase(cur_phase, next_phase):
    phase1_denary = all_green_phases_dict[cur_phase]
    phase2_denary = all_green_phases_dict[next_phase]
    # print(f"A Phase 1 Denary {phase1_denary} ")
    # print(f"A Phase 2 Denary {phase2_denary} ")
    end_phase_denary = end_current_phase(phase1_denary, phase2_denary)
    end_phase_base3 = decimal_to_base3(end_phase_denary)

    return phases_indices_dict[end_phase_denary]

def get_idx_to_start_phase(cur_phase, next_phase):
    phase1_denary = all_green_phases_dict[cur_phase]
    phase2_denary = all_green_phases_dict[next_phase]
    # print(f"A Phase 1 Denary {phase1_denary} ")
    # print(f"A Phase 2 Denary {phase2_denary} ")
    end_phase_denary = end_current_phase(phase1_denary, phase2_denary)
    end_phase_base3 = decimal_to_base3(end_phase_denary)
    # print(end_phase_base3)
    start_phase_denary = start_new_phase(end_phase_denary, phase2_denary)
    start_phase_base3 = decimal_to_base3(start_phase_denary)

    return phases_indices_dict[start_phase_denary]

def get_idx_of_green_phase(next_phase):
    return phases_indices_dict[all_green_phases_dict[next_phase]]

def get_array_of_green_lights(phase, print_ret=False):
    repr = decimal_to_base3(all_green_phases_dict[phase])
    for idx, val in enumerate(repr):
        if val == 2:
            repr[idx] = 1

    if print_ret:
        print("ret :", repr)
    return repr
    