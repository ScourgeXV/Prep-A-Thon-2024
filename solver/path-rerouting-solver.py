'''
This solver program involves optimization of path taken by each vehicle depending upon the traffic flow from
each intersection and signal timings at them. In this program we are optimizing path for only one vehilcle
The road network data will be read from the CSV file in real case but here it is pre-assumed for simplicity
and vehicle data will be read from another CSV which is also pre-assumed here.

This solver involves creating a cost Hamiltonian from the road network, signal timings and travel timings of
the vehicle. Then this cost Hamiltonian is optimized using Quantum Approximate Optimization Algorithm (QAOA)
which is basically optimum time taken to reach end node.

After simulating the QAOA circuit on quantum simulator, we measure, analyze and decode output we get to get
the optimum path for vehicle.
'''

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# Example distances (in kilometers) between intersections
# In real case Scenario we would input this data exactly from the CSV file containg road graph 
# For simplicity, assume 3 intersections
distances = np.array([
    [0, 1, 2],
    [1, 0, 1],
    [2, 1, 0]
])

# Vehicle speed (in km/h)
vehicle_speed = 40  # Assuming a constant speed for simplification

def calculate_travel_time(distance, speed):
    speed_km_per_min = speed / 60.0
    return distance / speed_km_per_min  # Travel time in minutes

def create_path_cost_hamiltonian(start, end, traffic_flows, signal_timings, emergency_flags):
    n = len(traffic_flows)
    cost_hamiltonian = np.zeros((2**n, 2**n))

    # Initializing the cost for the start node
    for i in range(n):
        # Only consider paths from start to end
        if i == start:
            # Include waiting time for the starting intersection
            waiting_time = signal_timings[i] * traffic_flows[i]
            cost_hamiltonian[i][i] += waiting_time

            # Calculating travel times to other intersections
            for j in range(n):
                if j != start:
                    travel_time = calculate_travel_time(distances[i][j], vehicle_speed)
                    cost_hamiltonian[i][j] += travel_time

    return cost_hamiltonian

def qaoa_path_optimization(start, end, traffic_flows, signal_timings, emergency_flags, p=1):
    n = len(traffic_flows)

    # Creating the cost Hamiltonian for path optimization
    cost_hamiltonian = create_path_cost_hamiltonian(start, end, traffic_flows, signal_timings, emergency_flags)

    # Initializing the QAOA circuit
    qaoa_circuit = QuantumCircuit(n)

    # Applying Hadamard gates to all qubits
    qaoa_circuit.h(range(n))

    # Constructing the QAOA circuit
    for layer in range(p):
        for i in range(n):
            qaoa_circuit.rz(cost_hamiltonian[i][i], i)
            qaoa_circuit.rx(np.pi / 2, i)

    # Measuring the output
    qaoa_circuit.measure_all()

    # Executing on a simulator
    simulator = AerSimulator()
    compiled_circuit = transpile(qaoa_circuit, simulator)
    result = simulator.run(compiled_circuit).result()
    counts = result.get_counts()

    return counts 

def decode_path(binary_string):
    # Mapping of binary digits to intersections
    intersection_mapping = {
        '0': None,  # Stay at the current intersection
        '1': 1,     # Move to next intersection 
    }
    
    path = []
    for i, bit in enumerate(binary_string):
        if bit == '1':
            path.append(i)  # Add the intersection index to the path

    return path

if __name__ == "__main__":
    # Sample traffic flow, signal timings, and emergency vehicle flags
    # As in this case we are considering data of only 1 vehicle we have taken only 1 vehicle for traffic flow
    # This is important so as to get accurate results
    traffic_flows = [1, 0, 0]  # Vehicles per minute at 3 intersections
    signal_timings = [30, 60, 20]  # Signal timings in seconds
    emergency_flags = [False, True, False]  # Emergency vehicles nearby

    # Specify start and end intersections
    start_node = 0  # Starting from intersection 0
    end_node = 2    # Ending at intersection 2

    # Performing QAOA path optimization
    optimization_result = qaoa_path_optimization(start_node, end_node, traffic_flows, signal_timings, emergency_flags, p=1)
    print("QAOA Path Optimization Result:", optimization_result)

    optimum_path_value = max(list(optimization_result.values()))
    for i in optimization_result:
        if optimization_result[i] == optimum_path_value:
            optimum_path = i
            break
    print("Optimized path for vehicle:", decode_path(optimum_path))
