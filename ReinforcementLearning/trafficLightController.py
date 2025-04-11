import traci
import pickle

denary_to_sumo_idx_mapping={40: 0, 41: 1, 43: 2, 44: 3, 49: 4, 50: 5, 52: 6, 67: 7, 68: 8, 70: 9, 76: 10, 80: 11, 28467: 12, 28476: 13, 28494: 14, 28503: 15, 30654: 16, 30663: 17, 30681: 18, 56898: 19, 56907: 20, 56925: 21, 56934: 22, 87489: 23, 87498: 24, 89676: 25, 89685: 26, 115920: 27, 115929: 28, 146538: 29, 146547: 30, 174969: 31, 174978: 32, 205605: 33, 205632: 34, 207792: 35, 207819: 36, 234036: 37, 234063: 38, 264627: 39, 266814: 40, 293058: 41, 323676: 42, 352107: 43, 382752: 44, 382779: 45, 384939: 46, 384966: 47, 411183: 48, 411210: 49, 441774: 50, 443961: 51, 470205: 52, 500823: 53, 529254: 54, 2302939: 55, 2302940: 56, 2302966: 57, 2302967: 58, 2480086: 59, 2480087: 60, 2480113: 61, 4605850: 62, 4605851: 63, 4605877: 64, 4605878: 65, 4783728: 66, 4783731: 67, 4783755: 68, 4783758: 69, 4784457: 70, 4784460: 71, 4785912: 72, 4785939: 73, 4786641: 74, 4788099: 75, 4788126: 76, 4788828: 77, 4962330: 78, 4962357: 79, 4964517: 80, 4964544: 81, 5139477: 82, 5139504: 83, 5141664: 84, 5141691: 85, 7085907: 86, 7085934: 87, 7263054: 88, 7263081: 89, 9388818: 90, 9388845: 91, 9566697: 92, 9566724: 93, 9567426: 94, 9567429: 95, 9567453: 96, 9567456: 97, 9568881: 98, 9568908: 99, 9569610: 100, 9569637: 101, 9571068: 102, 9571095: 103, 9571797: 104, 9571824: 105, 9745299: 106, 9745326: 107, 9747486: 108, 9747513: 109, 9922446: 110, 9922473: 111, 9924633: 112, 9924660: 113, 11868876: 114, 11868903: 115, 12046023: 116, 12046050: 117, 14171787: 118, 14171814: 119, 14554485: 120, 14556672: 121, 14582916: 122, 14731632: 123, 14733819: 124, 14760063: 125, 16651819: 126, 16651820: 127, 16828966: 128, 16828967: 129, 18954730: 130, 18954731: 131, 19132608: 132, 19132611: 133, 19133337: 134, 19133340: 135, 19134792: 136, 19135521: 137, 19136979: 138, 19137708: 139, 19311210: 140, 19313397: 141, 19488357: 142, 19490544: 143, 21434787: 144, 21611934: 145, 23737698: 146, 23915577: 147, 23916306: 148, 23916309: 149, 23917761: 150, 23918490: 151, 23919948: 152, 23920677: 153, 24094179: 154, 24096366: 155, 24271326: 156, 24273513: 157, 26217756: 158, 26394903: 159, 28520667: 160, 28903392: 161, 28905579: 162, 28931823: 163, 29080539: 164, 29082726: 165, 29108970: 166, 31000726: 167, 31000727: 168, 31177873: 169, 31177874: 170, 33303637: 171, 33303638: 172, 33481515: 173, 33481518: 174, 33482244: 175, 33482247: 176, 33483699: 177, 33484428: 178, 33485886: 179, 33486615: 180, 33660117: 181, 33662304: 182, 33837264: 183, 33839451: 184, 35783694: 185, 35960841: 186, 38086605: 187, 38264484: 188, 38265213: 189, 38265216: 190, 38266668: 191, 38267397: 192, 38268855: 193, 38269584: 194, 38443086: 195, 38445273: 196, 38620233: 197, 38622420: 198, 40566663: 199, 40743810: 200, 42869574: 201, 186535795: 202, 186535796: 203, 186535798: 204, 186535799: 205, 186564222: 206, 186566409: 207, 186592653: 208, 200884702: 209, 200884703: 210, 200884705: 211, 200913129: 212, 200915316: 213, 200941560: 214, 373071586: 215, 373071587: 216, 373071589: 217, 373071590: 218, 373100013: 219, 373102200: 220, 373128444: 221, 387479548: 222, 387479549: 223, 387479557: 224, 387479558: 225, 387538597: 226, 387538606: 227, 387656686: 228, 387656687: 229, 387715735: 230, 387833833: 231, 387833834: 232, 387892882: 233, 401946544: 234, 401946545: 235, 402123691: 236, 402123692: 237, 416295451: 238, 416295452: 239, 416472598: 240, 416472599: 241, 573956281: 242, 573956282: 243, 588305188: 244, 588305189: 245, 760492072: 246, 760492073: 247, 774900037: 248, 774900038: 249, 774959087: 250, 774959096: 251, 775077175: 252, 775077176: 253, 775136225: 254, 775254322: 255, 775254323: 256, 775313372: 257, 789367034: 258, 789544181: 259, 803715940: 260, 803715941: 261, 803893087: 262, 803893088: 263, 961376771: 264, 975725677: 265, 975725678: 266, 1147912561: 267, 1147912562: 268, 1162261803: 269, 1162261806: 270, 1162261812: 271, 1162261815: 272, 1162262523: 273, 1162262526: 274, 1162263252: 275, 1162263255: 276, 1162263987: 277, 1162263996: 278, 1162264707: 279, 1162265436: 280, 1162266174: 281, 1162266183: 282, 1162266894: 283, 1162267623: 284, 1162441125: 285, 1162443312: 286, 1162618272: 287, 1162620459: 288, 1164564702: 289, 1164741849: 290, 1166867613: 291, 1176611106: 292, 1176611109: 293, 1176611835: 294, 1176611838: 295, 1176613290: 296, 1176614019: 297, 1176615477: 298, 1176616206: 299, 1176789708: 300, 1176791895: 301, 1176966855: 302, 1176969042: 303, 1178913285: 304, 1179090432: 305, 1181216196: 306, 1190960013: 307, 1190960016: 308, 1190960742: 309, 1190960745: 310, 1190962197: 311, 1190962926: 312, 1190964384: 313, 1190965113: 314, 1191138615: 315, 1191140802: 316, 1191315762: 317, 1191317949: 318, 1193262192: 319, 1193439339: 320, 1195565103: 321, 1348797261: 322, 1348797264: 323, 1348799445: 324, 1348801632: 325, 1363146168: 326, 1363146171: 327, 1363148352: 328, 1363150539: 329, 1535333052: 330, 1535333055: 331, 1535335236: 332, 1535337423: 333, 1564208010: 334, 1564385157: 335, 1578556917: 336, 1578734064: 337, 1736217747: 338, 1750566654: 339, 1922753538: 340, 1951628499: 341, 1951805646: 342, 1965977406: 343, 1966154553: 344, 2123638236: 345, 2137987143: 346, 2310174027: 347, 2324523270: 348, 2324523273: 349, 2324523594: 350, 2324523597: 351, 2324523603: 352, 2324523606: 353, 2324523990: 354, 2324523993: 355, 2324524314: 356, 2324524317: 357, 2324524719: 358, 2324524722: 359, 2324525043: 360, 2324525046: 361, 2324525454: 362, 2324525778: 363, 2324525787: 364, 2324526174: 365, 2324526498: 366, 2324526903: 367, 2324527227: 368, 2324527641: 369, 2324527965: 370, 2324527974: 371, 2324528361: 372, 2324528685: 373, 2324529090: 374, 2324529414: 375, 2324702592: 376, 2324702916: 377, 2324704779: 378, 2324705103: 379, 2324879739: 380, 2324880063: 381, 2324881926: 382, 2324882250: 383, 2326826169: 384, 2326826493: 385, 2327003316: 386, 2327003640: 387, 2329129080: 388, 2329129404: 389, 2338872573: 390, 2338872576: 391, 2338873302: 392, 2338873305: 393, 2338874757: 394, 2338875486: 395, 2338876944: 396, 2338877673: 397, 2339051175: 398, 2339053362: 399, 2339228322: 400, 2339230509: 401, 2341174752: 402, 2341351899: 403, 2343477663: 404, 2353221480: 405, 2353221483: 406, 2353222209: 407, 2353222212: 408, 2353223664: 409, 2353224393: 410, 2353225851: 411, 2353226580: 412, 2353400082: 413, 2353402269: 414, 2353577229: 415, 2353579416: 416, 2355523659: 417, 2355700806: 418, 2357826570: 419, 2511058728: 420, 2511058731: 421, 2511060912: 422, 2511063099: 423, 2525407635: 424, 2525407638: 425, 2525409819: 426, 2525412006: 427, 2697594519: 428, 2697594522: 429, 2697596703: 430, 2697598890: 431, 2726469477: 432, 2726646624: 433, 2740818384: 434, 2740995531: 435, 2898479214: 436, 2912828121: 437, 3085015005: 438, 3128238873: 439, 3128416020: 440, 3300248610: 441, 3472435494: 442}
model_action_to_denary_mapping={0: 80, 1: 56934, 2: 174978, 3: 411210, 4: 529254, 5: 4605878, 6: 9567456, 7: 9571824, 8: 9924660, 9: 14171814, 10: 29108970, 11: 33303638, 12: 38265216, 13: 38269584, 14: 38622420, 15: 42869574, 16: 373071590, 17: 373128444, 18: 774959096, 19: 775313372, 20: 803893088, 21: 1147912562, 22: 2324523606, 23: 2324525046, 24: 2324527974, 25: 2324529414, 26: 2324882250, 27: 2329129404, 28: 2353222212, 29: 2353226580, 30: 2353579416, 31: 2357826570, 32: 2697594522, 33: 2697598890, 34: 3128416020, 35: 3472435494}

