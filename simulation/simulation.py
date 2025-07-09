from loader import load_topology
import simpy
import random 
import json 
import os 


# Simulation of a network topology with agents that send packets over paths using different strategies.
# Agents have a congestion window (cwnd) and send packets until they reach a defined number


#simpy resource: modell resources with defined capacity --> agents need to reserve a slot 
# --> path object with 3 capa --> 3 agents can send at the same time --> 4. agent has to wait 


class Agent:
    #agent that sends packets over paths
    #has a congestion window (cwnd) and sends packets until it reaches a defined number
    def __init__(self, env, name, config, paths, strategy):

        self.env = env #SimPy environment for scheduling events
        self.name = name  #unique identifier for the agent
        self.config = config
        self.paths = paths #list of paths the agent can choose from
        #self.attributes = config.attributes #["attributes"]
        self.strategy = strategy #strategy for selecting paths

        self.cwnd = config.cwnd #congestion window size
        self.total_packets = config.number_of_packets #total number of packets to send
        self.knob = config.knob 
        self.m = config.responsiveness #["responsiveness"]
        self.r = config.reset #["reset"]

        self.packet_loss_counter = 0 
        self.in_flight = 0
        self.sent_packets = 0 

        self.action = env.process(self.run()) #start the agent's process
        print(f"Agent {self.name} initialized with CWND={self.cwnd}, total packets={self.total_packets}, m={self.m}, r={self.r}")

    
    def run(self):
        # main process of the agent
        # sending packets as long as it has not sent all packets
        print(f"[t={self.env.now}] {self.name} starts sending packets")
        while self.sent_packets < self.total_packets:
            if self.in_flight < self.cwnd: #until cwnd is full 
                path = self.strategy.select_path(self.paths)
     
                yield self.env.process(self.send_packet(path))
            else:
                yield self.env.timeout(1)
        

    def send_packet(self, path):
        # send a packet over the selected path
        self.sent_packets += 1
        self.in_flight += 1
        send_time = self.env.now 

        print(f"[t={send_time}] {self.name} sends packet via {path.path} (cwnd={self.cwnd:.2f})")

        yield self.env.timeout(path.latency)

        receive_time = self.env.now
        if random.random() < 0.9:
            self.on_ack() #packet successfully delivered
            print(f"[t={receive_time}] {self.name} received ACK for packet via {path.path} (cwnd={self.cwnd:.2f})")
        else:
            self.on_loss() #packet lost
            print(f"[t={receive_time}] {self.name} packet lost via {path.path} (cwnd={self.cwnd:.2f})")


  
    def on_ack(self):
        # auccesful delievered packet, increase congestion window by m
        self.cwnd += self.m
        self.in_flight -= 1
        self.packet_loss_counter = 0 


    #packet loss on the way
    def on_loss(self):
        self.cwnd = max(1, self.cwnd / 2) 
        self.in_flight -= 1
        self.packet_loss_counter += 1

        #to many losses --> reset cwnd 
        if self.packet_loss_counter >= self.r:
            print(f"[t={self.env.now}] {self.name} resets CWND due to loss threshold")
            self.cwnd = 1
            self.packet_loss_counter = 0 #reset loss counter


# class for the path object
# represents a path in the network with its attributes like capacity, bandwidth, latency and resource    
class Path:
    def __init__(self, env, path, capacity, bandwidth, latency, attributes):
        self.env = env
        self.path = path
        self.capacity = capacity
        self.bandwidth = bandwidth
        self.latency = latency 
        self.attributes = attributes
        self.resource = simpy.Resource(env, capacity=self.capacity)


#class for the whole topology
class Topology: 
    def __init__(self, paths, agents, strategy, knob):
        self.paths = paths
        self.agents = agents
        self.strategy = strategy
        self.knob = knob 


    def __repr__(self):
        return f"Topology(paths={len(self.paths)}, agents={len(self.agents)}, strategies={len(self.strategy)})" 

    def save_attributes(self):
        pass

    def is_high_cost(self):
        return "high_cost" in self.attributes



        
# class for the strategy (parent class)
class Strategy: 
    def select_path(self, paths):
        pass    

 
def choose_strategy(strategy_name):
    # factory function to choose the strategy based on the name
    if not strategy_name:
        raise ValueError("Strategy name cannot be empty")
    if strategy_name == "Greedy":
        return Greedy() 
    if strategy_name == "Cautious":
        return Cautious()
    if strategy_name == "Rule_follower":
        return Rule_follower()
    else:
        raise ValueError(f"Unknown strategy: {strategy_name}")      

    
# concrete strategy implementations
# each strategy implements the select_path method to choose a path based on its own criteria

class Greedy(Strategy):
    # selects the path with the lowest latency, min latency
    def select_path(self, paths):
        if not paths: 
            raise ValueError("no paths available for greedy strategy")
        return min(paths, key=lambda p: p.latency)


class Cautious(Strategy):
    # selects the path with the least active users (queue length + count)
    def select_path(self, paths):
        if not paths: 
            raise ValueError("no paths available for cautious strategy")
        # active users of path 
        return min(paths, key=lambda p: len(p.resource.queue) + p.resource.count) 


class Rule_follower(Strategy):
    # selects the path with the lowest latency, but avoids paths with high cost
    # if no paths without high cost are available, it selects the path with the lowest latency
    def select_path(self, paths):
        if not paths: 
            raise ValueError("no paths available for rule follower strategy")
        allowed = [p for p in paths if "high_cost" not in p.attributes]
        if not allowed:
            allowed = paths
        return min(allowed, key=lambda p: p.latency) 


# class for the knobs 
class Knobs: 
    def __init__(self, knobs_dict):
        self.responsiveness = knobs_dict.get("responsiveness", {})
        self.reset = knobs_dict.get("reset", {}) 



# class for collecting data during the simulation
# logs packet send/receive times, path usage and agent statistics
class DataCollector:
    def __init__(self):
        self.packet_logs = []
        self.path_usage = {}
        self.agent_stats = {}


    def log_packet(self, agent_name, path_name, send_time, receive_time):
        self.packet_logs.append({
            "agent": agent_name,
            "path": path_name,
            "send": send_time,
            "receive": receive_time,
            "delay": receive_time - send_time
        })



    def log_path_usage(self, path_name):
        self.path_usage[path_name] = self.path_usage.get(path_name, 0) + 1

    def finalize(self):
        pass


# Function to monitor the simulation environment
# This function runs for a specified duration and can be used to log statistics or perform checks
def monitor(env, agents, duration):
    for remaining in range(duration, 0, -1):
        print(f"Monitoring: {remaining} steps remaining")
        yield env.timeout(10)
    print("Monitoring finished")



def load_json(env):
    # Load the topology from a JSON file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "..", "data", "topology.json")

    with open(json_path, "r") as f:
        data = json.load(f)

    return load_topology(data, env)



def main():
    # Main function to run the simulation
    env = simpy.Environment() # Create a SimPy environment for scheduling events
    print("Starting simulation...")
    topology = load_json(env)

    print(f"Loaded topology: {topology}")

    # Create paths from the topology data
    paths = list(topology.paths.values())

    # Create agents based on the topology configuration
    agents = [] 
    for name, config in topology.agents.items():
        strat_name = config.strategy
        strategy = choose_strategy(strat_name)
        agent = Agent(env, name, config, paths, strategy)
        agents.append(agent)


    # Start the monitoring process
    env.process(monitor(env, agents, duration=10))
    env.run(until=100)








if __name__ == "__main__":
    main() 