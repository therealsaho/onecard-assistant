# OneCard Assistant Prototype

**Problem:** Users struggle to understand credit card fees and statements.
**Who:** OneCard users.
**Value:** Instant, accurate answers and actions via a chat interface.

## How to run

### Audio Configuration
- `STT_PROVIDER`: `mock` (default) or `Google STT (old)`
- `TTS_PROVIDER`: `mock` (default) or `gtts`

### Running
1. Install dependencies: `pip install -r requirements.txt`
2. Run the app: `python -m streamlit run ui/app.py`

## Demo Flows
1. **"What is my current balance?"** - Fetch data and display from knowledge base.
2. **"Block my card"** - Securely block the card with user confirmation.
3. **"What’s the forex markup?"** - Provide specific fee information from the knowledge base.
