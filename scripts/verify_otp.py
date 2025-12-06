import os
import sys
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.agent import AssistantAgent

def run_verification():
    agent = AssistantAgent()
    session_state = {}
    user_id = "12345"
    
    print("--- Step 1: Block my card -> Yes -> 123456 (Success) ---")
    # 1. Initiate
    print("User: Block my card")
    resp = agent.handle_turn(user_id, "Block my card", session_state)
    
    # 2. Confirm
    print("User: Yes")
    resp = agent.handle_turn(user_id, "Yes", session_state)
    print(f"Agent: {resp['response_text']}")
    
    if session_state.get("awaiting_otp"):
        print("PASS: Agent is awaiting OTP.")
    else:
        print("FAIL: Agent NOT awaiting OTP.")
        
    # 3. OTP
    print("User: 123456")
    resp = agent.handle_turn(user_id, "123456", session_state)
    print(f"Agent: {resp['response_text']}")
    
    if "OTP Verified" in resp['response_text'] and not session_state.get("awaiting_otp"):
        print("PASS: OTP verified and action executed.")
    else:
        print("FAIL: OTP verification failed.")

    print("\n--- Step 2: Block my card -> Yes -> 000000 -> 123456 (Retry Success) ---")
    session_state = {}
    agent.handle_turn(user_id, "Block my card", session_state)
    agent.handle_turn(user_id, "Yes", session_state)
    
    print("User: 000000")
    resp = agent.handle_turn(user_id, "000000", session_state)
    print(f"Agent: {resp['response_text']}")
    
    if "Invalid OTP" in resp['response_text']:
        print("PASS: Invalid OTP detected.")
    else:
        print("FAIL: Invalid OTP NOT detected.")
        
    print("User: 123456")
    resp = agent.handle_turn(user_id, "123456", session_state)
    if "OTP Verified" in resp['response_text']:
        print("PASS: Retry successful.")
    else:
        print("FAIL: Retry failed.")

    print("\n--- Step 3: Max Attempts ---")
    session_state = {}
    agent.handle_turn(user_id, "Block my card", session_state)
    agent.handle_turn(user_id, "Yes", session_state)
    
    agent.handle_turn(user_id, "000000", session_state)
    agent.handle_turn(user_id, "000000", session_state)
    print("User: 000000 (3rd attempt)")
    resp = agent.handle_turn(user_id, "000000", session_state)
    print(f"Agent: {resp['response_text']}")
    
    if "cancelled" in resp['response_text']:
        print("PASS: Action cancelled after max attempts.")
    else:
        print("FAIL: Action NOT cancelled.")

if __name__ == "__main__":
    run_verification()
