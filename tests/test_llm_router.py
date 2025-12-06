import unittest
from unittest.mock import patch, MagicMock
import os
import json
from orchestrator.llm_router import LLMRouter

class TestLLMRouter(unittest.TestCase):

    def setUp(self):
        # Ensure env var is cleared before each test
        if "USE_REAL_LLM_ROUTER" in os.environ:
            del os.environ["USE_REAL_LLM_ROUTER"]

    def test_mock_mode_default(self):
        """Test that router defaults to mock mode and uses heuristics."""
        router = LLMRouter()
        self.assertFalse(router.use_real_llm)
        
        # Test heuristic classification
        result = router.classify("Block my card")
        self.assertEqual(result["intent"], "action")
        self.assertEqual(result["action_type"], "block_card")
        self.assertEqual(result["confidence"], 0.9)

        result = router.classify("What is my balance?")
        self.assertEqual(result["intent"], "info")
        self.assertEqual(result["action_type"], "get_account_summary")

    def test_mock_mode_synonyms(self):
        """Test augmented synonyms for mock router."""
        router = LLMRouter()
        
        # "Bro my card’s gone, shut it down"
        result = router.classify("Bro my card’s gone, shut it down")
        self.assertEqual(result["intent"], "action")
        self.assertEqual(result["action_type"], "block_card")
        
        # "Lock this card dude"
        result = router.classify("Lock this card dude")
        self.assertEqual(result["intent"], "action")
        self.assertEqual(result["action_type"], "block_card")
        
        # "freeze it"
        result = router.classify("freeze it")
        self.assertEqual(result["intent"], "action")
        self.assertEqual(result["action_type"], "block_card")

    @patch("orchestrator.llm_router.GeminiLLMClient")
    def test_real_mode_success(self, MockLLMClient):
        """Test real mode with valid LLM response."""
        os.environ["USE_REAL_LLM_ROUTER"] = "true"
        
        # Mock LLM response
        mock_instance = MockLLMClient.return_value
        mock_instance.generate.return_value = json.dumps({
            "intent": "action",
            "action_type": "dispute_transaction",
            "confidence": 0.95
        })
        
        router = LLMRouter()
        self.assertTrue(router.use_real_llm)
        
        result = router.classify("I want to dispute a charge")
        
        self.assertEqual(result["intent"], "action")
        self.assertEqual(result["action_type"], "dispute_transaction")
        self.assertEqual(result["confidence"], 0.95)
        
        # Verify LLM was called
        mock_instance.generate.assert_called_once()

    @patch("orchestrator.llm_router.GeminiLLMClient")
    def test_real_mode_fallback_invalid_json(self, MockLLMClient):
        """Test fallback when LLM returns invalid JSON."""
        os.environ["USE_REAL_LLM_ROUTER"] = "true"
        
        mock_instance = MockLLMClient.return_value
        mock_instance.generate.return_value = "I am not sure what you mean."
        
        router = LLMRouter()
        result = router.classify("Hello")
        
        # Should fallback to ambiguous with low confidence
        self.assertEqual(result["intent"], "ambiguous")
        self.assertEqual(result["confidence"], 0.3)

    @patch("orchestrator.llm_router.GeminiLLMClient")
    def test_real_mode_fallback_exception(self, MockLLMClient):
        """Test fallback when LLM raises exception."""
        os.environ["USE_REAL_LLM_ROUTER"] = "true"
        
        mock_instance = MockLLMClient.return_value
        mock_instance.generate.side_effect = Exception("API Error")
        
        router = LLMRouter()
        result = router.classify("Hello")
        
        self.assertEqual(result["intent"], "ambiguous")
        self.assertEqual(result["confidence"], 0.3)

if __name__ == "__main__":
    unittest.main()
