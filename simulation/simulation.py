from loader import load_topology
import simpy
import random 
import json 
import os 

# def clock(env, name, tick):
#     while True:
#         print(name, env.now)
#         yield env.timeout(tick)



#simpy resource: modell resources with defined capacity --> agents need to reserve a slot 
# --> path object with 3 capa --> 3 agents can send at the same time --> 4. agent has to wait 

class Agent:


    def __init__(self, env, name, config, paths, strategy):

        self.env = env #for events
        self.name = name
        self.config = config
        self.paths = paths 
        self.strategy = strategy 

        self.cwnd = config.cwnd #["cwnd"]
        self.total_packets = config.number_of_packets #["number_of_packets"]
        self.m = config.responsiveness #["responsiveness"]
        self.r = config.reset #["reset"]

        self.packet_loss_counter = 0 
        self.in_flight = 0
        self.sent_packets = 0 

        self.action = env.process(self.run()) #starts the agents process


    #main process of the agent
    def run(self):
  
        #when packets are sent 
        while self.sent_packets < self.total_packets:
            if self.in_flight < self.cwnd: #until cwnd is full 
                path = self.strategy.select_path(self.paths)
     
                yield self.env.process(self.send_packet(path))
            else:
                yield self.env.timeout(1)
        

    def send_packet(self, path):
        self.sent_packets += 1
        self.in_flight += 1
        send_time = self.env.now 

        print(f"[t={send_time}] {self.name} sends packet via {path.path} (cwnd={self.cwnd:.2f})")

        yield self.env.timeout(path.latency)

        receive_time = self.env.now
        if random.random() < 0.9:
            self.on_ack()
        else:
            self.on_loss() 


    #succesful delievered packet
    def on_ack(self):
        self.cwnd += self.m
        self.in_flight -= 1
        self.packet_loss_counter = 0 


    #packet loss on the way
    def on_loss(self):
        self.cwnd = max(1, self.cwnd / 2) 
        self.in_flight -= 1
        self.packet_loss_counter += 1

        #to many losses --> reset r 
        if self.packet_loss_counter >= self.r:
            print(f"[t={self.env.now}] {self.name} resets CWND due to loss threshold")
            self.cwnd = 1
            self.packet_loss_counter = 0




    
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
    if strategy_name == "Greedy":
        return Greedy() 
    if strategy_name == "Cautious":
        return Cautious()
    if strategy_name == "Rule_follower":
        return Rule_follower()
    else:
        raise ValueError(f"Unknown strategy: {strategy_name}")      

    
        

# classes for the strategies - inherit from strategy


class Greedy(Strategy):
    #min RTT 
    def select_path(self, paths):
        if not paths: 
            raise ValueError("no paths available for greedy strategy")
        return min(paths, key=lambda p: p.latency)
    
class Cautious(Strategy):
    # min load
    def select_path(self, paths):
        if not paths: 
            raise ValueError("no paths available for cautious strategy")
        # active users of path 
        return min(paths, key=lambda p: len(p.resource.queue) + p.resource.count) 


class Rule_follower(Strategy):
    # attribute aware 
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



def monitor(env, agents, duration):
    for remaining in range(duration, 0, -1):
        print(f"Monitoring: {remaining} steps remaining")
        yield env.timeout(10)
    print("Monitoring finished")

def load_json(env):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "..", "data", "topology.json")

    with open(json_path, "r") as f:
        data = json.load(f)

    return load_topology(data, env)

def main():

  
    env = simpy.Environment()
    topology = load_json(env)

    # raw_paths = topology.paths 

 
    # paths = []
    # for name, info in raw_paths.items():
    #     path_obj = Path(
    #         env,
    #         path=name,
    #         capacity=info["capacity"],
    #         latency=info["latency"],
    #         bandwidth=info["bandwidth"],
    #         attributes=info["attributes"]
    
    #     )
    #     paths.append(path_obj)


    paths = list(topology.paths.values())

    agents = [] #TODO create 50 
    for name, config in topology.agents.items():
        strat_name = config.strategy
        strategy = choose_strategy(strat_name)
        agent = Agent(env, name, config, paths, strategy)
        agents.append(agent)


    env.process(monitor(env, agents, duration=10))
    env.run(until=100)








if __name__ == "__main__":
    main() 