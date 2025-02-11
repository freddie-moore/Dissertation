#!/usr/bin/env python
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.dev/sumo
# Copyright (C) 2009-2024 German Aerospace Center (DLR) and others.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# https://www.eclipse.org/legal/epl-2.0/
# This Source Code may also be made available under the following Secondary
# Licenses when the conditions for such availability set forth in the Eclipse
# Public License 2.0 are satisfied: GNU General Public License, version 2
# or later which is available at
# https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
# SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later

# @file    runner.py
# @author  Lena Kalleske
# @author  Daniel Krajzewicz
# @author  Michael Behrisch
# @author  Jakob Erdmann
# @date    2009-03-26

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import traci._trafficlight
from traci_environment import TraciEnvironment
from model import DQN
import torch

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa

traci_env = TraciEnvironment("sumo-gui", {i for i in range(0,36)})
state, info = traci_env.reset()
n_actions = traci_env.get_n_actions()
n_observations = len(state)

# Set device
device = torch.device(
    "cuda" if torch.cuda.is_available() else
    "mps" if torch.backends.mps.is_available() else
    "cpu"
)

class SimpleController():
    def __init__(self, phases):
        self.phases = list(phases)
        self.i = 0

    def get_phase(self, state):
        self.i += 1
        return self.i % 3
        

class RLController():
    def __init__(self):
        self.model = DQN(n_observations, n_actions).to(device)
        self.model.load_state_dict(torch.load("./model/model.pth", map_location=device))
        self.model.eval()


    def get_phase(self, state):
        # Convert the state to a tensor if it's not already
        if not isinstance(state, torch.Tensor):
            state = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)

        # Infer the action
        with torch.no_grad():
            action = self.model(state).max(1).indices.item()  # Get the index of the highest Q-value

        return action

controller = SimpleController(traci_env.get_action_space())
# controller = RLController()

def run():
    """execute the TraCI control loop"""
    step_count = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        state = traci_env.get_state()
        phase = controller.get_phase(state)
        # traci_env.get_stuck_vehicles()
        # traci_env.no_lane_change()
        # print("received :", traci_env.get_emv_flags())
        _, _, _, _, step_count = traci_env.run_phase(phase)

    print(f"Execution finished, total time : {step_count}")
    traci.close()
    sys.stdout.flush()

def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options

# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    run()