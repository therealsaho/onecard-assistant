import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pytest
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_llm_mode():
    """
    Forces Mock Mode for LLM to ensure deterministic tests,
    regardless of local .env configuration.
    """
    # Patch the variable in gemini_client module where it is imported
    with patch("llm.gemini_client.USE_REAL_LLM", False), \
         patch("config.embedding_settings.RUN_REAL_EMBEDDINGS", False):
        yield
