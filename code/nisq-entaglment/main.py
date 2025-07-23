import qiskit
import qiskit.quantum_info
import qiskit_ibm_runtime
from qiskit_ibm_runtime import SamplerV2 as Sampler
import numpy as np
from qiskit_aer.primitives import Sampler as AerSampler
import matplotlib.pyplot as plt
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
    #noise_model = NoiseModel.from_backend(backend)

    #simulator = AerSimulator(noise_model=noise_model)
    simulator = AerSimulator()

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
    with open("data/ideal_results.json", "r") as f:
        try:
            results = json.load(f)
        except json.JSONDecodeError:
            results = []

    results.append(new_result)

    with open("data/ideal_results.json", "w") as f:
        json.dump(results, f, indent=4)

def graph_data(filePath):
    with open(filePath) as f:
        raw_data = json.load(f)

    backend_data = defaultdict(lambda: defaultdict(float))

    for entry in raw_data:
        backend = entry[0]['backend']
        distance = entry[0]['qubit_distance']
        max_abs_s = max(abs(s) for _, s in entry[0]['data'])
        backend_data[backend][distance] = max_abs_s

    plt.figure(figsize=(10, 6))

    colors = plt.get_cmap('tab10')
    backend_colors = {}

    for idx, (backend, dist_s_dict) in enumerate(backend_data.items()):
        distances = sorted(dist_s_dict.keys())
        s_values = [dist_s_dict[d] for d in distances]

        color = colors(idx)
        backend_colors[backend] = color

        plt.scatter(distances, s_values, color=color, label=backend)

    y_min = 0.75
    y_max = 2 * np.sqrt(2)
    plt.ylim(y_min, y_max)
    plt.yticks(np.arange(0.75, y_max + 0.01, 0.25))
    plt.xticks(np.arange(2, 12 + 0.01, 1))

    plt.axhspan(2, 2 * np.sqrt(2), facecolor='blue', alpha=0.1, hatch='//', edgecolor='blue')

    plt.axhline(y=2, color='gray', linestyle='--', label='Classical limit')
    plt.axhline(y=2 * np.sqrt(2), color='green', linestyle='--', label="Tsirelson's bound")

    plt.xlabel("Qubit Distance")
    plt.ylabel("Max |S| Value")
    plt.title("Max |S| Value vs Qubit Distance Across Backends")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def graph_single_output(backend_name: str, distance: int, filePath: str):
    outputs = get_single_output(backend_name, distance, filePath)["data"]
    phases_extracted, S_extracted = zip(*outputs)

    plt.figure(figsize=(10, 6))
    plt.plot(phases_extracted, S_extracted, marker='o', linestyle='-', color='blue', label='CHSH parameter')

    plt.xlim(-np.pi/2, 3*np.pi)
    plt.ylim(-2*np.sqrt(2), 2*np.sqrt(2))

    xticks = np.arange(-np.pi/2, 3*np.pi + 0.1, np.pi/2)
    xtick_labels = [r"$-\frac{\pi}{2}$", r"$0$", r"$\frac{\pi}{2}$", r"$\pi$", r"$\frac{3\pi}{2}$", r"$2\pi$", r"$\frac{5\pi}{2}$", r"$3\pi$"]
    plt.xticks(xticks, xtick_labels)

    yticks = np.arange(-2*np.sqrt(2), 2*np.sqrt(2) + 0.1, 1)
    plt.yticks(yticks)

    plt.axhspan(2, 2*np.sqrt(2), facecolor='blue', alpha=0.1, hatch='//', edgecolor='blue')
    plt.axhspan(-2*np.sqrt(2), -2, facecolor='blue', alpha=0.1, hatch='//', edgecolor='blue')

    plt.axhline(y=2, color='gray', linestyle='--', label='Classical limit (+2)')
    plt.axhline(y=-2, color='gray', linestyle='--', label='Classical limit (−2)')
    plt.axhline(y=2*np.sqrt(2), color='green', linestyle='--', label="Tsirelson's bound (+)")
    plt.axhline(y=-2*np.sqrt(2), color='green', linestyle='--', label="Tsirelson's bound (−)")

    plt.title(f"CHSH Parameter vs Phase ({backend_name})")
    plt.xlabel("Phase (radians)")
    plt.ylabel("CHSH Parameter (S)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

def get_single_output(backend_name: str, distance: int, filePath: str) -> dict:
    with open(filePath) as f:
        raw_data = json.load(f)

    for entry in raw_data:
        if entry[0]["backend"] == backend_name and entry[0]["qubit_distance"] == distance:
            return entry[0]



if __name__ == "__main__":
    phases = np.linspace(-np.pi/2, 3*np.pi, 43)
    backend_names = ["ibm_brisbane", "ibm_torino", "ibm_sherbrooke"]
    distances = list(range(2, 13))

    for backend_name in backend_names:
        for distance in distances:
            get_data(backend_name, distance, phases, SHOTS=10000)
            print(f"Logged data for {backend_name} at distance {distance}")
    #graph_single_output("ibm_torino", 2, "data/ideal_results.json")
    #print(get_single_output("ibm_torino", 2, "data/results.json"))
    graph_data("data/ideal_results.json")