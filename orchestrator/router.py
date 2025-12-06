"""
Router module for classifying user intents.
"""
import json

class Router:
    """
    Heuristic-based router for classifying user input.
    """
    
    def classify(self, text: str) -> dict:
        """
        Classifies the input text into an intent and action type.
        
        Args:
            text: The user's input text.
            
        Returns:
            A dictionary containing 'intent', 'action_type', and 'confidence'.
        """
        text_lower = text.lower()
        
        # Action: Block Card
        if any(keyword in text_lower for keyword in ["block", "lost", "stolen", "freeze"]) and "unblock" not in text_lower:
            return {
                "intent": "action",
                "action_type": "block_card",
                "confidence": 1.0
            }
            
        # Action: Unblock Card
        if any(keyword in text_lower for keyword in ["unblock", "unlock"]):
            return {
                "intent": "action",
                "action_type": "unblock_card",
                "confidence": 1.0
            }
            
        # Action: Dispute Transaction
        if any(keyword in text_lower for keyword in ["dispute", "wrong charge", "incorrect"]):
            return {
                "intent": "action",
                "action_type": "dispute_transaction",
                "confidence": 1.0
            }
            
        # Info: Account Summary / Transactions / Rewards / Policy
        if any(keyword in text_lower for keyword in ["balance", "bill", "due", "spend", "transactions", "fees", "charges", "rewards", "points", "forex", "markup"]):
             
             action_type = None
             if "balance" in text_lower or "due" in text_lower or "bill" in text_lower:
                 action_type = "get_account_summary"
             elif "transactions" in text_lower or "spend" in text_lower:
                 action_type = "get_recent_transactions"
             elif "rewards" in text_lower or "points" in text_lower:
                 action_type = "get_rewards_summary"
             
             return {
                "intent": "info",
                "action_type": action_type,
                "confidence": 0.9
            }

        return {
            "intent": "ambiguous",
            "action_type": None,
            "confidence": 0.5
        }
