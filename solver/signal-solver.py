'''
This solver program involves optimization of signal timings taking into considerations emergency
vehicles and normal traffic flows. However, this program pre-assumes already processed data for
the sake of simplicity, which in a real case scenario we would need to process from the 3 CSV
files taken as input.

This solver involves creating a cost Hamiltonian from the processed input and then using Quantum
Approximate Optimization Algorithm (QAOA) to optimize the cost function which is basically waiting
time for at each intersection (node of graph).

After simulating the QAOA circuit on quantum simulator, we measure, analyze and decode output we
get to optimized signal timings.
'''

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# Function to create the cost Hamiltonian based on the traffic data for signal optimization
def create_cost_hamiltonian(traffic_flows, signal_timings, emergency_flags):
    n = len(traffic_flows)  # Number of intersections
    # Initializing the cost Hamiltonian 
    cost_hamiltonian = np.zeros((2**n, 2**n))

    for i in range(n):
        # Waiting time component for each intersection: W_i = Signal Timing * Traffic Flow
        waiting_time = signal_timings[i] * traffic_flows[i]
        
        # Apply the waiting time to the Hamiltonian
        # This is a simple diagonal representation for the cost function
        cost_hamiltonian[i][i] += waiting_time

        # Emergency vehicle component
        if emergency_flags[i]:  # If an emergency vehicle is nearby
            emergency_penalty = 100  # Arbitrary penalty value
            cost_hamiltonian[i][i] += emergency_penalty

    return cost_hamiltonian

# QAOA Implementation for signal timings at each node
def qaoa_traffic_optimization(traffic_flows, signal_timings, emergency_flags, p=1):
    n = len(traffic_flows)

    # Creating the cost Hamiltonian
    cost_hamiltonian = create_cost_hamiltonian(traffic_flows, signal_timings, emergency_flags)

    # Initializing the QAOA circuit
    qaoa_circuit = QuantumCircuit(n)

    # Applying Hadamard gate to all qubits
    qaoa_circuit.h(range(n))

    # Constructing the QAOA circuit with parameterized rotations
    for layer in range(p):
        # Use RZ and RX gates to represent the cost Hamiltonian
        for i in range(n):
            qaoa_circuit.rz(cost_hamiltonian[i][i], i)  # RZ rotation based on the Hamiltonian
            qaoa_circuit.rx(np.pi / 2, i)  # RX rotation for mixing

    # Measuring the output
    qaoa_circuit.measure_all()

    # Executing on a simulator
    simulator = AerSimulator()
    compiled_circuit = transpile(qaoa_circuit, simulator)
    result = simulator.run(compiled_circuit).result()
    counts = result.get_counts()

    return counts

def decode_signals(binary_string):
    # Mapping of binary digits to signal timings
    signal_timings = {'0':20, '1':30, '2':60}
    
    # Decode each bit of the binary string into its corresponding timing
    decoded_timings = []
    for bit in binary_string:
        if bit in signal_timings:
            decoded_timings.append(signal_timings[bit])
        else:
            raise ValueError(f"Unexpected bit '{bit}' in binary string.")
    
    return decoded_timings

if __name__ == "__main__":
    # Sample traffic flow, signal timings, and emergency vehicle flags
    # This data can be processed through the 3 CSV files we will input for our program
    # For simplicity in this case, we are considering these simple processsed inputs
    traffic_flows = [50, 40, 10]  # Vehicles per minute at 3 intersections
    signal_timings = [30, 60, 20]  # Signal timings in seconds
    emergency_flags = [False, True, False]  # Emergency vehicles nearby

    # Performing QAOA optimization
    optimization_result = qaoa_traffic_optimization(traffic_flows, signal_timings, emergency_flags, p=1)
    print("QAOA Optimization Result:", optimization_result)

    optimum_signal_value = max(list(optimization_result.values()))
    for i in optimization_result:
        if optimization_result[i] == optimum_signal_value:
            optimum_signal = i
            break
    print("Optimized Signal Timings:", decode_signals(optimum_signal))
