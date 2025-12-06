"""
Minimal Streamlit app for OneCard Assistant Prototype.
Uses the AssistantAgent for orchestration.
"""
import streamlit as st
import json
import time
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.agent import AssistantAgent

# Initialize Agent
if "agent" not in st.session_state:
    st.session_state["agent"] = AssistantAgent()

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
    if "pending_action" not in st.session_state:
        st.session_state["pending_action"] = None
    
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
            response = st.session_state["agent"].handle_turn(
                st.session_state["user_id"], 
                prompt, 
                st.session_state
            )
            
        # Render Assistant Message
        # Check if it's a confirmation prompt to highlight
        response_text = response["response_text"]
        
        if "Reply with the single word **YES**" in response_text:
             st.warning("⚠️ Confirmation Required")
        
        st.session_state["messages"].append({"role": "assistant", "content": response_text})
        with st.chat_message("assistant"):
            st.markdown(response_text)
            
            # Show Audit ID if present
            if response.get("tool_output") and "audit_event" in response["tool_output"]:
                audit = response["tool_output"]["audit_event"]
                st.caption(f"✅ Audit Logged: {audit.get('action')} | {audit.get('timestamp')}")

        # Debug Info
        if show_debug and response.get("debug_info"):
            st.sidebar.json(response["debug_info"])
            if response.get("tool_output"):
                st.sidebar.markdown("### Tool Output")
                st.sidebar.json(response["tool_output"])

if __name__ == "__main__":
    main()
