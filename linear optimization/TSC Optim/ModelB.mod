/*********************************************
 * OPL 22.1.2.0 Model
 * Author: fredd
 * Creation Date: 25 Feb 2025 at 10:50:01
 *********************************************/
// Traffic Signal Control Optimization in OPL
int T = ...; // Total simulation time
int E = ...; // Number of lanes
int K = ...; // Maximum number of on / off periods per light

range Time = 0..T-1;
range Lanes = 0..E-1;
range Activation = 1..K;

// Given Parameters
float A[Lanes][Time] = ...;  // Vehicle arrival rate at each approach
float y = 0.38; // Fraction of a vehicle that can leave per time step

// Conflict Matrix
int C[Lanes][Lanes];

// Decision Variables
dvar int+ x_on[Lanes][Activation];  // Start time of green phase for each approach
dvar int+ x_off[Lanes][Activation]; // End time of green phase for each approach
dvar float+ q[Lanes][Time];             // Queue length at each approach at time t
dvar float+ d[Lanes][Time];            // Departures from each approach at time t

// Objective: Minimize total queue length over time
minimize sum(a in Lanes, t in Time) q[a][t];


subject to {
  // Light cannot reactivate until after it has switched off
  forall(a in Lanes, k in 1..K-1) {
    x_off[a][k] <= x_on[a][k+1];
  }

  // Conflicting signals cannot be active at the same time
  forall(a in Lanes, b in Lanes: C[a][b] == 1, k in Activation, m in Activation) {
    x_on[a][k] >= x_off[b][m] || x_on[b][m] >= x_off[a][k];
  }


  forall(a in Lanes, t in 1..T-1) {
    // Queue evolution equation
    q[a][t+1] == q[a][t] + A[a][t] - d[a][t];  

    // Vehicles can only leave when a signal is green
    // NOTE FOR GEERT : This is the constraint that I am stuck on
	// d[a][t] <= y * (sum(k in Activation) (t >= x_on[a][k] && t < x_off[a][k] ? 1 : 0));
    
    // Max actors that leave a queue must be <= queue length
    d[a][t] <= q[a][t];
  }
}
 