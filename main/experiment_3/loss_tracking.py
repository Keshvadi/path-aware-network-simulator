import pandas as pd


losses = []

max_loss_min_rtt = 0
max_loss_time_min_rtt = None
max_loss_path_min_rtt = None 

max_loss_min_load = 0
max_loss_time_min_load = None
max_loss_path_min_load = None 


print("avg loss for min_rtt with increasing number of agents")


df = pd.read_csv("results_with_loss_min_rtt_100_agents.csv")
loss_cols = [col for col in df.columns if col.endswith('_loss') and col != 'total_loss']
for col in loss_cols:
    current_max = df[col].max()
    if current_max > max_loss_min_rtt:
        max_loss_min_rtt = current_max
        max_loss_time_min_rtt = df[df[col] == current_max]['timestep'].values[0]
        max_loss_path_min_rtt = col.replace('_loss', '')

avg_loss = df['total_loss'].mean()

print(f"Agents → Avg. Loss: {avg_loss:.2f}")
print(f"Max Loss: {max_loss_min_rtt:.2f} at time {max_loss_time_min_rtt} on path {max_loss_path_min_rtt}")
losses.append(avg_loss)




print("avg loss for min_load with increasing number of agents")
df = pd.read_csv("results_with_loss_min_load_100_agents.csv")

loss_cols = [col for col in df.columns if col.endswith('_loss') and col != 'total_loss']

for col in loss_cols:
    current_max = df[col].max()
    if current_max > max_loss_min_load:
        max_loss_min_load = current_max
        max_loss_time_min_load = df[df[col] == current_max]['timestep'].values[0]
        max_loss_path_min_load = col.replace('_loss', '')

avg_loss = df['total_loss'].mean()

print(f"Agents → Avg. Loss: {avg_loss:.2f}")
print(f"Max Loss: {max_loss_min_load:.2f} at time {max_loss_time_min_load} on path {max_loss_path_min_load}")
losses.append(avg_loss)


