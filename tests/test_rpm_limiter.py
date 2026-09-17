import sys
import os
import json
import time
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.graph import build_graph
from agent import llm_provider

class CustomMockLLM:
    def __init__(self, responses, simulate_429=False):
        self.responses = responses
        self.call_count = 0
        self.simulate_429 = simulate_429
        self.throw_count = 0
        
    def invoke(self, messages):
        if self.simulate_429 and self.throw_count < 2:
            self.throw_count += 1
            raise Exception("429 ResourceExhausted: Quota exceeded")
            
        if self.call_count < len(self.responses):
            resp = self.responses[self.call_count]
        else:
            resp = self.responses[-1]
        self.call_count += 1
        
        class MockMsg:
            def __init__(self, c): self.content = c
        return MockMsg(json.dumps(resp))

class TestRpmLimiter(unittest.TestCase):
    def setUp(self):
        llm_provider.LAST_LLM_CALL_TIME = 0.0
        self.old_env = dict(os.environ)
        os.environ["MAX_ITERATIONS"] = "3"
        os.environ["MAX_TOOL_CALLS"] = "5"
        os.environ["GEMINI_MIN_CALL_INTERVAL_SECONDS"] = "12"
        os.environ["GEMINI_API_KEY"] = "fake-key"
        os.environ["USE_MOCK_LLM"] = "false"

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.old_env)

    def run_limiter_scenario(self, responses, simulate_429=False):
        mock_llm = CustomMockLLM(responses, simulate_429)
        
        sleep_calls = []
        def mock_sleep(seconds):
            sleep_calls.append(seconds)
            
        fake_time = [1000.0]
        def mock_time():
            fake_time[0] += 0.1
            return fake_time[0]
            
        with patch('time.sleep', side_effect=mock_sleep), patch('time.time', side_effect=mock_time):
            with patch('agent.llm_provider.ChatGoogleGenerativeAI', return_value=mock_llm):
                graph = build_graph()
                initial_state = {
                    "incident": "test", "status": "INVESTIGATING", "hypotheses": [],
                    "investigation_history": ["Started"], "evidence": [], "observed_facts": [],
                    "uncertainties": [], "alternative_explanations": [], "root_cause": "",
                    "confidence": 0.0, "iteration": 0, "next_action": "", "tool_calls": [],
                    "total_tool_calls": 0, "executed_tools": []
                }
                final_state = None
                for state in graph.stream(initial_state, stream_mode="values"):
                    final_state = state
        
        return final_state, sleep_calls, mock_llm

    @patch('agent.graph.TOOL_MAP')
    def test_multiple_calls_respect_interval(self, mock_tool_map):
        mock_tool_map.__contains__.return_value = True
        mock_get_pods = MagicMock()
        mock_get_pods.invoke.return_value = json.dumps({"observation": "pods"})
        mock_tool_map.__getitem__.return_value = mock_get_pods
        
        responses = [
            {"action": "INVESTIGATE", "tool_calls": [{"name": "get_pods", "args": {"namespace": "rca-demo"}}]},
            {"action": "CONCLUDE", "root_cause": "Found", "confidence": 0.9}
        ]
        final_state, sleep_calls, mock_llm = self.run_limiter_scenario(responses)
        self.assertGreater(len(sleep_calls), 0)

    @patch('agent.graph.TOOL_MAP')
    def test_tool_calls_do_not_incur_delay(self, mock_tool_map):
        mock_tool_map.__contains__.return_value = True
        mock_get_pods = MagicMock()
        mock_get_pods.invoke.return_value = json.dumps({"observation": "pods"})
        mock_tool_map.__getitem__.return_value = mock_get_pods

        responses = [
            {"action": "INVESTIGATE", "tool_calls": [{"name": "get_pods", "args": {"namespace": "rca-demo"}}]},
            {"action": "INVESTIGATE", "tool_calls": [{"name": "get_pod", "args": {"namespace": "rca-demo", "pod_name": "frontend"}}]},
            {"action": "CONCLUDE", "root_cause": "Found", "confidence": 0.9}
        ]
        final_state, sleep_calls, mock_llm = self.run_limiter_scenario(responses)
        # Should be exactly 2 rate limit sleeps between the 3 LLM calls
        self.assertEqual(len(sleep_calls), 2)

    @patch('agent.graph.TOOL_MAP')
    def test_429_retry_uses_backoff(self, mock_tool_map):
        responses = [{"action": "CONCLUDE", "root_cause": "Found", "confidence": 0.9}]
        # By patching tenacity's sleep inside run_limiter_scenario, we capture backoff sleeps too.
        final_state, sleep_calls, mock_llm = self.run_limiter_scenario(responses, simulate_429=True)
        self.assertGreater(mock_llm.throw_count, 0)
        self.assertGreater(len(sleep_calls), 0)

if __name__ == '__main__':
    unittest.main()
