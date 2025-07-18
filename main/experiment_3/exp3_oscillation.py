# import csv
# import pandas as pd

# agents = [10, 25, 50, 100]
# losses = []

# print("Oscillation analysis:\n")



# df_rtt = pd.read_csv("results_with_loss_min_rtt_100_agents.csv")
# path_load_cols = [col for col in df_rtt.columns if col.endswith('_load')]
# oscillation_rtt = df_rtt[path_load_cols].std().mean()
# print(f"Min-RTT with 100 agents → Oscillation: {oscillation_rtt:.2f}")


# df_load = pd.read_csv("results_with_loss_min_load_100_agents.csv")
# oscillation_load = df_load[path_load_cols].std().mean()
# print(f"Min-Load with 100 agents → Oscillation: {oscillation_load:.2f}")

import pandas as pd
import matplotlib.pyplot as plt

strategies = {
    "min_rtt": "results_with_loss_min_rtt_100_agents.csv",
    "min_load": "results_with_loss_min_load_100_agents.csv",
}

for strategy, file in strategies.items():
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
