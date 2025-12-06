"""
End-to-end simulation tests for the agent flow.
"""
import pytest
from orchestrator.agent import AssistantAgent

def test_demo_flow_info():
    """
    Demo Flow 1: Info Query
    User: "Why is my bill high?"
    Expected: Info response (mocked or RAG).
    """
    agent = AssistantAgent()
    session_state = {}
    
    # Note: "Why is my bill high?" -> "bill" keyword -> get_account_summary
    # But get_account_summary returns JSON.
    # The agent wrapper formats this.
    
    response = agent.handle_turn("12345", "Why is my bill high?", session_state)
    assert "Here is the information you requested" in response["response_text"]
    assert response["tool_output"] is not None
    assert "balance" in response["tool_output"]

def test_demo_flow_rag():
    """
    Demo Flow 2: RAG Query
    User: "What's the forex markup?"
    Expected: RAG response with citation.
    """
    agent = AssistantAgent()
    session_state = {}
    
    response = agent.handle_turn("12345", "What's the forex markup?", session_state)
    assert "Forex markup fee: 1%" in response["response_text"]
    assert "Source: knowledge_base.txt" in response["response_text"]

def test_demo_flow_action_block():
    """
    Demo Flow 3: Action + Confirm
    User: "Block my card" -> Agent: Confirm -> User: "YES" -> Agent: Success
    """
    agent = AssistantAgent()
    session_state = {}
    
    # 1. Request
    response1 = agent.handle_turn("12345", "Block my card", session_state)
    assert "You are about to" in response1["response_text"]
    assert session_state["pending_action"]["action_type"] == "block_card"
    
    # 2. Confirm
    response2 = agent.handle_turn("12345", "YES", session_state)
    assert "Action confirmed" in response2["response_text"]
    assert response2["tool_output"]["status"] == "success"
    assert "audit_event" in response2["tool_output"]
