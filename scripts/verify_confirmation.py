import os
import sys
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.agent import AssistantAgent

def run_verification():
    agent = AssistantAgent()
    session_state = {}
    user_id = "verify_user"
    
    print("--- Step 1: Block my card -> Yes (Accepted) ---")
    # 1. Initiate Action
    print("User: Block my card")
    resp = agent.handle_turn(user_id, "Block my card", session_state)
    print(f"Agent: {resp['response_text']}")
    print(f"Pending Action: {session_state.get('pending_action')}")
    
    # 2. Confirm
    print("User: Yes")
    resp = agent.handle_turn(user_id, "Yes", session_state)
    print(f"Agent: {resp['response_text']}")
    print(f"Debug: confirmation_checked={resp['debug_info'].get('confirmation_checked')}")
    print(f"Debug: confirmation_result={resp['debug_info'].get('confirmation_result')}")
    
    if resp['debug_info'].get('confirmation_result') == "accepted":
        print("PASS: Confirmation accepted.")
    else:
        print("FAIL: Confirmation NOT accepted.")
        
    print("\n--- Step 2: Block my card -> Yes please (Cancelled) ---")
    # Reset state
    session_state = {}
    
    # 1. Initiate Action
    print("User: Block my card")
    resp = agent.handle_turn(user_id, "Block my card", session_state)
    
    # 2. Invalid Confirm
    print("User: Yes please")
    resp = agent.handle_turn(user_id, "Yes please", session_state)
    print(f"Agent: {resp['response_text']}")
    print(f"Debug: confirmation_checked={resp['debug_info'].get('confirmation_checked')}")
    print(f"Debug: confirmation_result={resp['debug_info'].get('confirmation_result')}")
    
    if resp['debug_info'].get('confirmation_result') == "cancelled":
        print("PASS: Confirmation cancelled (strict check).")
    else:
        print("FAIL: Confirmation NOT cancelled.")

    print("\n--- Step 3: Yes (No Pending Action) ---")
    # Reset state
    session_state = {}
    
    print("User: Yes")
    resp = agent.handle_turn(user_id, "Yes", session_state)
    print(f"Debug: confirmation_checked={resp['debug_info'].get('confirmation_checked')}")
    
    if resp['debug_info'].get('confirmation_checked') is False:
        print("PASS: No confirmation check (routed normally).")
    else:
        print("FAIL: Confirmation checked unexpectedly.")

if __name__ == "__main__":
    run_verification()
