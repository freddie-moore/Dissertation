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
import random
import numpy as np
import traci._trafficlight

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa

# The program looks like this
#    <tlLogic id="0" type="static" programID="0" offset="0">
# the locations of the tls are      NESW
#        <phase duration="31" state="GrGr"/>
#        <phase duration="6"  state="yryr"/>
#        <phase duration="31" state="rGrG"/>
#        <phase duration="6"  state="ryry"/>
#    </tlLogic>

def generate_routes():
    random.seed(10)

    route_ids = {"ne", "ns", "nw", "en", "es", "ew","se", "sn", "sw","wn", "we", "ws"}

    n = 1000 # number of vehicles
    arrival_rate = 1
    arrival_times = np.cumsum(np.random.exponential(1/arrival_rate, size=n))

    with open("input_routes.rou.xml", "w") as routes:
        routes.write("""<routes>
            <vType id="type1" accel="0.8" decel="4.5" sigma="0.5" length="5" maxSpeed="70"/>
            <vType id="bike" vClass="bicycle"/>
            <vType id="rescue" vClass="emergency" maxSpeed="70" accel="0.8" speedFactor="1.5" guiShape="emergency">
                <param key="has.bluelight.device" value="true"/>
            </vType>
            <route id="ne" edges="ni eo"/>
            <route id="ns" edges="ni so"/>
            <route id="nw" edges="ni wo"/>
            <route id="en" edges="ei no"/>
            <route id="es" edges="ei so"/>
            <route id="ew" edges="ei wo"/>
            <route id="sn" edges="si no"/>
            <route id="se" edges="si eo"/>
            <route id="sw" edges="si wo"/>
            <route id="wn" edges="wi no"/>
            <route id="we" edges="wi eo"/>
            <route id="ws" edges="wi so"/>
        """)

        
        
        for i, route in enumerate(route_ids):
            routes.write(f"""<personFlow id="{i}" begin = "0" end="{n}" perHour="20">
                     <walk route="{route}"/>
            </personFlow>
            """)
        
        for i, arrival_time in enumerate(arrival_times):
            route = random.choice(list(route_ids))
            rand = random.random()
            if rand < 0.005:
                vehicle_type = "rescue"
            elif rand < 0.05:
                vehicle_type = "bike"
            else:
                vehicle_type = "type1"
                
            routes.write(f"<vehicle id=\"{route}_{i}\" type=\"{vehicle_type}\" route=\"{route}\" depart=\"{arrival_time}\" />\n")

        routes.write("</routes>")

def run():
    """execute the TraCI control loop"""
    step = 0
    GREEN_TIME = 30
    YELLOW_TIME = 6

    edge_ids = {"ni", "ei", "si", "wi"}
    self_defined_edges = {"ni": 0,"ei": 2,"si": 4,"wi": 6}
    while traci.simulation.getMinExpectedNumber() > 0:
        print(f"Expected cars left {traci.simulation.getMinExpectedNumber()}")
        max_edge = getMaxWaitingLane(edge_ids)
        if max_edge:
            # Initial yellow phase
            traci.trafficlight.setPhase("0", self_defined_edges[max_edge])
            for _ in range(YELLOW_TIME):
                traci.simulationStep()

            # Green phase
            traci.trafficlight.setPhase("0", self_defined_edges[max_edge]+1)
            cont = True
            while cont:
                for _ in range(GREEN_TIME):
                    traci.simulationStep()
                if getMaxWaitingLane(edge_ids) != max_edge or traci.simulation.getMinExpectedNumber() == 0:
                    cont = False

            # End yellow phase
            traci.trafficlight.setPhase("0", self_defined_edges[max_edge])
            for _ in range(YELLOW_TIME):
                traci.simulationStep()
        else:
            traci.trafficlight.setPhase("0", 8)
            for _ in range(GREEN_TIME):
                traci.simulationStep()

        step += 1
    traci.close()
    sys.stdout.flush()

def getMaxWaitingLane(edge_ids):
    max_wait = float('-inf')
    highest_edge = None
    for edge_id in edge_ids:
        if traci.edge.getWaitingTime(edge_id) > max_wait:
            highest_edge = edge_id
            max_wait = traci.edge.getWaitingTime(edge_id)

    return highest_edge if max_wait > 0  else None
    
def getTimeLeftInTrafficPhase(trafficLightId):
    return traci.trafficlight.getNextSwitch(trafficLightId) - traci.simulation.getTime()

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

    # first, generate the route file for this simulation
    generate_routes()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "test.sumocfg",
             "--tripinfo-output", "tripinfo.xml"])

    run()