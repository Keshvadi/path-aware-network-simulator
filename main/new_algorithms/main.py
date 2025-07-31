import json
import csv
import random
import os
import pandas as pd
import logging 
from collections import defaultdict

# ========================
# ======================================================
# COMPONENT 1: DATA MODELS (The Static World)
# ==============================================================================

class Path:
    """A simple data class to hold the properties of a single network path."""
    def __init__(self, path_id, capacity_mbps, base_rtt_ms, attributes=None, weight=1):
        self.id = path_id
        self.capacity_mbps = capacity_mbps
        self.base_rtt_ms = base_rtt_ms
        self.attributes = attributes if attributes is not None else []
        self.weight = weight 

    def __repr__(self):
        """Provides a developer-friendly string representation of the object."""
        return f"Path(id={self.id}, capacity={self.capacity_mbps}Mbps, rtt={self.base_rtt_ms}ms), attributes={self.attributes}, weight={self.weight})"

class Topology:
    """A container that loads and holds all Path objects from a config file."""
    def __init__(self, config_filepath):
        self.paths = []
        self.paths_by_id = {}
        self._load_from_config(config_filepath)

    def _load_from_config(self, config_filepath):
        """Loads path definitions from a JSON file."""
        print(f"Loading topology from: {config_filepath}")
        try:
            with open(config_filepath, 'r') as f:
                data = json.load(f)
                for path_data in data.get('paths', []):
                    path = Path(
                        path_id=path_data['id'],
                        capacity_mbps=path_data['capacity_mbps'],
                        base_rtt_ms=path_data['base_rtt_ms'],
                        attributes=path_data.get('attributes', []),
                        weight=path_data.get('weight', 1)
                    )
                    self.paths.append(path)
                    self.paths_by_id[path.id] = path
            print(f"Successfully loaded {len(self.paths)} paths.")
        except FileNotFoundError:
            print(f"Error: Topology file not found at {config_filepath}")
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {config_filepath}")

    def get_path_by_id(self, path_id):
        """Utility method to retrieve a path by its ID."""
        return self.paths_by_id.get(path_id)

# ==============================================================================
# COMPONENT 4: ALGORITHMS (Path Selection Logic)
# ==============================================================================

def select_min_rtt(agent, topology, path_loads):
    """Selects the path with the lowest base RTT."""
    # In a real scenario, this would be measured RTT, but we use base_rtt_ms for this simulation
    return min(topology.paths, key=lambda path: path.base_rtt_ms)

def select_min_load(agent, topology, path_loads):
    """Selects the path with the minimum current load."""
    if not path_loads:
        # Fallback if loads aren't available for some reason
        return random.choice(topology.paths)
        
    min_load_path_id = min(path_loads, key=path_loads.get)
    return topology.get_path_by_id(min_load_path_id)

def select_attribute_aware(agent, topology, path_loads):
    """Selects based on Min-RTT, but only from paths that are not 'high-cost'."""
    compliant_paths = [p for p in topology.paths if "high-cost" not in p.attributes]
    if not compliant_paths:
        # Fallback if no paths meet the criteria
        return random.choice(topology.paths)
    
    return min(compliant_paths, key=lambda path: path.base_rtt_ms)

round_robin_counter = {}

def select_round_robin(agent, topology, path_loads):
    """A simple round-robin selection strategy."""
    if agent.id not in round_robin_counter:
        round_robin_counter[agent.id] = 0
    
    # Get the current index for this agent
    index = round_robin_counter[agent.id] % len(topology.paths)
    selected_path = topology.paths[index]
    
    # Increment the counter for the next call
    round_robin_counter[agent.id] += 1
    
    return selected_path

weighted_path_cycle  = {}

wrr_state = defaultdict(lambda: {'index': 0, 'counter': 0})

def select_weighted_round_robin(agent, topology, path_loads):
    state = wrr_state[agent.id]
    index = state['index']
    counter = state['counter']

    paths = topology.paths
    if not paths:
        return None
    
    current_path = paths[index]
    weight = getattr(current_path, 'weight', 1)


    if counter < weight:
        state['counter'] += 1
        return current_path
    else:
        state['index'] = (index + 1) % len(paths)
        state['counter'] = 1
        return paths[state['index']]
    


