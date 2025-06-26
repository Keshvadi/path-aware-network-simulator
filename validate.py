import json 
# python script to validate the json file and load the json data

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
            return False
        except FileNotFoundError:
            print("File not found")
            return False 
        

# validate the data in the json file 
def validate_keys(filename):
    try:
        with open(filename, "r") as file:
            data = json.load(file)

        if "paths" not in data or "agents" not in data: 
            print("Error: missing paths or agents")
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
                
                
        for agent_name, agent in data["agents"].items():
            for key in ["cwnd", "number_of_packets", "strategy", "responsiveness", "reset"]:
                if key not in agent: 
                    print((f"Missing {key} in agent: {agent_name} "))
                    return False
                elif key in ["cwnd", "number_of_packets", "reset"] and not isinstance(agent[key], int):                    
                    print(f"{key} in {agent_name} is not an integer")
                    return False 
                elif key == "responsiveness" and not isinstance(agent[key], (float, int)):
                    print(f"{key} in agent {agent.get('name', '[unnamed]')} is not a float")
                    return False
  
        if "attributes" not in data:
            print("Missing attribute in Json")
        elif not isinstance(path_info["attributes"], list):
            print("Attributes not a list")
            return False 
        for attr in data["attributes"]:
            if not isinstance(attr, str):
                print(f"Attribute {attr} is wrong data format")
                return False 
    
        if "strategies" not in data:
            print("missing strategies")
        for strat in data["strategies"]:
            if not isinstance(strat, str):
                print(f"Strategies {strat} is wrong data format")
      

        if "knobs" not in data:
            print("Missing Knobs in Json")
        for knob, knob_value in data.get("knobs", {}).items():
            if not isinstance(knob_value, dict):
                print(f"Knobs {knob} is wrong data format")
                return False
            for key, value in knob_value.items():
                if not isinstance(value, (float, int)):
                    print(f"Knob value {key} in {knob} is not a number")
                    return False

        print("data exists & correct format")   
        return True 

    except json.decoder.JSONDecodeError:
        print("Invalid JSON")  # in case json is invalid
        return False
    
    except FileNotFoundError:
        print("File not found")
        return False


#class for the whole json file
class Topology: 
    def __init__(self, paths, agents, strategy, knob):
        self.paths = paths
        self.agents = agents
        self.strategy = strategy
        self.knob = knob 


    def __repr__(self):
        return f"Topology(paths={len(self.paths)}, agents={len(self.agents)}, strategies={len(self.strategy)})" 


#load topology file  & data 
def load_topology(data):
    agents = parse_agents(data)
    paths = parse_paths(data)
    strategy = data.get("strategies", [])
    knob = Knobs(data.get("knobs", {}))
    return Topology(paths=paths, agents=agents, strategy=strategy, knob=knob)



# class for the path 
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
      


class Strategy: 
    def select_path(self):
        pass         


class Greedy(Strategy):
    def select_path(self):
        pass   

class Cautious(Strategy):
    def select_path(self):
        pass  

class Rule_follower(Strategy):
    def select_path(self):
        pass   



class Knobs: 
    def __init__(self, knobs_dict):
        self.responsiveness = knobs_dict.get("responsiveness", {})
        self.reset = knobs_dict.get("reset", {}) 



def main():
    filename = "topology.json"
    data = load_data(filename)

    
    if not validate_keys("topology.json"):
        print("Validation failed!")
        return 

    topology = load_topology(data)
    print(topology)

    

if __name__ == "__main__":
    main() 
