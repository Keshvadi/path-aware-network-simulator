import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# plotting configurations

files = {
    "min_rtt": [
        ("10 agents", "results_experiment2_min_rtt_10_agents.csv"),
        ("25 agents", "results_experiment2_min_rtt_25_agents.csv"),
        ("50 agents", "results_experiment2_min_rtt_50_agents.csv"),
        ("100 agents", "results_experiment2_min_rtt_100_agents.csv"),
    ],
    "min_load": [
        ("10 agents", "results_experiment2_min_load_10_agents.csv"),
        ("25 agents", "results_experiment2_min_load_25_agents.csv"),
        ("50 agents", "results_experiment2_min_load_50_agents.csv"),
        ("100 agents", "results_experiment2_min_load_100_agents.csv"),
    ],
}

data = {
    "min_rtt": [],
    "min_load": [],
}
labels = []

for strategy, runs in files.items():
    for label, filename in runs:
        throughputs = []
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                throughputs.append(float(row['total_throughput']))
        avg = np.mean(throughputs)
        std = np.std(throughputs)
        data[strategy].append((avg, std))
        if strategy == "min_rtt":
            labels.append(label)


x = np.arange(len(labels))  # [0, 1, 2, 3]
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))
rtt_means = [val[0] for val in data["min_rtt"]]
rtt_stds = [val[1] for val in data["min_rtt"]]
load_means = [val[0] for val in data["min_load"]]
load_stds = [val[1] for val in data["min_load"]]


ax.bar(x - width/2, rtt_means, width,  label='Min-RTT', capsize=5)
ax.bar(x + width/2, load_means, width, label='Min-Load', capsize=5)

ax.set_ylabel('Average Throughput (Mbps)')
ax.set_title('Average Throughput with Increasing Number of Agents')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.show()




agent_counts = [10, 25, 50, 100]
strategies = ['min_rtt', 'min_load']

results = {}

for strategy in strategies:
    losses = []
    for n in agent_counts:
        filename = f"results_with_loss_{strategy}_{n}_agents.csv"
        df = pd.read_csv(filename)
        
        avg_loss = df['total_loss'].mean()
        losses.append(avg_loss)
    
    results[strategy] = losses

plt.figure(figsize=(8, 5))
for strategy in strategies:
    plt.plot(agent_counts, results[strategy], marker='o', label=strategy)

plt.title("Average Packet Loss vs. Number of Agents")
plt.xlabel("Number of Agents")
plt.ylabel("Average Packet Loss")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
