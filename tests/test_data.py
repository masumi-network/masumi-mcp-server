"""
Comprehensive test data for Masumi MCP Server testing.
All data is clearly marked as test/dummy data and safe for Preprod testnet use only.
"""

import os
from typing import Dict, Any
from datetime import datetime, timedelta

# Testnet safety configuration
TESTNET_CONFIG = {
    "network": "Preprod",
    "testing_mode": True,
    "mainnet_blocked": True,
    "dummy_data_only": True
}

# 1. Dummy Registered Agent Data
DUMMY_AGENTS = {
    "test_writer_agent": {
        "agentIdentifier": "masumi-test-writer-001",
        "name": "Test Content Writer Agent",
        "apiBaseUrl": "https://test-writer-agent.masumi-test.network/",
        "sellingWalletVkey": "vkey_test_writer_1234567890abcdef1234567890abcdef12345678",
        "capability": {
            "name": "Content Writing",
            "version": "1.0.0"
        },
        "pricing": {
            "basePrice": 1000000,  # 1 ADA in lovelace
            "currency": "ADA",
            "pricePerToken": 100
        },
        "metadata": {
            "description": "Test agent for content writing tasks",
            "author": "Masumi Test Team",
            "tags": ["writing", "content", "test"]
        }
    },
    "test_analyzer_agent": {
        "agentIdentifier": "masumi-test-analyzer-002", 
        "name": "Test Data Analyzer Agent",
        "apiBaseUrl": "https://test-analyzer-agent.masumi-test.network/",
        "sellingWalletVkey": "vkey_test_analyzer_abcdef1234567890abcdef1234567890abcdef12",
        "capability": {
            "name": "Data Analysis",
            "version": "2.1.0"
        },
        "pricing": {
            "basePrice": 2000000,  # 2 ADA in lovelace
            "currency": "ADA",
            "pricePerToken": 200
        },
        "metadata": {
            "description": "Test agent for data analysis tasks",
            "author": "Masumi Test Team", 
            "tags": ["analysis", "data", "test"]
        }
    }
}

# 2. Funded Test Wallet Configuration
TEST_WALLETS = {
    "buyer_wallet": {
        "address": "addr_test1qr8s7w7l9q2m3n4p5r6s7t8u9v0w1x2y3z4a5b6c7d8e9f0g1h2i3j4k5l6m7n8o9p0q1r2s3t4u5v6w7x8y9z0a1b2c3",
        "vkey": "vkey_test_buyer_fedcba0987654321fedcba0987654321fedcba09876543",
        "balance": "100000000",  # 100 ADA in lovelace
        "purpose": "For making test purchases"
    },
    "seller_wallet": {
        "address": "addr_test1qq9p0o1n2m3l4k5j6i7h8g9f0e1d2c3b4a5z6y7x8w9v0u1t2s3r4q5p6o7n8m9l0k1j2i3h4g5f6e7d8c9b0a1z2y3x4w5v6u7",
        "vkey": "vkey_test_seller_123456789abcdef123456789abcdef123456789abcdef12",
        "balance": "50000000",   # 50 ADA in lovelace
        "purpose": "For receiving test payments"
    }
}

# 3. Payment Finalization Test Data
PAYMENT_TEST_DATA = {
    "active_payment": {
        "payment_id": "test-payment-12345-abcdef-67890",
        "blockchain_identifier": "test-tx-hash-payment-abc123def456ghi789",
        "status": "pending",
        "amount": 1000000,  # 1 ADA
        "agent_identifier": "masumi-test-writer-001",
        "buyer_wallet": TEST_WALLETS["buyer_wallet"]["address"],
        "seller_wallet": TEST_WALLETS["seller_wallet"]["address"]
    },
    "finalization_payload": {
        "status": "completed",
        "transaction_hash": "test-finalization-tx-hash-def456ghi789jkl012",
        "completion_timestamp": "2024-01-15T10:30:00Z",
        "result_hash": "test-result-hash-mno345pqr678stu901"
    }
}

