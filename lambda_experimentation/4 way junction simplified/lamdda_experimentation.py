import traci
from sumolib import checkBinary
from write_routes import generate_routes
import matplotlib.pyplot as plt

def plot_arrays(x_values, y_values, title="Graph", xlabel="X-axis", ylabel="Y-axis"):
    if len(x_values) != len(y_values):
        raise ValueError("x_values and y_values must have the same length")
    
    plt.figure(figsize=(8, 5))
    plt.plot(x_values, y_values, marker='o', linestyle='-')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    plt.show()

params = [ 
                "-c", "test.sumocfg", 
                "-W", "true",
                "--lateral-resolution", "0.2"
            ]

binary = "sumo"
sumoBinary = checkBinary(binary)
traci.start([sumoBinary, *params])

avgs = []
car_counts = []

for j in range(1, 100, 5):
    num_cars = j
    


    generate_routes(num_cars)

    step_count = 0

    # keep specific route red for set amount of time
    traci.trafficlight.setPhase("0", 0)
    buffer = 500
    step_count += buffer
    traci.simulationStep(step_count)

    while traci.lane.getLastStepVehicleNumber("ni_1") > 0:  
        traci.trafficlight.setPhase("0", 2)
        step_count += 1
        traci.simulationStep(step_count)

    time = traci.simulation.getTime()
    avg = (time - buffer) / num_cars
    print(f"Processed {num_cars} vehicles in {time} steps. Avg time per vehicle is {avg}")
    avgs.append(avg)
    car_counts.append(j)
    traci.load(params)

avgs = avgs[1::]
car_counts = car_counts[1::]
plot_arrays(car_counts, avgs, "Car Counts / Avgs", "Car Counts", "Avg Time Per Car to Cross Junction")