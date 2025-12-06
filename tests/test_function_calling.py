import unittest
from unittest.mock import MagicMock, patch
import json
from orchestrator.agent import AssistantAgent
from tools import mock_tools

class TestFunctionCalling(unittest.TestCase):

    def setUp(self):
        self.agent = AssistantAgent()
        # Mock router to return function calls
        self.agent.router = MagicMock()
        self.agent.llm = MagicMock()
        self.agent.llm.real_mode = False # Default to mock mode

    def test_sensitive_tool_gating(self):
        """Test that sensitive tools are gated by confirmation."""
        # Mock router classification with arguments
        self.agent.router.classify.return_value = {
            "intent": "action",
            "action_type": "block_card",
            "arguments": {"reason": "lost card"},
            "confidence": 1.0
        }
        
        session_state = {}
        response = self.agent.handle_turn("user123", "Block my card", session_state)
        
        # Should ask for confirmation
        self.assertIn("You are about to **block card**", response["response_text"])
        self.assertIsNotNone(session_state.get("pending_action"))
        self.assertEqual(session_state["pending_action"]["action_type"], "block_card")
        self.assertEqual(session_state["pending_action"]["arguments"]["reason"], "lost card")

    def test_sensitive_tool_execution_after_confirmation(self):
        """Test execution of sensitive tool after confirmation."""
        session_state = {
            "pending_action": {
                "intent": "action",
                "action_type": "block_card",
                "arguments": {"reason": "lost card"}
            }
        }
        
        # Mock execute_tool to verify it's called with correct args
        with patch("orchestrator.agent.execute_tool") as mock_execute:
            mock_execute.return_value = {"status": "success", "message": "Blocked"}
            
            # User says YES
            response = self.agent.handle_turn("user123", "YES", session_state)
            
            # Should trigger OTP flow for block_card
            self.assertIn("OTP is required", response["response_text"])
            self.assertTrue(session_state["awaiting_otp"])
            
            # Now simulate OTP entry
            response = self.agent.handle_turn("user123", "123456", session_state)
            
            # Should execute tool
            mock_execute.assert_called_with("block_card", {"user_id": "user123", "reason": "lost card", "otp": "123456"})
            self.assertIn("OTP Verified", response["response_text"])

    def test_non_sensitive_tool_immediate_execution(self):
        """Test that non-sensitive tools execute immediately."""
        self.agent.router.classify.return_value = {
            "intent": "info",
            "action_type": "get_account_summary",
            "arguments": {},
            "confidence": 1.0
        }
        
        with patch("orchestrator.agent.execute_tool") as mock_execute:
            mock_execute.return_value = {"balance": 1000}
            
            session_state = {}
            response = self.agent.handle_turn("user123", "Balance", session_state)
            
            mock_execute.assert_called_with("get_account_summary", {"user_id": "user123"})
            self.assertIn("1000", response["response_text"])

if __name__ == "__main__":
    unittest.main()
