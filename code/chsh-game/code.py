import cirq
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

def create_chsh_circuit(x, y):    
    a = cirq.NamedQubit("Alice")
    b = cirq.NamedQubit("Bob")
    circuit = cirq.Circuit()

    circuit.append(cirq.H(a))
    circuit.append(cirq.CNOT(a, b))

    if x == 1:
        circuit.append(cirq.H(a))  

    if y == 0:
        circuit.append(cirq.ry(-np.pi / 4)(b))  
    elif y == 1:
        circuit.append(cirq.ry(np.pi / 4)(b))   

    circuit.append(cirq.measure(a, key="a"))
    circuit.append(cirq.measure(b, key="b"))

    return circuit

circuits = []
input_pairs = []
for x_in in [0, 1]:
    for y_in in [0, 1]:
        input_pairs.append((x_in, y_in))
        circuits.append(create_chsh_circuit(x_in, y_in))

repetitions=1024
simulator = cirq.Simulator()
results = [simulator.run(c, repetitions=repetitions) for c in circuits]

def format_counts(result):
    print(result.data)
    c0 = result.data['a']
    c1 = result.data['b']
    ba_pairs = [f"{b}{a}" for b, a in zip(c1, c0)]  
    return Counter(ba_pairs)

counts_list = [format_counts(r) for r in results]

for i, (x, y) in enumerate(input_pairs):
    print(f"Inputs (x={x}, y={y}):")
    sorted_counts = dict(sorted(counts_list[i].items()))
    print(f"  Outcomes (ba): {sorted_counts}")

def plot_histograms(counts_list, legends, title):
    fig, ax = plt.subplots(figsize=(10, 6))
    width = 0.2
    x_labels = sorted({k for counts in counts_list for k in counts})
    x = np.arange(len(x_labels))

    for i, counts in enumerate(counts_list):
        heights = [counts.get(label, 0) for label in x_labels]
        ax.bar(x + i * width, heights, width=width, label=legends[i])

    ax.set_xticks(x + width * (len(counts_list)-1) / 2)
    ax.set_xticklabels(x_labels)
    ax.set_title(title)
    ax.set_ylabel("Counts")
    ax.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

print("Plotting results...")
plot_histograms(
    counts_list,
    legends=[f'(x={x}, y={y})' for x, y in input_pairs],
    title='CHSH Game Outcomes'
)

def get_expectation(counts):
    agree = counts.get('00', 0) + counts.get('11', 0)
    disagree = counts.get('01', 0) + counts.get('10', 0)
    return (agree - disagree) / repetitions if repetitions > 0 else 0

expectations = []
for (x, y), counts in zip(input_pairs, counts_list):
    e = get_expectation(counts)
    print(f"E({x},{y}) = {e:.4f}")
    expectations.append(e)

# CHSH = E(0,0) + E(0,1) + E(1,0) - E(1,1)
chsh_value = abs(expectations[0] + expectations[1] + expectations[2] - expectations[3])
print(f"\nCHSH Value: {chsh_value:.4f}")