def select_epsilon_greedy(agent, topology, path_loads, epsilon=0.1):
    
    paths  = topology.paths
    if random.random() < epsilon:
        return random.choice(topology.paths)

    best_path = min(paths, key=lambda path: path.base_rtt_ms)
    return best_path


def select_blest(agent, topology, path_loads):
    """
    Blocking Estimation-based Selection:
    Avoid using slower paths if a faster one would likely deliver the data sooner.
    """
   
    best_path = min(topology.paths, key=lambda p: p.base_rtt_ms)

    candidates = []
    for path in topology.paths:

        if path.base_rtt_ms > best_path.base_rtt_ms * 1.5:
            continue  
        candidates.append(path)

    if not candidates:
        return best_path

    if path_loads:
        candidates.sort(key=lambda p: path_loads.get(p.id, 0))
        return candidates[0]
    else:
        return random.choice(candidates)



# ==============================================================================
# COMPONENT 2: THE AGENT (The Dynamic Players)
# ==============================================================================

class Agent:
    """Represents a single, independent data flow with its own state and logic."""
    def __init__(self, agent_id, initial_path, strategy_func):
        self.id = agent_id
        self.current_path = initial_path
        # Start with a small, randomized congestion window
        self.cwnd = random.uniform(1.0, 5.0) 
        self.strategy_func = strategy_func
     

    def update_cwnd(self, is_congested):
        """Implements the AIMD (Additive Increase, Multiplicative Decrease) logic."""
        if is_congested:
            # Multiplicative Decrease
            self.cwnd *= 0.5
        else:
            # Additive Increase
            self.cwnd += 1.0
        
        # Ensure cwnd does not fall below a minimum value
        self.cwnd = max(1.0, self.cwnd)

    def choose_new_path(self, topology, path_loads):
        """Executes its assigned strategy to select a new path."""
        new_path = self.strategy_func(self, topology, path_loads)
        if self.current_path.id != new_path.id:
            # When an agent switches path, reset its cwnd to a base value
            # This simulates the need to learn the new path's capacity
            self.cwnd = 2.0 
        self.current_path = new_path

# ==============================================================================
# COMPONENT 3: THE SIMULATOR (The Engine)
# ==============================================================================

