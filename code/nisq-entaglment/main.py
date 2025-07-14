import qiskit
import qiskit.quantum_info
import qiskit_ibm_runtime
from qiskit_ibm_runtime import SamplerV2 as Sampler
import numpy as np
from qiskit_aer.primitives import Sampler as AerSampler
import matplotlib as plt
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_aer.noise import NoiseModel
from qiskit_aer import AerSimulator
from qiskit import transpile
from collections import defaultdict
import json


#-------------Methods-------------
def gen_chsh(x, y, num_qubits=2, phase=np.pi/4):

    base_qc = qiskit.QuantumCircuit(num_qubits, 2)

    base_qc.h(0)
    base_qc.cx(0, num_qubits - 1)

    if x == 1:
        base_qc.h(0)

    if y == 0:
        base_qc.ry(-phase, num_qubits - 1)
    elif y == 1:
        base_qc.ry(phase, num_qubits - 1)   

    base_qc.measure(0, 0)
    base_qc.measure(num_qubits-1, 1)
    #measure_all() #([0, 1], [0, 1])

    return base_qc

def get_expectation(counts, SHOTS):
    agree = counts.get('00', 0) + counts.get('11', 0)
    disagree = counts.get('01', 0) + counts.get('10', 0)
    return (agree - disagree) / SHOTS if SHOTS > 0 else 0

def get_data(backend_name: str, distance: int, phases: list, SHOTS=1024):
    circuits = []
    metadata = []   

    for phase in phases:
        for x_in in [0, 1]:
            for y_in in [0, 1]:
                circuits.append(gen_chsh(x_in, y_in, num_qubits=distance, phase=phase))
                metadata.append({
                    'phase': phase,
                    'x_in': x_in,
                    'y_in': y_in
                })


    service = QiskitRuntimeService()
    backend = service.backend(backend_name)
    noise_model = NoiseModel.from_backend(backend)

    simulator = AerSimulator(noise_model=noise_model)
    transpiled_circuits = [transpile(circ, simulator, optimization_level=3, layout_method="trivial") for circ in circuits]

    results = simulator.run(transpiled_circuits, shots=SHOTS).result()
    counts_list = [results.get_counts(i) for i in range(len(transpiled_circuits))]
    results = list(zip(metadata, counts_list))

    outputs = []
    grouped_by_phase = defaultdict(list)

    for meta, counts in results:
        phase = float(meta['phase'])  
        grouped_by_phase[phase].append((meta['x_in'], meta['y_in'], counts))

    for phase, group in grouped_by_phase.items():
        expectations = []
        for x, y, counts in group:
            e = get_expectation(counts, SHOTS)
            #print(f"Phase={phase:.4f} | E({x},{y}) = {e:.4f}")
            expectations.append(e)

        if len(expectations) == 4:
            chsh_value = expectations[0] + expectations[1] + expectations[2] - expectations[3]
            outputs.append((phase, chsh_value))
            #print(f"→ CHSH for phase {phase:.4f}: {chsh_value:.4f}\n")

    new_result = [
        {
            "backend": backend_name,
            "qubit_distance": distance,
            "data": outputs
        }
    ]

    #gotta load current data first
    with open("data/results.json", "r") as f:
        try:
            results = json.load(f)
        except json.JSONDecodeError:
            results = []

    results.append(new_result)

    with open("data/results.json", "w") as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    phases = np.linspace(-np.pi/2, 3*np.pi, 43)
    backend_names = ["ibm_brisbane", "ibm_torino", "ibm_sherbrooke"]
    distances = list(range(2, 13))

    for backend_name in backend_names:
        for distance in distances:
            get_data(backend_name, distance, phases, SHOTS=10000)
            print(f"Logged data for {backend_name} at distance {distance}")