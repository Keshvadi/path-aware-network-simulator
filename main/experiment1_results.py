import csv
import matplotlib.pyplot as plt


files = {
    "min_rtt": "results_experiment1_min_rtt_50_agents.csv",
    "min_load": "results_experiment1_min_load_50_agents.csv",
    #"attribute_aware": "results_experiment1_attribute_aware_50_agents.csv"
}

paths_to_track = [
    "path_1",
    "path_2",
    "path_3",
]

show_path_loads = True

plt.figure(figsize=(10, 5))
for strategy, filename in files.items():
    timesteps = []
    throughput = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            timesteps.append(int(row['timestep']))
            throughput.append(float(row['total_throughput']))
    plt.plot(timesteps, throughput, label=strategy)
plt.title('Throughput Over Time')
plt.xlabel('Timestep') 
plt.ylabel('Throughput (Mbps)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show() 


if show_path_loads:
    for strategy, filename in files.items():
        plt.figure(figsize=(10, 5))
        path_loads = {p: [] for p in paths_to_track}
        timesteps = []
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                timesteps.append(int(row['timestep']))
                for p in paths_to_track:
                    key = f'{p}_load' 
                    if key in row:
                        path_loads[p].append(float(row[key])) 
        for p in path_loads:
            if path_loads[p]:
                plt.plot(timesteps, path_loads[p], label=f'{strategy} - {p}')
        plt.title(f'Path Loads - {strategy}')
        plt.xlabel('Timestep')
        plt.ylabel('Load (Mbps)')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()