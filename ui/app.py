"""
Minimal Streamlit app for OneCard Assistant Prototype.
Simulates the orchestrator loop using local mocks.
"""
import streamlit as st
import json
import time
import sys
import os

# Add project root to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.router import Router
from orchestrator.rag_engine import RAGEngine
from orchestrator.prompts import CONFIRMATION_PROMPT
from tools import mock_tools

# Initialize modules
router = Router()
rag = RAGEngine()

def orchestrator_simulate_turn(user_input: str, user_id: str) -> dict:
    """
    Simulates a single turn of the orchestrator.
    Returns a dictionary with 'response_text', 'tool_output', 'debug_info'.
    """
    debug_info = {}
    
    # 1. Router Classification
    classification = router.classify(user_input)
    debug_info["classification"] = classification
    
    intent = classification["intent"]
    action_type = classification["action_type"]
    
    # 2. Check for Confirmation
    # If the previous message was a confirmation request, check if this is "YES"
    if st.session_state.get("confirmation_pending"):
        pending_action = st.session_state.get("pending_action")
        if user_input.strip().upper() == "YES":
            # Execute Action
            tool_func = getattr(mock_tools, pending_action["action_type"])
            
            # Simple arg mapping for prototype
            kwargs = {"user_id": user_id}
            if pending_action["action_type"] == "block_card":
                kwargs["reason"] = "User Request"
            
            result = tool_func(**kwargs)
            
            st.session_state["confirmation_pending"] = False
            st.session_state["pending_action"] = None
            
            return {
                "response_text": f"Action confirmed. {result.get('message', 'Success')}",
                "tool_output": result,
                "debug_info": debug_info
            }
        else:
            # Cancel Action
            st.session_state["confirmation_pending"] = False
            st.session_state["pending_action"] = None
            return {
                "response_text": "Action cancelled.",
                "tool_output": None,
                "debug_info": debug_info
            }

    # 3. Handle Intents
    if intent == "action":
        if action_type == "block_card":
            # Request Confirmation
            st.session_state["confirmation_pending"] = True
            st.session_state["pending_action"] = classification
            
            # Format confirmation prompt
            prompt = CONFIRMATION_PROMPT.replace("[ACTION_DESCRIPTION]", "block your card immediately").replace("[user_id]", user_id)
            
            return {
                "response_text": prompt,
                "tool_output": None,
                "debug_info": debug_info
            }
        elif action_type == "unblock_card":
             result = mock_tools.unblock_card(user_id, "000000")
             return {
                 "response_text": f"Result: {result['message']} (Prototype: OTP handling simplified)",
                 "tool_output": result,
                 "debug_info": debug_info
             }
        elif action_type == "dispute_transaction":
             result = mock_tools.dispute_transaction(user_id, "t1", "User Request")
             return {
                 "response_text": f"Dispute submitted. Ticket: {result['ticket_id']}",
                 "tool_output": result,
                 "debug_info": debug_info
             }
        elif action_type in ["get_account_summary", "get_recent_transactions", "get_rewards_summary"]:
             # Treat as info tool
             tool_func = getattr(mock_tools, action_type)
             result = tool_func(user_id)
             return {
                 "response_text": f"Here is your requested info:\n\n```json\n{json.dumps(result, indent=2)}\n```",
                 "tool_output": result,
                 "debug_info": debug_info
             }

    elif intent == "info":
        if action_type:
             # If router identified an info tool, use it
             tool_func = getattr(mock_tools, action_type)
             result = tool_func(user_id)
             return {
                 "response_text": f"Here is your requested info:\n\n```json\n{json.dumps(result, indent=2)}\n```",
                 "tool_output": result,
                 "debug_info": debug_info
             }
        
        # RAG Search
        results = rag.search(user_input)
        debug_info["rag_results"] = results
        
        if results:
            top_result = results[0]
            response = f"{top_result['text']}\n\n(Source: {top_result['source']}, line {top_result['line_no']})"
        else:
            response = "I couldn't find specific policy information regarding that."
            
        return {
            "response_text": response,
            "tool_output": None,
            "debug_info": debug_info
        }
        
    else:
        return {
            "response_text": "I'm not sure I understand. Could you rephrase?",
            "tool_output": None,
            "debug_info": debug_info
        }

def main():
    st.set_page_config(page_title="OneCard Assistant Proto", page_icon="💳")
    
    st.title("OneCard Assistant Prototype")
    st.markdown("Mock prototype for demonstrating orchestration flows.")
    
    # Sidebar for Debug
    show_debug = st.sidebar.checkbox("Show Debug Info")
    
    # Session State Init
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = "12345"
    if "confirmation_pending" not in st.session_state:
        st.session_state["confirmation_pending"] = False
    
    # Render Chat
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # User Input
    if prompt := st.chat_input("How can I help you?"):
        # Render User Message
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Process
        with st.spinner("Processing..."):
            # Simulate latency
            time.sleep(0.5) 
            response = orchestrator_simulate_turn(prompt, st.session_state["user_id"])
            
        # Render Assistant Message
        st.session_state["messages"].append({"role": "assistant", "content": response["response_text"]})
        with st.chat_message("assistant"):
            st.markdown(response["response_text"])
            
        # Debug Info
        if show_debug and response.get("debug_info"):
            st.sidebar.json(response["debug_info"])
            if response.get("tool_output"):
                st.sidebar.markdown("### Tool Output")
                st.sidebar.json(response["tool_output"])

if __name__ == "__main__":
    main()
