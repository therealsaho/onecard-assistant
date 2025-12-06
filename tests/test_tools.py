"""
Unit tests for the Mock Tools module.
"""
import pytest
from tools import mock_tools

def test_get_account_summary():
    result = mock_tools.get_account_summary("12345")
    assert "balance" in result
    assert "credit_limit" in result
    assert result["user_id"] == "12345"

def test_get_account_summary_invalid_user():
    result = mock_tools.get_account_summary("99999")
    assert "error" in result

def test_block_card():
    # Reset mock db state if needed, but for now just run
    result = mock_tools.block_card("12345", "Test")
    assert result["status"] == "success"
    assert mock_tools.MOCK_DB["card_status"] == "blocked"

def test_unblock_card_success():
    result = mock_tools.unblock_card("12345", "123456")
    assert result["status"] == "success"
    assert mock_tools.MOCK_DB["card_status"] == "active"

def test_unblock_card_failure():
    result = mock_tools.unblock_card("12345", "000000")
    assert result["status"] == "failure"