class TrafficLightController:
    def __init__(self, yellow_time, green_time, training):
        self.phases_indices_dict = denary_to_sumo_idx_mapping
        self.all_green_phases_dict = model_action_to_denary_mapping
        self.YELLOW_TIME = yellow_time
        self.GREEN_TIME = green_time
        self.training = training

        # Keep track of actual vehicle departure times for fair comparison with LDO model
        if not self.training:
            self.actual_depart_times = dict()

    def run_tls_phase(self, current_model_action, next_model_action, step_count):
        # Run a complete traffic light phase change sequence
        # End current phase
        end_phase_idx = self.get_idx_to_end_phase(current_model_action, next_model_action)
        traci.trafficlight.setPhase("0", end_phase_idx)
        for i in range(0, self.YELLOW_TIME):
            self.update_actual_arrivals()
            step_count += 1
            traci.simulationStep(step_count)

        # Start new phase
        start_phase_idx = self.get_idx_to_start_phase(current_model_action, next_model_action)
        traci.trafficlight.setPhase("0", start_phase_idx)
        for i in range(0, self.YELLOW_TIME):
            self.update_actual_arrivals()
            step_count += 1
            traci.simulationStep(step_count)

        # Set green phase
        green_phase_idx = self.get_idx_of_green_phase(next_model_action)
        traci.trafficlight.setPhase("0", green_phase_idx)
        for i in range(0, self.GREEN_TIME):
            self.update_actual_arrivals()
            step_count += 1
            traci.simulationStep(step_count)

        return step_count

    def base3_to_decimal(self, phase):
        # Convert a base-3 representation to decimal
        decimal_value = 0
        for index, digit in enumerate(reversed(phase)):
            decimal_value += digit * (3 ** index)
        return decimal_value

    def decimal_to_base3(self, number, length=20):
        # Convert decimal to base-3 representation with specified length
        base3_digits = []
        while number > 0:
            base3_digits.append(number % 3)
            number //= 3
        
        # Ensure the representation has the correct length
        while len(base3_digits) < length:
            base3_digits.append(0)

        return list(reversed(base3_digits))

    def end_current_phase(self, cur_phase_denary, next_phase_denary):
        # Calculate the phase to end the current phase
        cur_phase = self.decimal_to_base3(cur_phase_denary)
        next_phase = self.decimal_to_base3(next_phase_denary)

        ret = []
        for bit1, bit2 in zip(cur_phase, next_phase):
            if bit1 == 2 and bit2 == 2:
                ret.append(2)
            elif bit1 == 2 and bit2 == 0:
                ret.append(1)
            else:
                ret.append(0)
            
        return self.base3_to_decimal(ret)

    def start_new_phase(self, cur_phase_denary, next_phase_denary):
        # Produce the base 3 representation of the intemediary start phase
        cur_phase = self.decimal_to_base3(cur_phase_denary)
        next_phase = self.decimal_to_base3(next_phase_denary)

        ret = []
        for bit1, bit2 in zip(cur_phase, next_phase):
            if bit1 == 2 and bit2 == 2:
                ret.append(2)
            elif bit1 == 1 and bit2 == 2:
                ret.append(2)
            elif bit1 == 0 and bit2 == 2:
                ret.append(1)
            else:
                ret.append(0)
            
        return self.base3_to_decimal(ret)

    def get_idx_to_end_phase(self, cur_phase, next_phase):
        # Get sumo phase index to end the current phase
        phase1_denary = self.all_green_phases_dict[cur_phase]
        phase2_denary = self.all_green_phases_dict[next_phase]
        end_phase_denary = self.end_current_phase(phase1_denary, phase2_denary)

        return self.phases_indices_dict[end_phase_denary]

    def get_idx_to_start_phase(self, cur_phase, next_phase):
        # Get sumo phase index to start the next phase
        phase1_denary = self.all_green_phases_dict[cur_phase]
        phase2_denary = self.all_green_phases_dict[next_phase]
        end_phase_denary = self.end_current_phase(phase1_denary, phase2_denary)
        start_phase_denary = self.start_new_phase(end_phase_denary, phase2_denary)

        return self.phases_indices_dict[start_phase_denary]

    def get_idx_of_green_phase(self, next_phase):
        # Returns the sumo index of the given phase
        return self.phases_indices_dict[self.all_green_phases_dict[next_phase]]

    def get_array_of_green_lights(self, phase):
        # Returns a boolean array indicating whether or not a given signal is green or not in the current phase
        repr = self.decimal_to_base3(self.all_green_phases_dict[phase])
        for idx, val in enumerate(repr):
            if val == 2:
                repr[idx] = 1

        return repr
    
    def update_actual_arrivals(self):
        ids = traci.simulation.getDepartedIDList()
        for id in ids:
            self.actual_depart_times[id] = (traci.vehicle.getDeparture(id), traci.vehicle.getRouteID(id))

    def save_actual_arrivals(self):
        print(self.actual_depart_times)
        with open("../LinearOptimization/saved_departures.pkl", "wb") as f:
            pickle.dump(self.actual_depart_times, f)