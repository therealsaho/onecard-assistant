"""
Mock tools implementation for OneCard Assistant.
Reads from data/mock_db.json (in-memory only) and simulates tool actions.
"""
import json
import os
import datetime
from typing import List, Dict, Optional

# Global in-memory database
MOCK_DB = {}

def _load_db():
    """Loads the mock database from disk into memory."""
    global MOCK_DB
    # robust path finding
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_path, "data", "mock_db.json")
    
    try:
        with open(db_path, "r") as f:
            MOCK_DB = json.load(f)
    except FileNotFoundError:
        # Fallback if file not found (should not happen in correct setup)
        MOCK_DB = {"user_id": "12345", "transactions": [], "card_status": "active"}

# Load DB at import time
_load_db()

def get_account_summary(user_id: str) -> dict:
    """
    Retrieves account summary.
    Precondition: Authenticated user.
    """
    if MOCK_DB.get("user_id") != user_id:
        return {"error": "User not found"}
        
    return {
        "user_id": MOCK_DB["user_id"],
        "balance": MOCK_DB.get("balance"),
        "credit_limit": MOCK_DB.get("credit_limit"),
        "available_credit": MOCK_DB.get("available_credit"),
        "due_date": MOCK_DB.get("due_date"),
        "minimum_due": MOCK_DB.get("minimum_due"),
        "card_status": MOCK_DB.get("card_status")
    }

def get_recent_transactions(user_id: str, n: int = 10) -> list:
    """
    Retrieves recent transactions.
    Precondition: Authenticated user.
    """
    if MOCK_DB.get("user_id") != user_id:
        return []
        
    transactions = MOCK_DB.get("transactions", [])
    # Sort by date desc if needed, but assuming mock data is ordered or just returning slice
    return transactions[:n]

def block_card(user_id: str, reason: str) -> dict:
    """
    Blocks the user's card.
    Precondition: Explicit 'YES' confirmation received.
    Side Effect: Updates MOCK_DB['card_status'] to 'blocked'.
    Audit: Generates audit event.
    """
    if MOCK_DB.get("user_id") != user_id:
        return {"status": "failure", "message": "User not found"}
    
    MOCK_DB["card_status"] = "blocked"
    
    return {
        "status": "success",
        "message": "Card blocked successfully",
        "block_id": f"blk_local_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
        "audit_event": {
            "timestamp": datetime.datetime.now().isoformat(),
            "user_id": user_id,
            "action": "block_card",
            "reason": reason
        }
    }

def unblock_card(user_id: str, otp: str) -> dict:
    """
    Unblocks the card if OTP is valid.
    Precondition: OTP == '123456'.
    Side Effect: Updates MOCK_DB['card_status'] to 'active'.
    """
    if MOCK_DB.get("user_id") != user_id:
        return {"status": "failure", "message": "User not found"}
        
    if otp == "123456":
        MOCK_DB["card_status"] = "active"
        return {
            "status": "success",
            "message": "Card unblocked successfully",
            "audit_event": {
                "timestamp": datetime.datetime.now().isoformat(),
                "user_id": user_id,
                "action": "unblock_card"
            }
        }
    else:
        return {
            "status": "failure",
            "message": "Invalid OTP",
            "reason": "invalid_otp"
        }

def dispute_transaction(user_id: str, tx_id: str, reason: str) -> dict:
    """
    Submits a transaction dispute.
    Side Effect: Logs dispute (mock).
    """
    if MOCK_DB.get("user_id") != user_id:
        return {"status": "failure", "message": "User not found"}
        
    return {
        "status": "submitted",
        "ticket_id": f"disp_{tx_id}_{datetime.datetime.now().strftime('%H%M')}",
        "estimated_resolution": "7 days",
        "audit_event": {
            "timestamp": datetime.datetime.now().isoformat(),
            "user_id": user_id,
            "action": "dispute_transaction",
            "tx_id": tx_id,
            "reason": reason
        }
    }

def get_rewards_summary(user_id: str) -> dict:
    """
    Retrieves rewards summary.
    """
    if MOCK_DB.get("user_id") != user_id:
        return {"error": "User not found"}
        
    return {
        "total_points": MOCK_DB.get("reward_points", 0),
        "expiring_soon": 100, # Mock value
        "redeemable_value_inr": MOCK_DB.get("reward_points", 0) / 10 # Mock conversion
    }

def execute_tool(name: str, args: dict) -> dict:
    """
    Executes a tool by name with the given arguments.
    Enforces argument validation via function_schema (if imported) or basic checks.
    """
    # Map tool names to functions
    tool_map = {
        "block_card": block_card,
        "unblock_card": unblock_card,
        "dispute_transaction": dispute_transaction,
        "get_account_summary": get_account_summary,
        "get_recent_transactions": get_recent_transactions,
        "get_rewards_summary": get_rewards_summary
    }
    
    if name not in tool_map:
        return {"error": f"Tool '{name}' not found."}
        
    func = tool_map[name]
    
    try:
        # Execute
        result = func(**args)
        return result
    except TypeError as e:
        return {"error": f"Invalid arguments for tool '{name}': {e}"}
    except Exception as e:
        return {"error": f"Tool execution failed: {e}"}
