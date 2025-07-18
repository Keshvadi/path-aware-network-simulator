import json
import csv
import random
import os

# ==============================================================================
# COMPONENT 1: DATA MODELS (The Static World)
# ==============================================================================

class Path:
    """A simple data class to hold the properties of a single network path."""
    def __init__(self, path_id, capacity_mbps, base_rtt_ms, attributes=None):
        self.id = path_id
        self.capacity_mbps = capacity_mbps
        self.base_rtt_ms = base_rtt_ms
        self.attributes = attributes if attributes is not None else []

    def __repr__(self):
        """Provides a developer-friendly string representation of the object."""
        return f"Path(id={self.id}, capacity={self.capacity_mbps}Mbps, rtt={self.base_rtt_ms}ms)"

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
                        attributes=path_data.get('attributes', [])
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
            "attribute_aware": select_attribute_aware
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

    def save_results(self, output_filepath="results_with_loss_min_load_100_agents.csv"):
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
          "base_rtt_ms": 50,
          "attributes": []
        },
        {
          "id": "path_2",
          "capacity_mbps": 200,
          "base_rtt_ms": 100,
          "attributes": []
        },
        {
          "id": "path_3",
          "capacity_mbps": 80,
          "base_rtt_ms": 50,
          "attributes": ["high-cost"]
        }
      ]
    }
    with open(filepath, 'w') as f:
        json.dump(topo_data, f, indent=2)

if __name__ == "__main__":
    # --- Simulation Parameters ---
    CONFIG_FILE = "topology.json"
    NUM_AGENTS = 100
    SIMULATION_DURATION = 300
    # Change this to "min_load" "min_rtt" or "attribute_aware" to test other strategies
    STRATEGY =  "min_load" #"attribute_aware" #"min_rtt" #"min_load" 
    
    
     # 1. Create the config file for the simulation
    create_topology_file(CONFIG_FILE)

    # 2. Initialize and run the simulator
    sim = Simulator(
        config_filepath=CONFIG_FILE,
        num_agents=NUM_AGENTS,
        duration=SIMULATION_DURATION,
        strategy_name=STRATEGY
    )
    sim.run()

    # 3. Save the results to a CSV file
    sim.save_results()

    # 4. Print a small part of the results to the console for immediate feedback
    print("\n--- Sample of Results (first 5 rows of results.csv) ---")
    with open("results_with_loss_min_load_100_agents.csv", 'r') as f:
        for i, line in enumerate(f):
            if i > 5:
                break
            # Print a truncated line to keep the output clean
            print(line.strip()[:150])

    # Clean up the created topology file
    os.remove(CONFIG_FILE)

