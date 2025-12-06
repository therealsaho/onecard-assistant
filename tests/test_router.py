"""
Unit tests for the Router module.
"""
import pytest
from orchestrator.router import Router

def test_router_classify_block_card():
    router = Router()
    result = router.classify("Block my card")
    assert result["intent"] == "action"
    assert result["action_type"] == "block_card"

def test_router_classify_unblock_card():
    router = Router()
    result = router.classify("Unblock my card")
    assert result["intent"] == "action"
    assert result["action_type"] == "unblock_card"

def test_router_classify_dispute():
    router = Router()
    result = router.classify("I want to dispute a transaction")
    assert result["intent"] == "action"
    assert result["action_type"] == "dispute_transaction"

def test_router_classify_info_balance():
    router = Router()
    result = router.classify("What is my balance?")
    assert result["intent"] == "info"
    assert result["action_type"] == "get_account_summary"

def test_router_classify_ambiguous():
    router = Router()
    result = router.classify("Hello")
    assert result["intent"] == "ambiguous"
