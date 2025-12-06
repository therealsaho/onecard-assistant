"""
LLM-based Router for intent classification.
"""
import os
import json
import re
from typing import Dict, Any, Optional
from llm.gemini_client import GeminiLLMClient

ROUTER_SYSTEM_PROMPT = """
You are an intent classifier for a credit-card assistant. Given a single user utterance, return ONLY a JSON object with fields:
{"intent":"info"|"action"|"ambiguous", "action_type": <string or null>, "confidence": <0.00-1.00>}

Rules & examples (few-shot):
- "Block my card"  -> {"intent":"action","action_type":"block_card","confidence":0.98}
- "Freeze my card, it was stolen" -> {"intent":"action","action_type":"block_card","confidence":0.97}
- "Bro my card's gone, shut it down" -> {"intent":"action","action_type":"block_card","confidence":0.96}
- "Lock this card dude" -> {"intent":"action","action_type":"block_card","confidence":0.95}
- "What is the forex markup?" -> {"intent":"info","action_type":null,"confidence":0.99}
- "I want to dispute transaction t2" -> {"intent":"action","action_type":"dispute_transaction","confidence":0.98}
- "Not sure" -> {"intent":"ambiguous","action_type":null,"confidence":0.35}

Instructions:
- Map slang and paraphrases to existing action_type values (block_card, unblock_card, get_account_summary, get_recent_transactions, dispute_transaction, get_rewards_summary).
- Set confidence high when mapping is clear (>0.85).
- If the model cannot map confidently, return "ambiguous" with low confidence (~0.3).
- Output STRICT JSON only; do not include prose.

LLM call settings: temperature=0.0, max_tokens=200.

"""

class LLMRouter:
    """
    Router that uses an LLM (or heuristics) to classify user intent.
    """
    def __init__(self):
        self.use_real_llm = os.environ.get("USE_REAL_LLM_ROUTER", "false").lower() == "true"
        self.llm = GeminiLLMClient() if self.use_real_llm else None

    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classifies the input text.
        """
        if self.use_real_llm:
            return self._classify_with_llm(text)
        else:
            return self._classify_with_heuristics(text)

    def _classify_with_heuristics(self, text: str) -> Dict[str, Any]:
        """
        Legacy heuristic-based classification (Mock Mode).
        """
        # Normalize text: lowercase, replace smart quotes, remove punctuation
        text_lower = text.lower().replace("’", "'").replace("“", '"').replace("”", '"')
        text_lower = re.sub(r'[^\w\s]', '', text_lower)
        
        BLOCK_SYNONYMS = ["block", "freeze", "shut down", "shut", "lock", "disable", "kill", "freeze it", "shut it down"]
        LOST_SYNONYMS = ["lost", "gone", "stolen", "misplaced", "missing"]
        
        # Action: Block Card
        # Direct block synonyms
        if any(keyword in text_lower for keyword in BLOCK_SYNONYMS) and "unblock" not in text_lower:
            return {
                "intent": "action",
                "action_type": "block_card",
                "confidence": 0.9
            }
            
        # Lost/Stolen + implied block (if just "lost" might be ambiguous, but usually implies block in this context)
        # But user asked: if any(lost) AND any(block) -> block. 
        # Actually the user request said:
        # if any(block in text for block in BLOCK_SYNONYMS): return ...
        # if any(lost in text for lost in LOST_SYNONYMS) and any(block in text for block in BLOCK_SYNONYMS): return ...
        # Wait, the second condition is redundant if the first one covers it. 
        # Let's re-read: "Bro my card’s gone, shut it down" -> "gone" is in LOST, "shut it down" is in BLOCK.
        # So checking BLOCK_SYNONYMS covers both cases if "shut it down" is present.
        # However, if user says "I lost my card", "lost" is in LOST_SYNONYMS but not BLOCK_SYNONYMS.
        # The user's heuristic pseudo-code was:
        # if any(block...): return block
        # if any(lost...) and any(block...): return block
        # This implies "lost" alone might NOT be enough? 
        # But "I lost my card" usually means "Block it".
        # Existing code had: if any(keyword in text_lower for keyword in ["block", "lost", "stolen", "freeze"])
        # So "lost" WAS enough.
        # I will keep "lost" / "stolen" as triggers for block_card as well, to maintain existing behavior for "I lost my card".
        
        if any(keyword in text_lower for keyword in LOST_SYNONYMS):
             return {
                "intent": "action",
                "action_type": "block_card",
                "confidence": 0.9
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
        if any(keyword in text_lower for keyword in ["balance", "bill", "due", "spend", "transactions", "fees", "charges", "rewards", "points", "forex", "markup", "interest", "period", "international"]):
             
             action_type = None
             if "balance" in text_lower or "due" in text_lower or "bill" in text_lower:
                 action_type = "get_account_summary"
             elif "transactions" in text_lower or "spend" in text_lower:
                 action_type = "get_recent_transactions"
             elif ("rewards" in text_lower or "points" in text_lower):
                 # Only map to tool if it looks like a personal query
                 if "my" in text_lower or len(text.split()) <= 3:
                     action_type = "get_rewards_summary"
                 else:
                     action_type = None # Fallback to RAG for general policy questions
             
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

    def _classify_with_llm(self, text: str) -> Dict[str, Any]:
        """
        Classifies using the LLM.
        """
        try:
            response_text = self.llm.generate(ROUTER_SYSTEM_PROMPT, text)
            
            # Extract JSON from response (handle potential markdown code blocks)
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                
                # Validate schema loosely
                if "intent" in result and "confidence" in result:
                    # Normalize confidence
                    result["confidence"] = float(result["confidence"])
                    return result
            
            # If parsing fails or schema invalid
            print(f"LLM Router failed to parse response: {response_text}")
            return self._fallback_response()
            
        except Exception as e:
            print(f"LLM Router Error: {e}")
            return self._fallback_response()

    def _fallback_response(self) -> Dict[str, Any]:
        """Returns a low-confidence ambiguous response."""
        return {
            "intent": "ambiguous",
            "action_type": None,
            "confidence": 0.3
        }
