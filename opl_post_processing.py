arr = """0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 1 1 1 0 0 0
0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 1 0 0 0 0 0
0 0 1 1 1 0 0 0 0 1 0 0 1 0 0 0 0 0 0 0 0 0
1 1 0 0 0 1 1 1 0 1 1 1 0 0 0 0 0 0 0 0 0 0
1 1 0 0 0 1 1 1 0 0 1 1 0 0 0 0 0 0 0 0 0 0
0 0 0 1 1 1 0 0 0 0 1 1 1 0 0 0 0 0 0 0 0 0
1 1 1 0 0 0 1 1 1 0 0 0 0 1 0 0 0 0 0 0 0 0
1 1 1 0 0 0 1 1 0 0 0 0 0 1 1 0 0 0 0 0 0 0
0 0 1 1 1 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 1 1 1
0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 1 1 1 1 1
0 0 0 1 1 1 0 0 1 0 1 1 0 0 0 0 0 0 0 0 0 0"""


arr = arr.split("\n")

for idx, str in enumerate(arr):
    arr[idx] = str.split(" ")
    for i, char in enumerate(arr[idx]):
        arr[idx][i] = int(char)

time_steps = len(arr[0])
num_lanes = len(arr)
print(num_lanes, time_steps)
print(arr)
active_phases_count = []
for t in range(0,time_steps):
    total = 0
    for l in range(0,num_lanes):
        total += arr[l][t]
    active_phases_count.append(total)
        
print(active_phases_count)

phase_lenghts = []
for row in arr:
    count = 0
    for num in row:
        if num == 1:
            count += 1
        elif count > 0:
            phase_lenghts.append(count)
            count = 0
    if count > 0:
        phase_lenghts.append(count)

print(phase_lenghts)
