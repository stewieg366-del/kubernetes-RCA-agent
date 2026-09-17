import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from observability.kubernetes_tools import get_pods
from observability.models import Evidence

class TestEvidenceTimestamps(unittest.TestCase):
    @patch('observability.kubernetes_tools.v1.list_namespaced_pod')
    def test_timestamp_is_ist(self, mock_list_pods):
        # Mock kubernetes API response
        mock_list_pods.return_value = MagicMock(items=[])
        
        evidence = get_pods("rca-demo")
        
        # It's a pydantic model or similar that has a timestamp string
        if isinstance(evidence, Evidence):
            timestamp = evidence.timestamp
        else:
            # If it's something else, try to get it
            timestamp = evidence.get("timestamp")
            
        self.assertIsNotNone(timestamp, "Timestamp should not be None")
        self.assertIn("+05:30", timestamp, f"Timestamp must have +05:30 offset. Got: {timestamp}")
        
if __name__ == '__main__':
    unittest.main()
