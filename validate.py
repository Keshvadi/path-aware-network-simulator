import json 



# python script to validate the json data


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



def main():
    data = validate("topology.json")
    if data: 
        for key, value in data["paths"].items():
            print(key, value)
        for key, value in (data["agents"].items()):
            print(key, value)
        print(data["strategies"])
        for key, value in data["knobs"].items():
            print(key, value)

if __name__ == "__main__":
    main() 
