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
from stt.adapter import STTAdapter
from tts.adapter import TTSAdapter

# Initialize Agent and Adapters
if "agent" not in st.session_state:
    st.session_state["agent"] = AssistantAgent()
if "stt" not in st.session_state:
    st.session_state["stt"] = STTAdapter()
if "tts" not in st.session_state:
    st.session_state["tts"] = TTSAdapter()

def main():
    st.set_page_config(page_title="OneCard Assistant Proto", page_icon="💳")
    
    # Inject Fixed Mic CSS & JS
    try:
        with open("ui/static/fixed_mic.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        
        with open("ui/static/fixed_mic.js") as f:
            st.components.v1.html(f"<script>{f.read()}</script>", height=0, width=0)
    except FileNotFoundError:
        st.error("Static assets not found. Please ensure ui/static/fixed_mic.css and .js exist.")

    st.title("OneCard Assistant Prototype")
    st.markdown("Mock prototype for demonstrating orchestration flows.")
    
    # Status Indicators
    col1, col2, col3 = st.columns(3)
    
    # LLM Mode
    llm_mode = "GEMINI FLASH" if st.session_state["agent"].llm.real_mode else "MOCK"
    mode_color = "green" if st.session_state["agent"].llm.real_mode else "orange"
    col1.markdown(f"**LLM:** :{mode_color}[{llm_mode}]")
    
    # STT Mode
    stt_provider = st.session_state["stt"].provider.upper()
    stt_color = "green" if stt_provider != "MOCK" else "orange"
    col2.markdown(f"**STT:** :{stt_color}[{stt_provider}]")
    
    # TTS Mode
    tts_provider = st.session_state["tts"].provider.upper()
    tts_color = "green" if tts_provider != "MOCK" else "orange"
    col3.markdown(f"**TTS:** :{tts_color}[{tts_provider}]")
    
    # Sidebar for Debug & Settings
    show_debug = st.sidebar.checkbox("Show Debug Info")
    play_audio = st.sidebar.checkbox("Play audio replies", value=False)
    
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
            
    # Spacer to prevent overlap with fixed mic
    st.markdown("<div style='height:120px'></div>", unsafe_allow_html=True)

    # Fixed Mic Container
    st.markdown('<div class="onecard-fixed-mic-wrapper"><div class="onecard-fixed-mic"><div class="mic-row">', unsafe_allow_html=True)
    
    # Audio Input (Persistent Mic)
    if "mic_id" not in st.session_state:
        st.session_state["mic_id"] = 0
        
    mic_key = f"mic_{st.session_state['mic_id']}"
    
    # Render widget inside wrapper (visually)
    mic_audio = st.audio_input("Tap to record", key=mic_key, label_visibility="collapsed")
    
    st.markdown('</div></div></div>', unsafe_allow_html=True)
    
    if mic_audio:
        with st.spinner("Processing audio..."):
            try:
                audio_bytes = mic_audio.read()
                stt_result = st.session_state["stt"].transcribe(audio_bytes)
                user_text = stt_result["text"]
                
                # Render User Message
                st.session_state["messages"].append({"role": "user", "content": user_text})
                
                # Process
                time.sleep(0.5) 
                response = st.session_state["agent"].handle_turn(
                    st.session_state["user_id"], 
                    user_text, 
                    st.session_state
                )
                
                response_text = response["response_text"]
                st.session_state["messages"].append({"role": "assistant", "content": response_text})
                
                # Handle TTS
                if play_audio:
                    audio_path = st.session_state["tts"].synthesize(response_text)
                    if audio_path:
                        st.session_state["auto_play_audio"] = audio_path
                
                st.session_state["mic_id"] += 1
                st.rerun()
                
            except Exception as e:
                st.error(f"Error processing audio: {e}")
                user_text = None

    # Handle Autoplay after rerun
    if "auto_play_audio" in st.session_state and st.session_state["auto_play_audio"]:
        st.audio(st.session_state["auto_play_audio"], autoplay=True)
        st.session_state["auto_play_audio"] = None


    
    # Text Input (Standard)
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
        response_text = response["response_text"]
        
        if "Reply with the single word **YES**" in response_text:
             st.warning("⚠️ Confirmation Required")
        
        if st.session_state.get("awaiting_otp"):
             st.info("🔒 OTP Required: Please enter the 6-digit OTP (Hint: 123456)")
        
        st.session_state["messages"].append({"role": "assistant", "content": response_text})
        with st.chat_message("assistant"):
            st.markdown(response_text)
            
            # TTS Playback
            if play_audio:
                with st.spinner("Synthesizing speech..."):
                    audio_path = st.session_state["tts"].synthesize(response_text)
                    if audio_path:
                        st.audio(audio_path, autoplay=True)
            
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
