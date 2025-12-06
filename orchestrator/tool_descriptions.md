# Tool Descriptions

## Audit Event Schema
For every action tool execution, an audit log must be generated with the following schema:
```json
{
  "timestamp": "ISO8601_STRING",
  "user_id": "STRING",
  "action": "STRING",
  "tool_output": "OBJECT"
}
```

## Tool Contracts

### `get_account_summary`
- **Description**: Retrieves the current account balance, credit limit, and payment due details.
- **Inputs**:
    - `user_id` (string): The authenticated user's ID. Example: "12345"
- **Output Schema**:
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
- **Side Effects**: None.
- **Preconditions**: Authenticated user.
- **Idempotency**: Yes.

### `get_recent_transactions`
- **Description**: Fetches the last N transactions for the user.
- **Inputs**:
    - `user_id` (string): The authenticated user's ID. Example: "12345"
    - `n` (integer, optional): Number of transactions to retrieve. Default: 10. Example: 5
- **Output Schema**:
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
- **Side Effects**: None.
- **Preconditions**: Authenticated user.
- **Idempotency**: Yes.

### `block_card`
- **Description**: Temporarily blocks the user's credit card to prevent new transactions.
- **Inputs**:
    - `user_id` (string): The authenticated user's ID. Example: "12345"
    - `reason` (string): Reason for blocking. Example: "Lost card"
- **Output Schema**:
    ```json
    {
      "status": "success",
      "message": "Card blocked successfully",
      "block_id": "blk_999"
    }
    ```
- **Side Effects**: Updates `card_status` to "blocked" in the database. Generates audit log.
- **Preconditions**: **REQUIRES EXPLICIT CONFIRMATION**. The user must have replied "YES" to a confirmation prompt immediately preceding this call.
- **Idempotency**: Yes (blocking an already blocked card succeeds with same status).

### `unblock_card`
- **Description**: Unblocks a previously blocked card using an OTP.
- **Inputs**:
    - `user_id` (string): The authenticated user's ID. Example: "12345"
    - `otp` (string): One-Time Password provided by user. Example: "123456"
- **Output Schema**:
    ```json
    {
      "status": "success",
      "message": "Card unblocked successfully"
    }
    ```
- **Side Effects**: Updates `card_status` to "active" in the database. Generates audit log.
- **Preconditions**: OTP must match the system generated OTP (Prototype: "123456").
- **Idempotency**: Yes.

### `dispute_transaction`
- **Description**: Raises a dispute for a specific transaction.
- **Inputs**:
    - `user_id` (string): The authenticated user's ID. Example: "12345"
    - `tx_id` (string): The ID of the transaction to dispute. Example: "t1"
    - `reason` (string): User's explanation for the dispute. Example: "Double charge"
- **Output Schema**:
    ```json
    {
      "status": "submitted",
      "ticket_id": "disp_001",
      "estimated_resolution": "7 days"
    }
    ```
- **Side Effects**: Creates a dispute record. Generates audit log.
- **Preconditions**: Transaction must exist and be within dispute window.
- **Idempotency**: Yes (submitting duplicate dispute returns existing ticket).

### `get_rewards_summary`
- **Description**: Retrieves the user's reward points balance and expiry details.
- **Inputs**:
    - `user_id` (string): The authenticated user's ID. Example: "12345"
- **Output Schema**:
    ```json
    {
      "total_points": 5000,
      "expiring_soon": 100,
      "redeemable_value_inr": 500
    }
    ```
- **Side Effects**: None.
- **Preconditions**: Authenticated user.
- **Idempotency**: Yes.
