import pandas as pd


df = pd.read_csv("results_experiment2_min_rtt_10_agents.csv")

print(df[['path_1_load', 'path_2_load', 'path_3_load']].head())


