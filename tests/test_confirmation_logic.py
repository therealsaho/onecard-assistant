import pytest
from orchestrator.agent import AssistantAgent

def test_confirmation_accepted_strict():
    """Verify strict YES accepts confirmation."""
    agent = AssistantAgent()
    session_state = {
        "pending_action": {"action_type": "block_card", "intent": "action"}
    }
    
    # "YES" -> Accepted
    response = agent.handle_turn("user1", "YES", session_state)
    assert response["debug_info"]["confirmation_checked"] is True
    assert response["debug_info"]["confirmation_result"] == "accepted"
    assert session_state["pending_action"] is None
    assert "tool_output" in response and response["tool_output"] is not None

def test_confirmation_accepted_mixed_case():
    """Verify mixed case Yes accepts confirmation."""
    agent = AssistantAgent()
    session_state = {
        "pending_action": {"action_type": "block_card", "intent": "action"}
    }
    
    # "Yes" -> Accepted
    response = agent.handle_turn("user1", "Yes", session_state)
    assert response["debug_info"]["confirmation_checked"] is True
    assert response["debug_info"]["confirmation_result"] == "accepted"
    assert session_state["pending_action"] is None

def test_confirmation_cancelled_extra_words():
    """Verify extra words cancel confirmation."""
    agent = AssistantAgent()
    session_state = {
        "pending_action": {"action_type": "block_card", "intent": "action"}
    }
    
    # "YES please" -> Cancelled
    response = agent.handle_turn("user1", "YES please", session_state)
    assert response["debug_info"]["confirmation_checked"] is True
    assert response["debug_info"]["confirmation_result"] == "cancelled"
    assert session_state["pending_action"] is None
    assert response["tool_output"] is None

def test_confirmation_cancelled_no():
    """Verify NO cancels confirmation."""
    agent = AssistantAgent()
    session_state = {
        "pending_action": {"action_type": "block_card", "intent": "action"}
    }
    
    # "NO" -> Cancelled
    response = agent.handle_turn("user1", "NO", session_state)
    assert response["debug_info"]["confirmation_checked"] is True
    assert response["debug_info"]["confirmation_result"] == "cancelled"
    assert session_state["pending_action"] is None

def test_no_pending_action_routing():
    """Verify normal routing when no pending action."""
    agent = AssistantAgent()
    session_state = {}
    
    # "Yes" without pending action -> Router (likely ambiguous or chat)
    # But here we just check confirmation_checked is False
    response = agent.handle_turn("user1", "Hello", session_state)
    assert response["debug_info"]["confirmation_checked"] is False
    assert response["debug_info"]["confirmation_result"] is None
