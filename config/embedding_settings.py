"""
Embedding RAG configuration settings.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Embedding Provider: 'mock', 'openai', 'gemini', 'sentence-transformers'
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "mock").lower()

# Run real embeddings?
RUN_REAL_EMBEDDINGS = os.getenv("RUN_REAL_EMBEDDINGS", "false").lower() == "true"

# Embedding Model Name (provider specific)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# RAG Index Directory
RAG_INDEX_DIR = os.getenv("RAG_INDEX_DIR", os.path.join("data", "rag_index"))

# Minimum Similarity Score Threshold
RAG_MIN_SCORE = float(os.getenv("RAG_MIN_SCORE", "0.25"))

# Reranker Enabled?
RERANKER_ENABLED = os.getenv("RUN_RERANKER", "false").lower() == "true"

# Index Version
INDEX_VERSION = "v1"
