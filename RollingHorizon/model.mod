// Parameters
int lambda = 5; // Discretized time step interval
int T = 20;     // Planning horizon
int K = ...;      // Control horizon
int E = 16;     // Number of lanes
float GREEN_Y = 0.3 * lambda;    // Fraction of a vehicle that can leave per time step
float YELLOW_Y = 0.5 * GREEN_Y;   // Yellow phase allows half the flow of green

// Define ranges for indexing
range Time = 0..T-1;    // Time steps range
range Lanes = 0..E-1;   // Lanes range
range CarLanes = 0..E-5;
range PedLanes = E-4..E-1; 

// Input data
float initial_q[Lanes] = ...;        // Initial queue lengths for all lanes
float initial_emv_q[CarLanes] = ...; // Initial emergency vehicle queue lengths
int A[Lanes][Time] = ...;            // Arrivals for the current horizon
int emv_A[CarLanes][Time] = ...;

// Conflict matrix: C[i][j] = 1 means signals i and j conflict
int C[Lanes][Lanes] = [[0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0], [0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1], [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0], [1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0], [1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1], [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1], [1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0], [1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0], [0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1], [0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1], [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1], [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0]];
// Decision Variables
dvar boolean x[Lanes][Time];    // x(e,t) = 1 if lane e is green at time t
dvar boolean y[Lanes][Time];    // y(e,t) = 1 if lane e is yellow at time t
dvar float+ q[Lanes][Time];     // Queue length at lane e, time t
dvar float+ d[Lanes][Time];     // Vehicles/Peds that depart from lane e at time t
dvar float+ emv_q[CarLanes][Time];
dvar float+ emv_d[CarLanes][Time];

// Objective Function: Minimize cumulative queue length
minimize sum(t in Time, e in Lanes) q[e][t] + sum(t in Time, e in CarLanes) emv_q[e][t] + sum(t in Time, e in PedLanes) q[e][t];

// Constraints
subject to {
    // Set initial queue lengths
    forall(e in Lanes)
        q[e][0] == initial_q[e];
    forall(e in CarLanes)
        emv_q[e][0] == initial_emv_q[e];

    // Queue evolution equations
    forall(e in CarLanes, t in 0..T-2)
        q[e][t+1] >= q[e][t] - d[e][t] + A[e][t]; 
        
    forall(e in CarLanes, t in 0..T-2)
        emv_q[e][t+1] >= emv_q[e][t] - emv_d[e][t] + emv_A[e][t];
    
    // Cars can only leave a lane if an emergency vehicle is not leaving
    forall(e in CarLanes, t in Time)
        d[e][t] <= emv_q[e][t]; 
    
    // Max departures must be <= queue length
    forall(e in Lanes, t in Time)
        d[e][t] <= q[e][t];
    forall(e in CarLanes, t in Time)
        emv_d[e][t] <= emv_q[e][t];
      
    // Vehicles can leave when a signal is green or yellow
    forall(e in CarLanes, t in Time)
        d[e][t] <= GREEN_Y * x[e][t] + YELLOW_Y * y[e][t];
    forall(e in CarLanes, t in Time)
        emv_d[e][t] <= GREEN_Y * x[e][t] + YELLOW_Y * y[e][t];
      	
    // Pedestrians can only leave when a signal is green
    forall(e in PedLanes, t in Time)
        d[e][t] <= x[e][t] * 10;	
      
    // Conflicting signals cannot be yellow or green at the same time
    forall(e1 in Lanes, e2 in Lanes : C[e1][e2] == 1, t in Time) {
        x[e1][t] + y[e1][t] + x[e2][t] + y[e2][t] <= 1;
    }
    
    // Yellow phase must be present before and after a transition from green to red
    forall(e in Lanes, t in 1..T-2) {
        y[e][t] >= x[e][t-1] - x[e][t];
        y[e][t] >= x[e][t+1] - x[e][t];
    }
}

// Output queue lengths for the control horizon
execute {
    var logFile = new IloOplOutputFile("log.txt", "a");
    for (var t = 0; t < K; t++) {
        for(var e in Lanes) {
            logFile.write(q[e][t] + " ");
        }
        for(var e in CarLanes) {
            logFile.write(emv_q[e][t] + " ");
        }
        logFile.writeln()
    }
    logFile.close();
}