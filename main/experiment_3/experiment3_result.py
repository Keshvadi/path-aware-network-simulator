import pandas as pd
import csv
import matplotlib.pyplot as plt


files = {
    "min_rtt": "results_with_loss_min_rtt_100_agents.csv",
    "min_load": "results_with_loss_min_load_100_agents.csv",
}

paths_to_track = [
    "path_1",
    "path_2",
]


for strategy, file in files.items():
    df = pd.read_csv(file)
    
    # Plot Throughput
    plt.plot(df["timestep"], df["total_throughput"], label=strategy)
    print(f"{strategy}: Total Loss = {df['total_loss'].sum():.2f}")
    
    # Oszillation (Stabilität)
    path_cols = [col for col in df.columns if col.endswith('_load')]
    oscillation = df[path_cols].std().mean()
    print(f"{strategy}: Avg. Oscillation = {oscillation:.2f}")

plt.title("Throughput Over Time")
plt.xlabel("Timestep")
plt.ylabel("Throughput (Mbps)")
plt.legend()
plt.grid(True)
plt.show()

show_path_loads = True



plt.figure(figsize=(10, 5))

for strategy, file in files.items():
    df = pd.read_csv(file)
    plt.plot(df["timestep"], df["path_1_load"], label=f"{strategy} – path_1")
    plt.plot(df["timestep"], df["path_2_load"], label=f"{strategy} – path_2")

plt.title("Load on Each Path Over Time")
plt.xlabel("Timestep")
plt.ylabel("Load (CWND sum)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


for strategy, file in files.items():
    df = pd.read_csv(file)
    total_load_1 = df["path_1_load"].sum()
    total_load_2 = df["path_2_load"].sum()
    total_loss_1 = df["path_1_loss"].sum()
    total_loss_2 = df["path_2_loss"].sum()
    print(f"\n{strategy.upper()} Results:")
    print(f"Total Load on path_1: {total_load_1:.2f}")
    print(f"Total Load on path_2: {total_load_2:.2f}")
    print(f"Total Loss on path_1: {total_loss_1:.2f}")
    print(f"Total Loss on path_2: {total_loss_2:.2f}")

