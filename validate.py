import json 


# python script to validate the json file 


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


class Path: 

    def __init__(self, path, capacity, latency, bandwith, attributes):
       self.path = path
       self.capacity = capacity 
       self.latency = latency
       self.bandwidth = bandwith 
       self.attributes = attributes 

    def save_attributes(self):
        pass

    def is_high_cost(self):
        return "high_cost" in self.attributes
    
         
        

class Agent: 
    def __init__(self, number_of_packets, cwnd, strategy, responsiveness, reset):
        self.self = self 
        self.number_of_packets = number_of_packets
        self.cwnd = cwnd 
        self.strategy = strategy 
        self.responsiveness = responsiveness
        self.reset = reset 


class Strategies: 
    def __init__(self):
        self.self = self 


class Knobs: 
    def __init__(self):
        self.self = self 



def load_topology(json):
    pass

def parse_agent():
    pass 


def parse_paths():
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
    validate_keys("topology.json")

    

if __name__ == "__main__":
    main() 
