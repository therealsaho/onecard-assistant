# Tools Contracts

## `get_account_summary(user_id)`
- **Input:** `user_id` (string)
- **Response:**
  ```json
  {
    "user_id": "12345",
    "balance": 15000,
    "credit_limit": 100000,
    "available_credit": 85000,
    "due_date": "2025-12-03",
    "minimum_due": 750
  }
  ```
- **Preconditions:** None.

## `get_recent_transactions(user_id, n=10)`
- **Input:** `user_id` (string), `n` (integer, default=10)
- **Response:**
  ```json
  [
    {
      "tx_id": "t1",
      "date": "2025-11-10",
      "amount": 4000,
      "merchant": "ElectroMart",
      "category": "Electronics"
    }
  ]
  ```
- **Preconditions:** None.

## `block_card(user_id, reason)`
- **Input:** `user_id` (string), `reason` (string)
- **Response:**
  ```json
  {
    "status": "success",
    "message": "Card blocked successfully",
    "block_id": "blk_999"
  }
  ```
- **Preconditions:** Agent must request and receive a one-word explicit confirmation (YES) from the authenticated user before invoking.

## `unblock_card(user_id, otp)`
- **Input:** `user_id` (string), `otp` (string)
- **Response:**
  ```json
  {
    "status": "success",
    "message": "Card unblocked successfully"
  }
  ```
- **Preconditions:** Valid OTP required.

## `dispute_transaction(user_id, tx_id, reason)`
- **Input:** `user_id` (string), `tx_id` (string), `reason` (string)
- **Response:**
  ```json
  {
    "status": "submitted",
    "ticket_id": "disp_001",
    "estimated_resolution": "7 days"
  }
  ```
- **Preconditions:** None.

## `get_rewards_summary(user_id)`
- **Input:** `user_id` (string)
- **Response:**
  ```json
  {
    "total_points": 5000,
    "expiring_soon": 100,
    "redeemable_value_inr": 500
  }
  ```
- **Preconditions:** None.
