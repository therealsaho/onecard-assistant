"""
Agent module for OneCard Assistant.
Implements the main orchestration loop, confirmation enforcement, and tool execution.
"""
import os
import json
import datetime
from typing import Dict, Any, Optional

from orchestrator.router import Router
from orchestrator.rag_engine import RAGEngine
from orchestrator.prompts import (
    SYSTEM_PROMPT,
    ROUTER_PROMPT,
    CONFIRMATION_PROMPT,
    RAG_PROMPT,
)
from tools import mock_tools
from llm.gemini_client import GeminiLLMClient

class AssistantAgent:
    """
    The main agent class that handles user turns, manages state, and executes tools.
    """

    def __init__(self):
        self.router = Router()
        self.rag = RAGEngine()
        self.llm = GeminiLLMClient()
        self.allow_local_audit = os.environ.get("ALLOW_LOCAL_AUDIT", "false").lower() == "true"
        self.audit_log_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "audit_log.jsonl"
        )

    def handle_turn(self, user_id: str, user_message: str, session_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a single user turn.
        """
        debug_info = {
            "llm_mode": "GEMINI FLASH" if self.llm.real_mode else "MOCK",
            "llm_input_preview": "",
            "llm_output_preview": "",
            "confirmation_checked": False,
            "confirmation_result": None
        }
        
        # 0. Check for OTP Input
        if session_state.get("awaiting_otp"):
            return self._handle_otp(user_id, user_message, session_state, debug_info)

        # 1. Check for Pending Confirmation FIRST
        if session_state.get("pending_action"):
            debug_info["confirmation_checked"] = True
            return self._handle_confirmation(user_id, user_message, session_state, debug_info)

        # 2. Router Classification (Only if no pending action)
        classification = self.router.classify(user_message)
        debug_info["classification"] = classification
        
        intent = classification["intent"]
        action_type = classification["action_type"]
        
        # 3. Handle Intents
        if intent == "action":
            return self._handle_action_intent(user_id, classification, session_state, debug_info)
            
        elif intent == "info":
            return self._handle_info_intent(user_id, user_message, action_type, debug_info)
            
        else:
            # Ambiguous
            return {
                "response_text": "I'm not sure I understand. Could you rephrase?",
                "tool_output": None,
                "debug_info": debug_info
            }

    def _handle_confirmation(self, user_id: str, user_message: str, session_state: Dict[str, Any], debug_info: Dict[str, Any]) -> Dict[str, Any]:
        """Handles the confirmation logic for pending actions."""
        pending_action = session_state["pending_action"]
        debug_info["pending_action"] = pending_action
        
        # Strict YES check: single token, case-insensitive, no extra chars
        msg = user_message.strip()
        is_confirmed = (msg.upper() == "YES") and (len(msg.split()) == 1)
        
        if is_confirmed:
            debug_info["confirmation_result"] = "accepted"
            
            action_type = pending_action["action_type"]
            
            # OTP Gating for sensitive actions
            if action_type in ["block_card", "unblock_card"]:
                pending_action["requires_otp"] = True
                pending_action["otp_attempts"] = 0
                session_state["awaiting_otp"] = True
                
                return {
                    "response_text": "A 6-digit OTP is required to proceed with this action. Please enter the 6-digit OTP now.",
                    "tool_output": None,
                    "debug_info": debug_info
                }

            # Execute Action (Non-OTP)
            tool_func = getattr(mock_tools, action_type)
            
            # Map arguments (Mock logic)
            kwargs = {"user_id": user_id}
            if action_type == "block_card":
                kwargs["reason"] = "User Request"
            elif action_type == "unblock_card":
                kwargs["otp"] = "123456" # Magic OTP for prototype demo
            elif action_type == "dispute_transaction":
                kwargs["tx_id"] = "t1" # Mock
                kwargs["reason"] = "User Request"

            result = tool_func(**kwargs)
            
            # Log Audit
            if self.allow_local_audit and "audit_event" in result:
                self._log_audit_event(result["audit_event"])
            
            # Clear state
            session_state["pending_action"] = None
            
            # Generate Response (optionally use LLM)
            if self.llm.real_mode:
                prompt = f"The user confirmed the action '{action_type}'. The tool returned: {json.dumps(result)}. Summarize this for the user."
                response_text = self.llm.generate(SYSTEM_PROMPT, prompt)
                self._update_debug_llm(debug_info, prompt, response_text)
            else:
                response_text = f"Action confirmed. {result.get('message', 'Success')}"

            return {
                "response_text": response_text,
                "tool_output": result,
                "debug_info": debug_info
            }
        else:
            # Cancel Action - Strict confirmation failed
            debug_info["confirmation_result"] = "cancelled"
            
            # Log Audit for Cancellation
            if self.allow_local_audit:
                self._log_audit_event({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "user_id": user_id,
                    "action": pending_action["action_type"],
                    "status": "CANCELLED",
                    "reason": "User did not confirm with strict YES"
                })

            session_state["pending_action"] = None
            return {
                "response_text": "Action cancelled. You can request it again if needed.",
                "tool_output": None,
                "debug_info": debug_info
            }

    def _handle_otp(self, user_id: str, user_message: str, session_state: Dict[str, Any], debug_info: Dict[str, Any]) -> Dict[str, Any]:
        """Handles OTP verification."""
        pending_action = session_state["pending_action"]
        otp_msg = user_message.strip()
        
        # Validate OTP
        is_valid = otp_msg.isdigit() and len(otp_msg) == 6 and otp_msg == "123456"
        
        if is_valid:
            # Execute Action
            action_type = pending_action["action_type"]
            tool_func = getattr(mock_tools, action_type)
            
            # Map arguments
            kwargs = {"user_id": user_id}
            if action_type == "block_card":
                kwargs["reason"] = "User Request"
            elif action_type == "unblock_card":
                kwargs["otp"] = "123456"
                
            result = tool_func(**kwargs)
            
            # Add OTP metadata to audit
            if "audit_event" in result:
                result["audit_event"]["otp_verified"] = True
                result["audit_event"]["otp_attempts"] = pending_action["otp_attempts"]
                if self.allow_local_audit:
                    self._log_audit_event(result["audit_event"])
            
            # Clear state
            session_state["pending_action"] = None
            session_state["awaiting_otp"] = False
            
            return {
                "response_text": f"OTP Verified. {result.get('message', 'Success')}",
                "tool_output": result,
                "debug_info": debug_info
            }
        else:
            # Invalid OTP
            pending_action["otp_attempts"] += 1
            attempts = pending_action["otp_attempts"]
            
            if attempts >= 3:
                # Cancel Action
                if self.allow_local_audit:
                    self._log_audit_event({
                        "timestamp": datetime.datetime.now().isoformat(),
                        "user_id": user_id,
                        "action": pending_action["action_type"],
                        "status": "CANCELLED",
                        "reason": "too_many_otp_attempts",
                        "otp_verified": False,
                        "otp_attempts": attempts
                    })
                
                session_state["pending_action"] = None
                session_state["awaiting_otp"] = False
                
                return {
                    "response_text": "OTP verification failed. The action has been cancelled for your safety. Please contact support at 1800-XXX-XXXX to re-initiate.",
                    "tool_output": None,
                    "debug_info": debug_info
                }
            else:
                # Retry
                remaining = 3 - attempts
                return {
                    "response_text": f"Invalid OTP. Please enter the 6-digit OTP sent to your registered phone. Attempts left: {remaining}.",
                    "tool_output": None,
                    "debug_info": debug_info
                }

    def _handle_action_intent(self, user_id: str, classification: Dict[str, Any], session_state: Dict[str, Any], debug_info: Dict[str, Any]) -> Dict[str, Any]:
        """Handles action intents by initiating confirmation."""
        action_type = classification["action_type"]
        
        if action_type in ["get_account_summary", "get_recent_transactions", "get_rewards_summary"]:
             return self._handle_info_intent(user_id, "", action_type, debug_info)

        # Destructive actions require confirmation
        session_state["pending_action"] = classification
        
        # Generate Confirmation Prompt
        action_desc = action_type.replace("_", " ")
        
        if self.llm.real_mode:
            # Use LLM to generate confirmation prompt, but MUST include the strict instruction
            context = f"User wants to {action_desc} for account {user_id}. Generate a confirmation request using the exact template provided in the system prompt."
            response_text = self.llm.generate(CONFIRMATION_PROMPT, context)
            self._update_debug_llm(debug_info, context, response_text)
        else:
            # Deterministic Template
            response_text = CONFIRMATION_PROMPT.replace("[ACTION_DESCRIPTION]", action_desc).replace("[user_id]", user_id)
        
        return {
            "response_text": response_text,
            "tool_output": None,
            "debug_info": debug_info
        }

    def _handle_info_intent(self, user_id: str, user_message: str, action_type: Optional[str], debug_info: Dict[str, Any]) -> Dict[str, Any]:
        """Handles info intents (Tools or RAG)."""
        
        if action_type:
            # Read-only tool
            tool_func = getattr(mock_tools, action_type)
            result = tool_func(user_id)
            
            if self.llm.real_mode:
                prompt = f"User asked: '{user_message}'. Tool output: {json.dumps(result)}. Provide a helpful answer."
                response_text = self.llm.generate(SYSTEM_PROMPT, prompt)
                self._update_debug_llm(debug_info, prompt, response_text)
            else:
                response_text = f"Here is the information you requested:\n\n```json\n{json.dumps(result, indent=2)}\n```"
            
            return {
                "response_text": response_text,
                "tool_output": result,
                "debug_info": debug_info
            }
        else:
            # RAG Search
            results = self.rag.search(user_message)
            debug_info["rag_results"] = results
            
            if self.llm.real_mode:
                # RAG Prompt
                context_str = "\n\n".join([f"Source: {r['source']} (Line {r['line_no']})\nContent: {r['text']}" for r in results])
                prompt = RAG_PROMPT.replace("{context_chunks}", context_str).replace("{user_query}", user_message)
                response_text = self.llm.generate(SYSTEM_PROMPT, prompt) # Passing SYSTEM_PROMPT as system, and RAG prompt as user message
                self._update_debug_llm(debug_info, prompt, response_text)
            else:
                # Mock Template
                if not results:
                    response_text = "I couldn't find specific policy information regarding that in my knowledge base."
                else:
                    top_result = results[0]
                    response_text = f"{top_result['text']}\n\n(Source: {top_result['source']}, line {top_result['line_no']})"
            
            return {
                "response_text": response_text,
                "tool_output": None,
                "debug_info": debug_info
            }

    def _update_debug_llm(self, debug_info, input_text, output_text):
        debug_info["llm_input_preview"] = input_text[:100] + "..."
        debug_info["llm_output_preview"] = output_text[:100] + "..."

    def _log_audit_event(self, audit_event: Dict[str, Any]):
        """Logs audit event to local file if enabled."""
        try:
            with open(self.audit_log_path, "a") as f:
                f.write(json.dumps(audit_event) + "\n")
        except Exception as e:
            print(f"Failed to write audit log: {e}")
