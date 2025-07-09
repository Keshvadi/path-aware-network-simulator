import simpy 
from simulation import Greedy, Cautious, Rule_follower



class DummyResource:
    def __init__(self, count=0, queue=None):
        self.count = count
        self.queue = queue if queue else []



class TestPath:
    def __init__(self, env, name, latency, attributes=None):
        self.path = name 
        self.latency = latency
        self.attributes = attributes if attributes else []
        self.resource = simpy.Resource(env, capacity=10)


def test_strategy(strategy_instance, paths):
    print(f"\nTesting strategy: {strategy_instance.__class__.__name__}")
    chosen = strategy_instance.select_path(paths)
    print(f"Selected path: {chosen.path} (latency={chosen.latency}, attributes={chosen.attributes})")





if __name__ == "__main__":

    env = simpy.Environment() 

    path1 = TestPath(env, "path_1", latency=10, attributes=["low_cost"])
    path2 = TestPath(env, "path_2", latency=20, attributes=["high_cost"])
    path3 = TestPath(env, "path_3", latency=5, attributes=["high_cost"])

    #path3.resource.count = 5     
    path3.resource.queue = [1, 2] 

    test_paths = [path1, path2, path3]

    test_strategy(Greedy(), test_paths)
    test_strategy(Cautious(), test_paths)
    test_strategy(Rule_follower(), test_paths)