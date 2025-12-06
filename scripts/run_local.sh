#!/bin/bash
# Script to run the OneCard Assistant Prototype locally.
# This runs in offline mock mode — no external APIs.

echo "Setting up environment..."
# Assuming python is available. In a real script we might create venv.
# python -m venv venv
# source venv/bin/activate

echo "Installing requirements..."
pip install -r requirements.txt

echo "Running tests..."
pytest tests/

echo "Starting Streamlit app..."
streamlit run ui/app.py
