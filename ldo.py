from ortools.linear_solver import pywraplp

def solve_traffic_ilp(num_phases, num_edges, vehicle_arrivals, conflict_pairs, saturation_flow, phase_duration=36):
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        raise RuntimeError("Solver not available")
    
    T = max(max(arrivals) for arrivals in vehicle_arrivals.values()) + 100  # Large enough time horizon
    
    # Decision Variables
    x = {}  # x[s, t]: 1 if phase s is active at time t
    for s in range(num_phases):
        for t in range(T):
            x[s, t] = solver.BoolVar(f'x_{s}_{t}')
    
    q = {}  # q[e, t]: Queue length on edge e at time t
    for e in range(num_edges):
        for t in range(T):
            q[e, t] = solver.IntVar(0, solver.infinity(), f'q_{e}_{t}')
    
    y = {}  # y[i, t]: 1 if vehicle i exits at time t
    for e in vehicle_arrivals:
        for i in range(len(vehicle_arrivals[e])):
            for t in range(T):
                y[e, i, t] = solver.BoolVar(f'y_{e}_{i}_{t}')
    
    T_last = solver.IntVar(0, T, 'T_last')  # Last vehicle exit time
    
    # Constraints
    
    # (1) Fixed phase duration
    # for s in range(num_phases):
    #     for t in range(T - phase_duration + 1):
    #         solver.Add(sum(x[s, t + k] for k in range(phase_duration)) == phase_duration)
    
    # (2) Conflict constraints
    for (s1, s2) in conflict_pairs:
        for t in range(T):
            solver.Add(x[s1, t] + x[s2, t] <= 1)
    
    # (3) Queue dynamics
    for e in range(num_edges):
        for t in range(1, T):
            arrivals = vehicle_arrivals[e].count(t)  # Count vehicles arriving at time t
            departures = solver.Min(q[e, t - 1], sum(saturation_flow[e] * x[s, t - 1] for s in range(num_phases)))
            solver.Add(q[e, t] == q[e, t - 1] + arrivals - departures)
    
    # (4) Vehicle exit tracking
    for e in vehicle_arrivals:
        for i, arrival_time in enumerate(vehicle_arrivals[e]):
            solver.Add(sum(y[e, i, t] for t in range(arrival_time, T)) == 1)  # Must exit at some time
            for t in range(arrival_time, T):
                solver.Add(y[e, i, t] <= q[e, t])  # Can't exit if queue is empty
    
    # (5) Last vehicle exit time
    for e in vehicle_arrivals:
        for i in range(len(vehicle_arrivals[e])):
            for t in range(T):
                solver.Add(T_last >= t * y[e, i, t])
    
    # Objective: Minimize last vehicle exit time
    solver.Minimize(T_last)
    
    status = solver.Solve()
    
    if status == pywraplp.Solver.OPTIMAL:
        print(f"Optimal last vehicle exit time: {T_last.solution_value()}")
    else:
        print("No optimal solution found")

# Example usage
dummy_arrivals = {  # Edge -> list of arrival times
    0: [1, 5, 10],
    1: [2, 6, 12],
    2: [4, 8, 15],
    3: [3, 7, 14]
}
conflicts = [(0, 1), (2, 3)]  # Example conflicting phases
saturation = {0: 5, 1: 5, 2: 5, 3: 5}  # Max departures per step
solve_traffic_ilp(num_phases=4, num_edges=4, vehicle_arrivals=dummy_arrivals, conflict_pairs=conflicts, saturation_flow=saturation)
