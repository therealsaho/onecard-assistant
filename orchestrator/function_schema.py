"""
Pydantic models for tool arguments and tool registry.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Type

class BlockCardArgs(BaseModel):
    reason: str = Field(..., description="Reason for blocking the card (e.g., 'lost', 'stolen').")

class UnblockCardArgs(BaseModel):
    otp: str = Field(..., description="6-digit OTP for verification.")

class DisputeTransactionArgs(BaseModel):
    tx_id: str = Field(..., description="Transaction ID to dispute.")
    reason: str = Field(..., description="Reason for the dispute.")

class GetAccountSummaryArgs(BaseModel):
    pass

class GetRecentTransactionsArgs(BaseModel):
    n: int = Field(10, description="Number of transactions to retrieve.")

class GetRewardsSummaryArgs(BaseModel):
    pass

# Tool Registry
TOOL_REGISTRY: Dict[str, Type[BaseModel]] = {
    "block_card": BlockCardArgs,
    "unblock_card": UnblockCardArgs,
    "dispute_transaction": DisputeTransactionArgs,
    "get_account_summary": GetAccountSummaryArgs,
    "get_recent_transactions": GetRecentTransactionsArgs,
    "get_rewards_summary": GetRewardsSummaryArgs,
}

TOOL_DESCRIPTIONS = {
    "block_card": "Block the user's card. Requires a reason.",
    "unblock_card": "Unblock the user's card. Requires a 6-digit OTP.",
    "dispute_transaction": "Dispute a transaction. Requires transaction ID and reason.",
    "get_account_summary": "Get account balance, credit limit, and due date.",
    "get_recent_transactions": "Get a list of recent transactions.",
    "get_rewards_summary": "Get rewards points summary.",
}
