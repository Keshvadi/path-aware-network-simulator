import unittest
import json 
from validate import validate_keys, load_data, load_topology


class Test_json(unittest.TestCase):

    def test_valid_file(self):
        data = load_data("topology.json")
        self.assertTrue(validate_keys("topology.json"))
        topology = load_topology(data)
        self.assertIsNotNone(topology)
        self.assertGreater(len(topology.paths), 0)
        self.assertGreater(len(topology.agents), 0)

    def test_missing_file(self):
        self.assertFalse(validate_keys("non_existing_file.json"))


    def test_invalid_json_format(self):
        with open("invalid.json", "w") as f:
            f.write("{ invalid json")

        result = validate_keys("invalid.json")
        self.assertFalse(result )

    
    def test_valid_json(self):
        data = {
            "paths": {
                "path1": {
                    "capacity": 10,
                    "latency": 5,
                    "bandwidth": 100,
                    "attributes": ["high_cost"]
                }
            },
            "agents": {
                "agent1": {
                    "cwnd": 10,
                    "number_of_packets": 20,
                    "strategy": "greedy_speed_demon",
                    "responsiveness": 0.9,
                    "reset": 1
                }
            },
            "strategies": ["greedy_speed_demon"],
            "knobs": {
                "responsiveness": {"high": 0.99, "low": 0.01},
                "reset": {"hard_reset": 0.01, "soft_reset": 0.99}
            },
            "attributes": ["high_cost"]
        }

        with open("valid.json", "w") as f:
            import json
            json.dump(data, f)

        self.assertTrue(validate_keys("valid.json"))



if __name__ == "__main__":
    unittest.main() 