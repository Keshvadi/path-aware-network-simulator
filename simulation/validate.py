import json 
# python script to validate the json file and load the json data


# load json file 
def load_data(filename):
    with open("topology.json", "r") as file: 
        return json.load(file)


# validate if the json exists and is valid json format 
def validate_keys(filename):
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
def validate_data(filename):
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
                
        # validate agents         
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


