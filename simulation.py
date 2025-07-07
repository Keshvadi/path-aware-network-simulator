from loader import load_topology, strategy_factory
import simpy


# def clock(env, name, tick):
#     while True:
#         print(name, env.now)
#         yield env.timeout(tick)


class Agent:
    def __init__(self,env,name):
        pass 

    def run(self):
        pass 


class Paths:
    def __init__(self):
        pass



def monitor(env, agents):
    pass 


#class for the whole topology
class Topology: 
    def __init__(self, paths, agents, strategy, knob):
        self.paths = paths
        self.agents = agents
        self.strategy = strategy
        self.knob = knob 


    def __repr__(self):
        return f"Topology(paths={len(self.paths)}, agents={len(self.agents)}, strategies={len(self.strategy)})" 

# class for the paths 
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



        
# class for the strategy (parent class)
class Strategy: 
    def select_path(self):
        pass         

# classes for the strategies - inherit from strategy
class Greedy(Strategy):
    def select_path(self):
        pass   

class Cautious(Strategy):
    def select_path(self):
        pass  

class Rule_follower(Strategy):
    def select_path(self):
        pass   



# class for the knobs 
class Knobs: 
    def __init__(self, knobs_dict):
        self.responsiveness = knobs_dict.get("responsiveness", {})
        self.reset = knobs_dict.get("reset", {}) 