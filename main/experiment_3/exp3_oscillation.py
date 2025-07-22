import csv
import pandas as pd

agents = [10, 25, 50, 100]
losses = []

print("Oscillation analysis:\n")



df_rtt = pd.read_csv("results_with_loss_min_rtt_100_agents.csv")
path_load_cols = [col for col in df_rtt.columns if col.endswith('_load')]
oscillation_rtt = df_rtt[path_load_cols].std().mean()
print(f"Min-RTT with 100 agents → Oscillation: {oscillation_rtt:.2f}")


df_load = pd.read_csv("results_with_loss_min_load_100_agents.csv")
oscillation_load = df_load[path_load_cols].std().mean()
print(f"Min-Load with  agents → Oscillation: {oscillation_load:.2f}")

