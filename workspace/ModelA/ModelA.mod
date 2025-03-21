/*********************************************
 * OPL 22.1.2.0 Model
 * Author: fredd
 * Creation Date: 15 Feb 2025 at 18:09:32
 *********************************************/
int T = 15;  // Number of timesteps
int E = 4;    // Number of lanes
float y = 0.38;    // Fraction of a vehicle that can leave per time step

// Define ranges for indexing
range Time = 0..T-1; // Time steps range
range Lanes = 0..E-1; // Lanes range

int A[Lanes][Time] = [[0, 2, 0, 0, 0, 0, 2, 0, 0, 0], [0, 0, 0, 2, 2, 0, 0, 0, 2, 0], [2, 2, 0, 2, 0, 0, 2, 0, 0, 0], [2, 2, 2, 2, 2, 2, 2, 2, 0, 2]];

// Conflict matrix: C[i][j] = 1 means signals i and j conflict
int C[Lanes][Lanes] = [[1, 1, 1, 1, 1], [1,0, 1, 1], [1,1, 0, 1], [1,1, 1, 0]];

execute {
    writeln("C Matrix:");
    for (var i in Lanes) {
        writeln(C[i]);
    }
}

// Decision Variables
dvar boolean x[Lanes][Time]; // x(e,t) = 1 if lane e is green at time t
dvar float+ q[Lanes][Time]; // Queue length at lane e, time t
dvar float+ d[Lanes][Time]; // Vehicles that depart from lane e at time t

// Objective Function: Minimizing cumulative queue length
minimize sum(t in Time, e in Lanes) q[e][t];

// Constraints
subject to {
    // Queue evolution equation
    forall(e in Lanes, t in 0..T-2)
    	q[e][t+1] >= q[e][t] - d[e][t] + A[e][t];
    
    // Max cars that leave a queue must be <= queue length
    forall(e in Lanes, t in Time)
        d[e][t] <= q[e][t];
        
    // Cars can only leave a queue if the respective signal is green, at a rate of y
    forall(e in Lanes, t in Time)
        d[e][t] <= y * x[e][t];

    // Conflicting signals cannot be active at the same time
    forall(e1 in Lanes, e2 in Lanes : C[e1][e2] == 1, t in Time)
        x[e1][t] + x[e2][t] <= 1;
}	