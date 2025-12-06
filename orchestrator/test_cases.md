# Manual Test Cases

## 1. Info Query: Account Summary
**Input:** "What's my minimum due and when?"
- **Expected Router Output:** `{"intent": "info", "action_type": "get_account_summary"}`
- **Expected Tool Call:** `get_account_summary(user_id="12345")`
- **Expected Response:** "Your minimum due is ₹750, and the due date is 2025-12-03."

## 2. RAG Policy Query: Forex Markup
**Input:** "What is OneCard’s forex markup?"
- **Expected Router Output:** `{"intent": "info", "action_type": null}`
- **Expected RAG Action:** Search `knowledge_base.txt` for "forex markup".
- **Expected Response:** "The forex markup fee is 1% on card transactions processed in currencies other than INR. (Policy source: knowledge_base.txt (line 2))"

## 3. Action + Confirm: Block Card
**Input:** "Block my card"
- **Expected Router Output:** `{"intent": "action", "action_type": "block_card"}`
- **Expected Agent Response:** "Are you sure you want to block your card? This action cannot be easily undone. Reply **YES** to confirm or any other text to cancel."
- **User Reply:** "YES"
- **Expected Tool Call:** `block_card(user_id="12345", reason="User Request")`
- **Expected Final Response:** "Card blocked successfully. Confirmation ID: blk_999"

## 4. Action Reject: Block Card
**Input:** "Block my card"
- **Expected Router Output:** `{"intent": "action", "action_type": "block_card"}`
- **Expected Agent Response:** "Are you sure you want to block your card? This action cannot be easily undone. Reply **YES** to confirm or any other text to cancel."
- **User Reply:** "NO" (or "Wait", "Cancel")
- **Expected Final Response:** "Action cancelled. Your card remains active."
- **Expected Side Effect:** `card_status` remains "active".

## 5. Dispute Transaction
**Input:** "I want to dispute transaction t2 because it’s incorrect"
- **Expected Router Output:** `{"intent": "action", "action_type": "dispute_transaction"}`
- **Expected Tool Call:** `dispute_transaction(user_id="12345", tx_id="t2", reason="incorrect")`
- **Expected Response:** "Dispute submitted. Ticket ID: disp_001. Estimated resolution: 7 days."

## 6. OTP Failure: Unblock Card
**Input:** "Unblock my card"
- **Expected Router Output:** `{"intent": "action", "action_type": "unblock_card"}`
- **Expected Agent Response:** "Please provide the OTP sent to your registered mobile number."
- **User Reply:** "000000" (Wrong OTP)
- **Expected Tool Call:** `unblock_card(user_id="12345", otp="000000")`
- **Expected Response:** "Error: Invalid OTP. Please try again."
