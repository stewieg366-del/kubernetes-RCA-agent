import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.graph import build_graph

class MockLLM:
    def __init__(self, responses):
        self.responses = responses
        self.call_count = 0
        
    def invoke(self, messages):
        if self.call_count < len(self.responses):
            resp = self.responses[self.call_count]
        else:
            resp = self.responses[-1]
        self.call_count += 1
        class MockMsg:
            def __init__(self, c): self.content = c
        import json
        return MockMsg(json.dumps(resp))

class TestOOMPrioritization(unittest.TestCase):
    @patch("agent.graph.TOOL_MAP")
    @patch("agent.graph.GeminiModelProvider")
    def test_oom_killed_generalization(self, mock_provider_class, mock_tool_map):
        # 1. Mock the tools to simulate a noisy environment
        mock_get_pods = MagicMock()
        mock_get_pods.invoke.return_value = json.dumps({
            "observation": "Pods in rca-demo:\n - noisy-app-1 (Running, 0 restarts, SandboxChanged events)\n - target-worker-app (CrashLoopBackOff, 5 restarts)"
        })
        
        mock_get_container_status = MagicMock()
        mock_get_container_status.invoke.return_value = json.dumps({
            "observation": "Container target-worker-app status: lastState.terminated.reason=OOMKilled, exitCode=137."
        })
        
        mock_tool_map.__contains__.side_effect = lambda name: name in ["get_pods", "get_container_status"]
        mock_tool_map.__getitem__.side_effect = lambda name: {
            "get_pods": mock_get_pods,
            "get_container_status": mock_get_container_status
        }[name]

        # 2. Mock LLM to follow the new heuristic
        responses = [
            {
                "action": "INVESTIGATE",
                "reasoning": "Incident mentions crashes. Surveying all pods for restarts instead of anchoring on noisy-app-1.",
                "tool_calls": [{"name": "get_pods", "args": {"namespace": "rca-demo"}}],
                "hypotheses_updates": ["Some pod is crashing"]
            },
            {
                "action": "INVESTIGATE",
                "reasoning": "Noticed target-worker-app has CrashLoopBackOff and restarts. Checking its container status directly for OOMKilled/exit 137.",
                "tool_calls": [{"name": "get_container_status", "args": {"namespace": "rca-demo", "pod_name": "target-worker-app"}}],
                "hypotheses_updates": ["target-worker-app might be OOMKilled"]
            },
            {
                "action": "CONCLUDE",
                "reasoning": "Container target-worker-app has OOMKilled and exit code 137. This is the root cause.",
                "root_cause": "target-worker-app was OOMKilled (exit code 137).",
                "confidence": 0.95
            }
        ]
        
        mock_llm = MockLLM(responses)
        mock_provider_instance = MagicMock()
        def side_effect(messages):
            return mock_llm.invoke(messages), {"model": "mock", "fallback_info": None}
        mock_provider_instance.invoke_with_fallback.side_effect = side_effect
        mock_provider_class.return_value = mock_provider_instance

        # 3. Run the graph
        graph = build_graph()
        initial_state = {
            "incident": "Pod is repeatedly crashing in rca-demo.",
            "status": "INVESTIGATING",
            "hypotheses": [],
            "investigation_history": [],
            "evidence": [],
            "observed_facts": [],
            "uncertainties": [],
            "alternative_explanations": [],
            "root_cause": "",
            "confidence": 0.0,
            "iteration": 0,
            "next_action": "",
            "tool_calls": [],
            "total_tool_calls": 0,
            "executed_tools": []
        }
        
        final_state = None
        for state in graph.stream(initial_state, stream_mode="values"):
            final_state = state
            
        self.assertEqual(final_state["status"], "ROOT_CAUSE_CONFIRMED")
        self.assertIn("OOMKilled", final_state["root_cause"])
        self.assertIn("target-worker-app", final_state["root_cause"])

if __name__ == '__main__':
    unittest.main()
