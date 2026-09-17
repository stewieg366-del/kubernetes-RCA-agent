import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure required env vars are set before importing
os.environ["GEMINI_API_KEY"] = "fake-api-key"

from agent.llm_provider import GeminiModelProvider, is_transient_error

class TestGeminiModelProvider(unittest.TestCase):
    def setUp(self):
        # Override sleep to speed up tests
        self.sleep_patcher = patch('time.sleep', return_value=None)
        self.sleep_patcher.start()
        
    def tearDown(self):
        self.sleep_patcher.stop()

    @patch('agent.llm_provider.ChatGoogleGenerativeAI')
    def test_a_primary_succeeds(self, mock_chat_cls):
        mock_primary = MagicMock()
        mock_fallback = MagicMock()
        mock_chat_cls.side_effect = [mock_primary, mock_fallback]
        
        mock_primary.invoke.return_value = "Success"
        
        provider = GeminiModelProvider()
        res, metadata = provider.invoke_with_fallback(["test message"])
        
        self.assertEqual(res, "Success")
        self.assertEqual(metadata["model"], "gemini-3.6-flash")
        self.assertIsNone(metadata["fallback_info"])
        mock_primary.invoke.assert_called_once()
        mock_fallback.invoke.assert_not_called()

    @patch('agent.llm_provider.ChatGoogleGenerativeAI')
    def test_b_primary_429_fallback_succeeds(self, mock_chat_cls):
        mock_primary = MagicMock()
        mock_fallback = MagicMock()
        mock_chat_cls.side_effect = [mock_primary, mock_fallback]
        
        # Primary fails with 429 constantly
        mock_primary.invoke.side_effect = Exception("HTTP 429 Too Many Requests")
        mock_fallback.invoke.return_value = "Fallback Success"
        
        provider = GeminiModelProvider()
        res, metadata = provider.invoke_with_fallback(["test message"])
        
        self.assertEqual(res, "Fallback Success")
        self.assertEqual(metadata["model"], "gemini-3.5-flash")
        self.assertIn("Fallback: gemini-3.5-flash", metadata["fallback_info"])
        self.assertIn("HTTP 429 Too Many Requests", metadata["fallback_info"])
        self.assertEqual(mock_primary.invoke.call_count, 3) # Tenacity retries
        mock_fallback.invoke.assert_called_once()

    @patch('agent.llm_provider.ChatGoogleGenerativeAI')
    def test_c_primary_503_fallback_succeeds(self, mock_chat_cls):
        mock_primary = MagicMock()
        mock_fallback = MagicMock()
        mock_chat_cls.side_effect = [mock_primary, mock_fallback]
        
        mock_primary.invoke.side_effect = Exception("HTTP 503 Service Unavailable")
        mock_fallback.invoke.return_value = "Fallback Success"
        
        provider = GeminiModelProvider()
        res, metadata = provider.invoke_with_fallback(["test message"])
        
        self.assertEqual(res, "Fallback Success")
        self.assertEqual(metadata["model"], "gemini-3.5-flash")
        self.assertIn("503", metadata["fallback_info"])
        self.assertEqual(mock_primary.invoke.call_count, 3)
        mock_fallback.invoke.assert_called_once()

    @patch('agent.llm_provider.ChatGoogleGenerativeAI')
    def test_d_both_fail_transient(self, mock_chat_cls):
        mock_primary = MagicMock()
        mock_fallback = MagicMock()
        mock_chat_cls.side_effect = [mock_primary, mock_fallback]
        
        mock_primary.invoke.side_effect = Exception("HTTP 429 Too Many Requests")
        mock_fallback.invoke.side_effect = Exception("HTTP 429 Too Many Requests")
        
        provider = GeminiModelProvider()
        with self.assertRaises(Exception) as context:
            provider.invoke_with_fallback(["test message"])
            
        self.assertIn("429", str(context.exception))
        self.assertEqual(mock_primary.invoke.call_count, 3)
        self.assertEqual(mock_fallback.invoke.call_count, 3)

    @patch('os.environ.get')
    def test_e_missing_api_key(self, mock_env_get):
        def mock_get(key, default=None):
            if key == "GEMINI_API_KEY":
                return ""
            return default
        mock_env_get.side_effect = mock_get
        
        with self.assertRaises(ValueError) as context:
            GeminiModelProvider()
        self.assertIn("GEMINI_API_KEY environment variable is missing", str(context.exception))

    @patch('agent.llm_provider.ChatGoogleGenerativeAI')
    def test_f_security_or_auth_error_no_fallback(self, mock_chat_cls):
        mock_primary = MagicMock()
        mock_fallback = MagicMock()
        mock_chat_cls.side_effect = [mock_primary, mock_fallback]
        
        mock_primary.invoke.side_effect = Exception("Auth Failure 401 Unauthorized")
        
        provider = GeminiModelProvider()
        with self.assertRaises(Exception) as context:
            provider.invoke_with_fallback(["test message"])
            
        self.assertIn("401 Unauthorized", str(context.exception))
        self.assertEqual(mock_primary.invoke.call_count, 1) # No retries for non-transient
        mock_fallback.invoke.assert_not_called() # No fallback for non-transient

    @patch('agent.llm_provider.ChatGoogleGenerativeAI')
    def test_h_api_key_redacted_in_fallback(self, mock_chat_cls):
        mock_primary = MagicMock()
        mock_fallback = MagicMock()
        mock_chat_cls.side_effect = [mock_primary, mock_fallback]
        
        mock_primary.invoke.side_effect = Exception("HTTP 429 key fake-api-key rate limited")
        mock_fallback.invoke.return_value = "Fallback Success"
        
        provider = GeminiModelProvider()
        res, metadata = provider.invoke_with_fallback(["test message"])
        
        self.assertNotIn("fake-api-key", metadata["fallback_info"])
        self.assertIn("[REDACTED_API_KEY]", metadata["fallback_info"])

if __name__ == '__main__':
    unittest.main()
