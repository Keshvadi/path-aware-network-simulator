import unittest
import simpy
from simulation import Agent, Path, Greedy

class Test_agent_aimd(unittest.TestCase):
    def setUp(self):
        self.env = simpy.Environment()
        self.path = Path(self.env, path="path_1", capacity=1, bandwidth=100, latency=10, attributes=[])

        class testConfig:
            def __init__(self):
                self.cwnd = 1
                self.number_of_packets = 10
                self.responsiveness = 1
                self.reset = 3
        
        config = testConfig()

        self.agent = Agent(self.env, "agent_1", config, [self.path], Greedy())

    def test_on_ack_increases_cwnd(self):
        old_cwnd = self.agent.cwnd
        self.agent.in_flight = 1
        self.agent.on_ack()
        self.assertEqual(self.agent.cwnd, old_cwnd + self.agent.m)
        self.assertEqual(self.agent.in_flight, 0)
        self.assertEqual(self.agent.packet_loss_counter, 0)


    def test_on_loss_halves_cwnd(self):
        self.agent.cwnd = 8
        self.agent.in_flight = 1
        self.agent.packet_loss_counter = 0
        self.agent.r = 3

        self.agent.on_loss()

        self.assertEqual(self.agent.cwnd, 4)  # halbe cwnd
        self.assertEqual(self.agent.in_flight, 0)
        self.assertEqual(self.agent.packet_loss_counter, 1)

    def test_on_loss_reset_cwnd(self):
        self.agent.cwnd = 8
        self.agent.in_flight = 1
        self.agent.packet_loss_counter = 2
        self.agent.r = 3

        self.agent.on_loss()

        self.assertEqual(self.agent.cwnd, 1)
        self.assertEqual(self.agent.in_flight, 0)
        self.assertEqual(self.agent.packet_loss_counter, 0)



if __name__ == "__main__":
    unittest.main() 