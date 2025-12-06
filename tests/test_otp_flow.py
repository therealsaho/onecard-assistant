import pytest
from orchestrator.agent import AssistantAgent

def test_otp_happy_path():
    """Verify OTP happy path: Action -> Yes -> 123456 -> Success."""
    agent = AssistantAgent()
    session_state = {}
    user_id = "12345"
    
    # 1. Initiate Action
    agent.handle_turn(user_id, "Block my card", session_state)
    assert session_state["pending_action"]["action_type"] == "block_card"
    
    # 2. Confirm
    resp = agent.handle_turn(user_id, "YES", session_state)
    assert session_state["awaiting_otp"] is True
    assert "6-digit OTP is required" in resp["response_text"]
    
    # 3. Enter OTP
    resp = agent.handle_turn(user_id, "123456", session_state)
    assert "OTP Verified" in resp["response_text"]
    assert resp["tool_output"]["audit_event"]["otp_verified"] is True
    assert session_state.get("pending_action") is None
    assert session_state.get("awaiting_otp") is False

def test_otp_retry_then_success():
    """Verify OTP retry logic."""
    agent = AssistantAgent()
    session_state = {}
    user_id = "12345"
    
    # 1. Initiate & Confirm
    agent.handle_turn(user_id, "Block my card", session_state)
    agent.handle_turn(user_id, "YES", session_state)
    
    # 2. Invalid OTP
    resp = agent.handle_turn(user_id, "000000", session_state)
    assert "Invalid OTP" in resp["response_text"]
    assert "Attempts left: 2" in resp["response_text"]
    assert session_state["awaiting_otp"] is True
    
    # 3. Correct OTP
    resp = agent.handle_turn(user_id, "123456", session_state)
    assert "OTP Verified" in resp["response_text"]
    assert session_state.get("awaiting_otp") is False

def test_otp_max_attempts():
    """Verify max attempts cancellation."""
    agent = AssistantAgent()
    session_state = {}
    user_id = "12345"
    
    # 1. Initiate & Confirm
    agent.handle_turn(user_id, "Block my card", session_state)
    agent.handle_turn(user_id, "YES", session_state)
    
    # 2. Invalid OTP x3
    agent.handle_turn(user_id, "000000", session_state) # 2 left
    agent.handle_turn(user_id, "000000", session_state) # 1 left
    resp = agent.handle_turn(user_id, "000000", session_state) # 0 left -> Cancel
    
    assert "cancelled" in resp["response_text"]
    assert session_state.get("pending_action") is None
    assert session_state.get("awaiting_otp") is False

def test_otp_context_isolation():
    """Verify 123456 is treated as normal message if not awaiting OTP."""
    agent = AssistantAgent()
    session_state = {}
    user_id = "user_otp_iso"
    
    # Send 123456 without pending action
    resp = agent.handle_turn(user_id, "123456", session_state)
    
    # Should be routed (likely ambiguous or info, but NOT OTP verified)
    assert "OTP Verified" not in resp["response_text"]
    assert session_state.get("awaiting_otp") is None
