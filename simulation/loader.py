
from validate import validate_keys, validate_data


# load and parse the topology from a JSON file, create classes and objects for the topology, paths, agents, strategies, and knobs


class Topology: 
    # class for the whole topology
    def __init__(self, paths, agents, strategy, knob):
        self.paths = paths
        self.agents = agents
        self.strategy = strategy
        self.knob = knob 


    def __repr__(self):
        return f"Topology(paths={len(self.paths)}, agents={len(self.agents)}, strategies={len(self.strategy)})" 


def load_topology(data, env):
    # Load the topology from the validated data
    agents = parse_agents(data, env) # parse agents from the data
    if not agents:
        raise ValueError("No agents found in the data")
    paths = parse_paths(data, env) # parse paths from the data
    if not paths:
        raise ValueError("No paths found in the data") 
    strategy = data.get("strategies", [])
    knob = Knobs(data.get("knobs", {}))
    return Topology(paths=paths, agents=agents, strategy=strategy, knob=knob)



class Path: 
    # class for the path object
    def __init__(self, env, path, capacity, latency, bandwidth, attributes):
       self.env = env 
       self.path = path
       self.capacity = capacity 
       self.latency = latency
       self.bandwidth = bandwidth 
       self.attributes = attributes 


    def __repr__(self):
        return f"Path({self.path}, cap={self.capacity}, lat={self.latency}, bw={self.bandwidth}, attr={self.attributes})"
    

    def save_attributes(self):
        pass

    def is_high_cost(self):
        return "high_cost" in self.attributes


def parse_paths(data, env):
    # Parse the paths from the data and create Path objects
    if "paths" not in data:
        raise ValueError("No paths found in the data")
    path_obj = {}
    for path_name, path_info in data["paths"].items():
        path_obj[path_name] = Path(
            env=env,
            path=path_name,
            capacity=path_info["capacity"],
            latency=path_info["latency"],
            bandwidth=path_info["bandwidth"],
            attributes=path_info["attributes"]
        )
    print ("path_obj:", path_obj)   
    return path_obj 
      
        
class AgentConfig: 
    # class for the agent configuration
    def __init__(self, number_of_packets, cwnd, strategy, responsiveness, reset):
        self.number_of_packets = number_of_packets
        self.cwnd = cwnd 
        self.strategy = strategy 
        self.responsiveness = responsiveness
        self.reset = reset 


    def __repr__(self):
        return f"Agent(packets={self.number_of_packets}, cwnd={self.cwnd}, strategy={self.strategy}, resp={self.responsiveness}, reset={self.reset})"


def parse_agents(data, env):
    agent_obj = {}
    for agent_name, agent_info in data["agents"].items():
        agent_obj[agent_name] = AgentConfig(
            number_of_packets=agent_info["number_of_packets"],
            cwnd=agent_info["cwnd"],
            strategy=agent_info["strategy"],
            responsiveness=agent_info["responsiveness"],
            reset=agent_info["reset"]
        )
    print ("agent_obj:", agent_obj)   
    return agent_obj 
      

# class for the strategy (parent class)
class Strategy: 
    def select_path(self):
        pass         

class Knobs:
    def __init__(self, knobs_dict):
        self.responsiveness = knobs_dict.get("responsiveness", {})
        self.reset = knobs_dict.get("reset", {})

    def __repr__(self):
        return f"Knobs(resp={self.responsiveness}, reset={self.reset})"




def main():
    filename = "topology.json"

    data = validate_keys(filename)

    if not data:
        print("Validation failed!")
        return
    
    if not validate_data(filename):
        print("Data validation failed")
        return 

    topology = load_topology(data)
    print(topology)
        

if __name__ == "__main__":
    main() 