class Simulator:
    """Manages the overall state and progression of the simulation."""
    def __init__(self, config_filepath, num_agents, duration, strategy_name):
        self.topology = Topology(config_filepath)
        self.num_agents = num_agents
        self.duration = duration
        self.strategy_map = {
            "min_rtt": select_min_rtt,
            "min_load": select_min_load,
            "attribute_aware": select_attribute_aware,
            "round_robin": select_round_robin,
            "weighted_round_robin": select_weighted_round_robin,
            "epsilon_greedy": select_epsilon_greedy,
            "blest": select_blest
        }

        

        self.strategy_func = self.strategy_map.get(strategy_name)
        if not self.strategy_func:
            raise ValueError(f"Unknown strategy: {strategy_name}")
            
        self.agents = self._create_agents()
        self.log_data = []

    def _create_agents(self):
        """Creates all agent instances for the simulation."""
        agents = []
        for i in range(self.num_agents):
            # Assign an initial path randomly to distribute agents at the start
            initial_path = random.choice(self.topology.paths)
            agent = Agent(agent_id=i, initial_path=initial_path, strategy_func=self.strategy_func)
            agents.append(agent)
        return agents

    def run(self):
        """The main loop that executes for each time step."""
        print(f"\nStarting simulation with {self.num_agents} agents for {self.duration} steps...")
        
        path_loads = {path.id: 0 for path in self.topology.paths}

        for t in range(self.duration):
            # 1. Calculate path loads based on current agent cwnds
            current_path_loads = {path.id: 0 for path in self.topology.paths}
            for agent in self.agents:
                current_path_loads[agent.current_path.id] += agent.cwnd
            
            # 2. Determine which paths are congested
            congested_paths = set()
            path_loss = {}

            for path in self.topology.paths:
                if current_path_loads[path.id] > path.capacity_mbps:
                    congested_paths.add(path.id)
                    loss = current_path_loads[path.id] - path.capacity_mbps
                else:
                    loss = 0.0
                path_loss[path.id] = round(loss, 2) 

            # 3. Update agent CWNDs based on congestion and choose new paths for the *next* step
            for agent in self.agents:
                is_congested = agent.current_path.id in congested_paths
                agent.update_cwnd(is_congested)
                agent.choose_new_path(self.topology, current_path_loads)
            
            # 4. Log the state of the system for the current time step `t`
            log_entry = {
                'timestep': t,
                'total_throughput': sum(agent.cwnd for agent in self.agents)
            }
            # Log individual agent data
            for agent in self.agents:
                log_entry[f'agent_{agent.id}_path'] = agent.current_path.id
                log_entry[f'agent_{agent.id}_cwnd'] = round(agent.cwnd, 2)
            # Log path load data
            for path_id, load in current_path_loads.items():
                log_entry[f'{path_id}_load'] = round(load, 2)
            
            # log loss data
            for path_id, loss in path_loss.items():
                log_entry[f'{path_id}_loss'] = loss
            log_entry['total_loss'] = round(sum(path_loss.values()),2)


            self.log_data.append(log_entry)

        print(f"t={t}: loads={current_path_loads}, capacity={[p.capacity_mbps for p in self.topology.paths]}, loss={path_loss}")



        print("Simulation finished.")

    def save_results(self, output_filepath="results_experiment1_min_rtt_150_agents.csv"):
        """Writes the logged data to a CSV file."""
        if not self.log_data:
            print("No data to save.")
            return

        print(f"Saving results to {output_filepath}...")
        # The header is dynamic to accommodate any number of agents and paths
        header = self.log_data[0].keys()
        
        with open(output_filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            writer.writerows(self.log_data)
        print("Results saved.")

# ==============================================================================
# MAIN EXECUTION BLOCK
# ==============================================================================

def create_topology_file(filepath="topology.json"):
    """A helper function to create the JSON config file."""
    topo_data = {
      "paths": [
        {
          "id": "path_1",
          "capacity_mbps": 100,
          "weight": 100,
          "base_rtt_ms": 50,
          "attributes": []
        },
        {
          "id": "path_2",
          "capacity_mbps": 200,
          "weight": 200,
          "base_rtt_ms": 100,
          "attributes": []
        },
        {
          "id": "path_3",
          "capacity_mbps": 80,
          "weight": 80,
          "base_rtt_ms": 50,
          "attributes": ["high-cost"]
        }
      ]
    }
    with open(filepath, 'w') as f:
        json.dump(topo_data, f, indent=2)


RESULT_DIR = "results"
os.makedirs(RESULT_DIR, exist_ok=True)



def create_meta_file(result_filename, strategy, num_agents, config_file, duration, experiment):
    """Creates a .meta.json file containing metadata for the simulation."""
    meta = {
        "strategy": strategy,
        "agents": num_agents,
        "topology": config_file,
        "duration": duration,
        "experiment": experiment
    }

    with open(result_filename.replace(".csv", ".meta.json"), "w") as f:
        json.dump(meta, f, indent=2)




def compute_fairness(load_df):
    loads = load_df.sum(axis=1) 
    numerator = (loads.sum()) ** 2
    denominator = len(loads) * (loads ** 2).sum()
    if denominator == 0:
        return 0
    return numerator / denominator


def compute_efficiency(df):
    if 'total_throughput' in df.columns:
        return df['total_throughput'].mean()
    elif 'total_rate' in df.columns:
        return df['total_rate'].mean()
    return 0






if __name__ == "__main__":
    # --- Simulation Parameters ---
    CONFIG_FILE = "topology.json"
    SIMULATION_DURATION = 300
    AGENT_COUNTS = [10, 25, 50, 100, 150, 250, 500]
    STRATEGIES = ["min_rtt", "min_load", "attribute_aware", "round_robin", "weighted_round_robin", "epsilon_greedy", "blest"]
 

        # Logging config
    
    logging.basicConfig(
        filename=os.path.join(RESULT_DIR, "experiment_new_algorithms_log.txt"),
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

 

    create_topology_file(CONFIG_FILE)

    logging.info("=== Starting all simulations ===")


  
    for strategy in STRATEGIES:
        for num_agents in AGENT_COUNTS:
            print(f"\nRunning: {strategy} with {num_agents} agents")

            sim = Simulator(
                config_filepath=CONFIG_FILE,
                num_agents=num_agents,
                duration=SIMULATION_DURATION,
                strategy_name=strategy
            )
            sim.run()

            result_filename = os.path.join(RESULT_DIR, f"results_experiment_new_algorithms_{strategy}_{num_agents}_agents.csv")
            
            sim.save_results(output_filepath=result_filename)

            create_meta_file(
                result_filename=result_filename,
                strategy=strategy,
                num_agents=num_agents,
                config_file=CONFIG_FILE,
                duration=SIMULATION_DURATION,
                experiment="experiment_new_algorithms"
            )



            df = pd.read_csv(result_filename)


    # Oscillation and Loss summary
    logging.info("\n=== Oscillation and Loss Comparison Summary ===")
    for strategy in STRATEGIES:
        for num_agents in AGENT_COUNTS:
            try:
                df = pd.read_csv(f"results_experiment_new_algorithms_{strategy}_{num_agents}_agents.csv")
                path_cols = [col for col in df.columns if col.endswith('_load')]

                # Oszillation berechnen
                osc = df[path_cols].std().mean()
                loss = df['total_loss'].mean()




                fairness = compute_fairness(df[path_cols])
                efficiency = compute_efficiency(df)
                stability = 1 / (1 + osc)  
                loss_avoidance = 1 / (1 + loss)  

                msg = (
                    f"{strategy.upper()} with {num_agents} agents "
                    f"Osc: {osc:.2f}, Loss: {loss:.2f} Mbps, "
                    f"Fairness: {fairness:.2f}, Efficiency: {efficiency:.2f}, "
                    f"Stability: {stability:.2f}, LossAvoid: {loss_avoidance:.2f}"
                )

                logging.info(msg)
                print(msg)

            except FileNotFoundError:
                logging.warning(f"Missing file for {strategy}, {num_agents} agents")

    os.remove(CONFIG_FILE)
    logging.info("All simulations completed. Topology file removed.\n")



        # Write summary CSV for all strategies
    summary_rows = []

    for strategy in STRATEGIES:
        for num_agents in AGENT_COUNTS:
            try:
                result_path = os.path.join(RESULT_DIR, f"results_experiment_new_algorithms_{strategy}_{num_agents}_agents.csv")
                df = pd.read_csv(result_path)
                path_cols = [col for col in df.columns if col.endswith('_load')]

                osc = df[path_cols].std().mean()
                loss = df['total_loss'].mean()

                fairness = compute_fairness(df[path_cols])
                efficiency = compute_efficiency(df)
                stability = 1 / (1 + osc) 
                # the higher the oscillation, the lower the stability
                #formula maps high oscillation to low stability scores and keeps values between 0 and 1
                loss_avoidance = 1 / (1 + loss)  
                # penalizes high loss values, if loss is 0 the score is 1 (best)
                # if loss increases, score decreases --> reflects worse performance

                summary_rows.append({
                    "strategy": strategy,
                    "agents": num_agents,
                    "oscillation": round(osc, 4),
                    "loss": round(loss, 4),
                    "fairness": round(fairness, 4),
                    "efficiency": round(efficiency, 4),
                    "stability": round(stability, 4),
                    "loss_avoidance": round(loss_avoidance, 4)
                })

            except Exception as e:
                logging.warning(f"Could not compute summary for {strategy}, {num_agents} agents: {e}")

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(os.path.join(RESULT_DIR, "experiment_new_algorithms_summary.csv"), index=False)
    logging.info("Saved experiment summary to summary CSV.")

