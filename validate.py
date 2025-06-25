import json 
# python script to validate the json file 

def load_data(filename):
    with open("topology.json", "r") as file: 
        return json.load(file)


# validate if the json exists and is valid json format 
def validate(filename):
   
        try:
            with open(filename, "r") as file:
                data = json.load(file) # put JSON-data to a variable
                print("Valid JSON")    # in case json is valid
                return data
        except json.decoder.JSONDecodeError:
            print("Invalid JSON")  # in case json is invalid
            return None
        except FileNotFoundError:
            print("File not found")
            return None 
        

# validate the data in the json file 
def validate_keys(filename):
    try:
        with open(filename, "r") as file:
            data = json.load(file)

        if "paths" not in data: 
            print("Error in paths")
            return False
        
        for path_name, path_info in data["paths"].items():
            for key in ["capacity", "latency", "bandwidth"]:
                if key not in path_info: 
                    print((f"Missing {key} in: {path_name}"))
                    return False
                elif not isinstance(path_info[key], int):
                    print(f"{key} in {path_name} is not an integer")
                    return False 
                
        if "attributes" not in path_info:
            print(f"Missing attributes in {path_info}")
            return False 
        elif not isinstance(path_info["attributes"], list):
            print(f"false datatype in {path_info}")
            return False 

        print("data exists & correct format")   
        return True 

    except json.decoder.JSONDecodeError:
        print("Invalid JSON")  # in case json is invalid
        return None


class Topology: 
    def __init__(self, paths, agents, strategy, knob):
        self.paths = paths
        self.agents = agents
        self.strategy = strategy
        self.knob = knob 


    def __repr__(self):
        return f"Topology(paths={len(self.paths)}, agents={len(self.agents)})" 


def load_topology(data):
    agents = parse_agents(data)
    paths = parse_paths(data)
    strategy = data.get("strategies", [])
    knob = data.get("knobs", {})
    return Topology(paths=paths, agents=agents, strategy=strategy, knob=knob)


class Path: 

    def __init__(self, path, capacity, latency, bandwidth, attributes):
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



#paths_data = data["paths"]


#create instance object of the path data
def parse_paths(data):
    path_obj = {}
    for path_name, path_info in data["paths"].items():
        path_obj[path_name] = Path(
            path=path_name,
            capacity=path_info["capacity"],
            latency=path_info["latency"],
            bandwidth=path_info["bandwidth"],
            attributes=path_info["attributes"]
        )
    print ("path_obj:", path_obj)   
    return path_obj 
      
        

class Agent: 
    def __init__(self, number_of_packets, cwnd, strategy, responsiveness, reset):
        self.number_of_packets = number_of_packets
        self.cwnd = cwnd 
        self.strategy = strategy 
        self.responsiveness = responsiveness
        self.reset = reset 

    
    def __repr__(self):
        return f"Agent(packets={self.number_of_packets}, cwnd={self.cwnd}, strategy={self.strategy}, resp={self.responsiveness}, reset={self.reset})"


def parse_agents(data):
    agent_obj = {}
    for agent_name, agent_info in data["agents"].items():
        agent_obj[agent_name] = Agent(
            number_of_packets=agent_info["number_of_packets"],
            cwnd=agent_info["cwnd"],
            strategy=agent_info["strategy"],
            responsiveness=agent_info["responsiveness"],
            reset=agent_info["reset"]
        )
    print ("agent_obj:", agent_obj)   
    return agent_obj 
      


class Strategies: 
    def __init__(self):
        pass 


class Greedy(Strategies):
    pass 

class Cautious(Strategies):
    pass

class Rule_follower(Strategies):
    pass 



class Knobs: 
    def __init__(self):
        pass

class Responsive(Knobs):
    pass

class Reset(Knobs):
    pass 



def main():
    #data = validate("topology.json")
    # if data: 
    #     for key, value in data["paths"].items():
    #         print(key, value)
    #     for key, value in (data["agents"].items()):
    #         print(key, value)
    #     print(data["strategies"])
    #     for key, value in data["knobs"].items():
    #         print(key, value)
    filename = "topology.json"

    data = load_data(filename)

    validate_keys("topology.json")

    topology = load_topology(data)
    print(topology)

    

if __name__ == "__main__":
    main() 
