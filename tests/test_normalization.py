import unittest
from agent.normalize import normalize_node, clean_fact, normalize_history
from agent.state import AgentState

class TestNormalization(unittest.TestCase):
    def test_deduplication(self):
        state = {
            "evidence": [
                {"source": "loki", "type": "log", "resource": "checkout", "observation": "Error 502"},
                {"source": "loki", "type": "log", "resource": "checkout", "observation": "Error 502"},
                {"source": "k8s", "type": "pod", "resource": "checkout", "observation": "Running"}
            ],
            "observed_facts": [
                "Frontend returned 502",
                "frontend returned 502 ",
                "Checkout pod is running"
            ]
        }
        res = normalize_node(state)
        
        self.assertEqual(len(res["evidence"]), 2)
        self.assertEqual(len(res["observed_facts"]), 2)
        self.assertIn("Frontend returned 502", res["observed_facts"])

    def test_preserve_genuine_uncertainties_and_alternatives(self):
        state = {
            "status": "ROOT_CAUSE_CONFIRMED",
            "uncertainties": ["Is DNS failing?", "Is checkout down?", "is dns failing?"],
            "alternative_explanations": ["Network partition", "network partition"]
        }
        res = normalize_node(state)
        
        # Uncertainties should be deduplicated but NOT cleared
        self.assertEqual(len(res["uncertainties"]), 2)
        self.assertIn("Is DNS failing?", res["uncertainties"])
        self.assertIn("Is checkout down?", res["uncertainties"])
        
        # Alternatives should be deduplicated but NOT blindly marked as ruled out
        self.assertEqual(len(res["alternative_explanations"]), 1)
        self.assertEqual("Network partition", res["alternative_explanations"][0])

    def test_fact_vs_inference_separation(self):
        fact1 = "frontend exit code 1 due to DNS failure"
        fact2 = "checkout pod is crashing because of OOM"
        fact3 = "payment service is missing"
        
        self.assertEqual(clean_fact(fact1), "frontend exit code 1")
        self.assertEqual(clean_fact(fact2), "checkout pod is crashing")
        self.assertEqual(clean_fact(fact3), "payment service is missing")

    def test_history_timeline_formatting(self):
        history = [
            "Iteration 1: Analyzing issue",
            "Called get_service with args {'namespace': 'rca-demo', 'service_name': 'payment'}",
            "Called get_pods with args {'namespace': 'rca-demo'}",
            "Iteration 2: Missing service",
        ]
        res = normalize_history(history)
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0], "Iteration 1: Analyzing issue")
        self.assertEqual(res[1], "Tools executed: get_service, get_pods")
        self.assertEqual(res[2], "Iteration 2: Missing service")

if __name__ == '__main__':
    unittest.main()
