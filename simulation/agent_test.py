import unittest
import simpy
from simulation import Agent, Path, Greedy


## Test cases for the Agent class with AIMD strategy
# This test suite checks the behavior of the Agent class when handling acknowledgments and packet losses
class Test_agent_aimd(unittest.TestCase):
    def setUp(self):
        # Set up the simulation environment and create an Agent instance with a Greedy strategy
        self.env = simpy.Environment()
        self.path = Path(self.env, path="path_1", capacity=1, bandwidth=100, latency=10, attributes=[])


        # Define a test configuration for the Agent
        # This configuration includes parameters like cwnd, number_of_packets, responsiveness, and reset
        class testConfig:
            def __init__(self):
                self.cwnd = 1
                self.number_of_packets = 10
                self.responsiveness = 1
                self.reset = 3
        
        config = testConfig()

        self.agent = Agent(self.env, "agent_1", config, [self.path], Greedy())


    def test_on_ack_increases_cwnd(self):
        # Test that the congestion window increases by m on acknowledgment
        old_cwnd = self.agent.cwnd
        self.agent.in_flight = 1
        self.agent.on_ack() # simulate receiving an acknowledgment
        self.assertEqual(self.agent.cwnd, old_cwnd + self.agent.m) # increase cwnd by m
        self.assertEqual(self.agent.in_flight, 0)
        self.assertEqual(self.agent.packet_loss_counter, 0) 


    def test_on_loss_halves_cwnd(self):
        # Test that the congestion window is halved on packet loss
        self.agent.cwnd = 8
        self.agent.in_flight = 1
        self.agent.packet_loss_counter = 0
        self.agent.r = 3

        self.agent.on_loss()

        self.assertEqual(self.agent.cwnd, 4)  # halbe cwnd
        self.assertEqual(self.agent.in_flight, 0)
        self.assertEqual(self.agent.packet_loss_counter, 1)


    def test_on_loss_reset_cwnd(self):
        # Test that the congestion window is reset to 1 after too many losses
        # This simulates a scenario where the agent has experienced multiple packet losses
        self.agent.cwnd = 8
        self.agent.in_flight = 1
        self.agent.packet_loss_counter = 2
        self.agent.r = 3

        self.agent.on_loss()

        self.assertEqual(self.agent.cwnd, 1)
        self.assertEqual(self.agent.in_flight, 0)
        self.assertEqual(self.agent.packet_loss_counter, 0)


if __name__ == "__main__":
    unittest.main()  # Run the test cases