# 4. Purchase Refund Test Data
PURCHASE_REFUND_DATA = {
    "refundable_purchase": {
        "purchase_id": "test-purchase-67890-fedcba-12345",
        "payment_id": "test-payment-12345-abcdef-67890",
        "agent_identifier": "masumi-test-analyzer-002",
        "amount": 2000000,  # 2 ADA
        "status": "completed",
        "purchase_date": "2024-01-10T14:20:00Z"
    },
    "refund_request_payload": {
        "reason": "Service not delivered as expected",
        "refund_type": "full",
        "requested_amount": 2000000,
        "request_timestamp": "2024-01-16T09:15:00Z"
    },
    "refund_cancellation_payload": {
        "cancellation_reason": "Issue resolved by agent",
        "cancel_timestamp": "2024-01-17T11:45:00Z"
    }
}

# 5. Agent Deregistration Test Data
AGENT_DEREGISTRATION_DATA = {
    "deregisterable_agent": {
        "agentIdentifier": "masumi-test-temp-agent-003",
        "name": "Temporary Test Agent",
        "registration_date": "2024-01-01T00:00:00Z",
        "status": "active",
        "wallet_vkey": "vkey_test_temp_abcdef123456789abcdef123456789abcdef123456789"
    },
    "deregistration_payload": {
        "reason": "Test agent - planned deregistration",
        "effective_date": "2024-01-20T12:00:00Z"
    }
}

# Test Smart Contract Addresses
TEST_CONTRACTS = {
    "payment": "addr_test1contract_payment_test_abc123def456ghi789jkl012",
    "registry": "addr_test1contract_registry_test_mno345pqr678stu901vwx234"
}

# Common test parameters for API calls
DEFAULT_TEST_PARAMS = {
    "network": "Preprod",
    "limit": 10,
    "includeHistory": False
}

def validate_testnet_safety(network: str) -> None:
    """Ensure operations are testnet-safe"""
    if network == "Mainnet":
        raise ValueError("Mainnet operations not allowed in testing mode")
    
    if network != "Preprod":
        raise ValueError(f"Only Preprod network allowed in testing, got: {network}")

def validate_test_data_only(identifier: str) -> None:
    """Ensure only test/dummy data is used"""
    if not identifier.startswith("masumi-test-"):
        raise ValueError(f"Only test data allowed. Identifier must start with 'masumi-test-', got: {identifier}")

def get_test_agent(agent_type: str = "writer") -> Dict[str, Any]:
    """Get test agent data by type"""
    if agent_type == "writer":
        return DUMMY_AGENTS["test_writer_agent"]
    elif agent_type == "analyzer":
        return DUMMY_AGENTS["test_analyzer_agent"]
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")

def get_test_wallet(wallet_type: str = "buyer") -> Dict[str, Any]:
    """Get test wallet data by type"""
    if wallet_type not in TEST_WALLETS:
        raise ValueError(f"Unknown wallet type: {wallet_type}")
    return TEST_WALLETS[wallet_type]

def get_future_timestamp(hours_ahead: int = 12) -> str:
    """Generate future timestamp for test data"""
    future_time = datetime.utcnow() + timedelta(hours=hours_ahead)
    return future_time.isoformat() + "Z"

def generate_test_identifier(prefix: str = "masumi-test") -> str:
    """Generate unique test identifier"""
    import uuid
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

# Validation function for all test operations
def ensure_testnet_environment() -> None:
    """Verify we're in a safe testnet environment"""
    network = os.getenv("MASUMI_NETWORK", "Preprod")
    testing_mode = os.getenv("MASUMI_TESTING_MODE", "true").lower() == "true"
    
    if network == "Mainnet" and testing_mode:
        raise ValueError("Cannot run tests on Mainnet when MASUMI_TESTING_MODE is enabled")
    
    if not testing_mode and network == "Mainnet":
        raise ValueError("Mainnet operations require MASUMI_TESTING_MODE to be disabled")

# Export all test data for easy access
__all__ = [
    "TESTNET_CONFIG",
    "DUMMY_AGENTS", 
    "TEST_WALLETS",
    "PAYMENT_TEST_DATA",
    "PURCHASE_REFUND_DATA", 
    "AGENT_DEREGISTRATION_DATA",
    "TEST_CONTRACTS",
    "DEFAULT_TEST_PARAMS",
    "validate_testnet_safety",
    "validate_test_data_only",
    "get_test_agent",
    "get_test_wallet", 
    "get_future_timestamp",
    "generate_test_identifier",
    "ensure_testnet_environment"
]