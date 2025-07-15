from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector, SparsePauliOp
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime import QiskitRuntimeService
import numpy as np

def calculate_horodecki_bound(paulis_expectation_values):
    """Calculate Horodecki CHSH bound from Pauli expectation values"""
    T = np.zeros((3, 3))
    for idx, exp_val in enumerate(paulis_expectation_values):
        T[idx, idx] = exp_val
    
    U = T.T @ T
    eigenvalues = np.linalg.eigvalsh(U)
    eigenvalues = sorted(eigenvalues, reverse=True)
    
    B_rho = 2 * np.sqrt(eigenvalues[0] + eigenvalues[1])
    return T, U, eigenvalues, B_rho

def run_noiseless_simulation():
    """Run ideal noiseless simulation"""
    print("="*50)
    print("NOISELESS SIMULATION")
    print("="*50)
    
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    
    state = Statevector.from_instruction(qc)
    
    paulis = ['XX', 'YY', 'ZZ']
    expectation_values = []
    
    for pauli_str in paulis:
        pauli_op = SparsePauliOp.from_list([(pauli_str, 1.0)])
        exp_val = np.real(state.expectation_value(pauli_op))
        expectation_values.append(exp_val)
    
    T, U, eigenvalues, B_rho = calculate_horodecki_bound(expectation_values)
    
    print("Correlation matrix T:")
    print(T)
    print("\nU = TᵀT:")
    print(U)
    print(f"\nHorodecki CHSH bound: {B_rho:.6f}")
    print(f"Horodecki Criterion: {eigenvalues[0] + eigenvalues[1]:.6f}")
    
    return B_rho

def run_noisy_simulation():
    """Run simulation with IBM Brisbane noise model"""
    print("\n" + "="*50)
    print("NOISY SIMULATION (IBM Brisbane)")
    print("="*50)
    
    try:
        service = QiskitRuntimeService()
        backend = service.backend("ibm_brisbane")
        noise_model = NoiseModel.from_backend(backend)
        
        print(f"Noise model created from: {backend.name}")
        print(f"Number of qubits: {backend.configuration().n_qubits}")
        print(f"Basis gates: {backend.configuration().basis_gates}")
        
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        
        qc_transpiled = transpile(qc, backend, optimization_level=3)
        
        simulator = AerSimulator(noise_model=noise_model)
        
        paulis = ['XX', 'YY', 'ZZ']
        expectation_values = []
        
        for pauli_str in paulis:
            meas_qc = qc_transpiled.copy()
            
            if pauli_str[0] == 'X':
                meas_qc.ry(-np.pi/2, 0)
            elif pauli_str[0] == 'Y':
                meas_qc.rx(np.pi/2, 0)
            
            if pauli_str[1] == 'X':
                meas_qc.ry(-np.pi/2, 1)
            elif pauli_str[1] == 'Y':
                meas_qc.rx(np.pi/2, 1)
            
            meas_qc.measure_all()
            
            job = simulator.run(meas_qc, shots=8192)
            result = job.result()
            counts = result.get_counts()
            
            total_shots = sum(counts.values())
            exp_val = 0
            for bitstring, count in counts.items():
                parity = sum(int(bit) for bit in bitstring) % 2
                sign = 1 if parity == 0 else -1
                exp_val += sign * count / total_shots
            
            expectation_values.append(exp_val)
            print(f"Expectation value for {pauli_str}: {exp_val:.6f}")
        
        T, U, eigenvalues, B_rho = calculate_horodecki_bound(expectation_values)
        
        print("\nCorrelation matrix T:")
        print(T)
        print("\nU = TᵀT:")
        print(U)
        print(f"\nHorodecki CHSH bound: {B_rho:.6f}")
        print(f"Horodecki Criterion: {eigenvalues[0] + eigenvalues[1]:.6f}")
        
        return B_rho
        
    except Exception as e:
        print(f"Error accessing IBM Brisbane backend: {e}")

# Run both simulations
noiseless_bound = run_noiseless_simulation()
noisy_bound = run_noisy_simulation()

# Summary comparison
print("\n" + "="*50)
print("COMPARISON SUMMARY")
print("="*50)
print(f"Classical bound: 2.0")
print(f"Quantum bound (Tsirelson): {2*np.sqrt(2):.6f}")
print(f"Noiseless simulation: {noiseless_bound:.6f}")
print(f"Noisy simulation: {noisy_bound:.6f}")
print(f"Noise degradation: {noiseless_bound - noisy_bound:.6f}")

# Entanglement assessment
print(f"\nEntanglement analysis:")
print(f"Noiseless: {'Entangled' if noiseless_bound > 2.0 else 'Separable'}")
print(f"Noisy: {'Entangled' if noisy_bound > 2.0 else 'Separable'}")