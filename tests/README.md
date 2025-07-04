# Masumi MCP Server Test Suite

This directory contains comprehensive tests for the Masumi MCP Server functionality.

## Test Files

### 1. `simple_test.py`
- Basic smoke tests for server startup and module imports
- Quick validation of tool registration and testnet safety
- Useful for rapid development feedback

### 2. `test_mcp_connection.py`
- Tests MCP protocol compliance and server initialization
- Validates JSON-RPC communication
- Tests tool discovery and listing

### 3. `test_tools_comprehensive.py`
- Comprehensive testing of all 11 MCP tools
- Parameter validation and error handling
- Configuration dependency testing

### 4. `test_testnet_safety.py`
- Dedicated testnet safety validation tests
- Mainnet operation blocking verification
- Network parameter validation
- Agent name prefix validation for test environments

### 5. `test_agent_integration.py`
- End-to-end agent management workflows
- Agent registration, unregistration, and querying
- Integration testing with test data
- Multi-agent operation scenarios

### 6. `test_data.py`
- Comprehensive test data infrastructure
- Dummy agents, wallets, and payment data
- Testnet safety validation functions
- Test data generation utilities

## Running Tests

### Run All Tests
```bash
# From project root
export PYTHONPATH=$(pwd)/ && uv run python tests/run_all_tests.py
```

### Run Specific Test Suites
```bash
# Connection tests
uv run python tests/run_all_tests.py connection

# Tool tests
uv run python tests/run_all_tests.py tools

# Safety tests
uv run python tests/run_all_tests.py safety

# Agent integration tests
uv run python tests/run_all_tests.py agent

# Simple smoke tests
uv run python tests/run_all_tests.py simple
```

### Run Individual Test Files
```bash
# Simple smoke test
export PYTHONPATH=$(pwd)/ && uv run python tests/simple_test.py

# MCP connection tests
export PYTHONPATH=$(pwd)/ && uv run python tests/test_mcp_connection.py

# Other test files follow similar pattern
```

## Test Categories

### 🔌 Connection Tests
- MCP protocol initialization
- Server startup validation
- Tool discovery and registration

### 🛠️ Tool Tests
- All 11 tools functionality
- Parameter validation
- Error handling and edge cases

### 🛡️ Safety Tests
- Testnet vs Mainnet validation
- Parameter bounds checking
- Test data prefix requirements

### 🤖 Agent Integration Tests
- Complete agent lifecycle workflows
- Registration → Query → Unregistration
- Multi-agent scenarios

## Test Data Safety

All tests use the comprehensive test data from `test_data.py`:

- **Testnet Only**: All operations restricted to Preprod network
- **Test Prefixes**: Agent names must start with `masumi-test-`
- **Dummy Data**: Safe test wallets, payments, and agent data
- **Validation**: Built-in safety checks prevent mainnet operations

## Test Environment Requirements

- Python 3.12+
- uv package manager
- MCP server dependencies (httpx, python-dotenv, etc.)
- No actual network configuration required (tests validate error handling)

## Expected Test Behavior

Since the tests run without actual Masumi network configuration:

1. **Testnet Safety**: ✅ Should pass - validates mainnet blocking
2. **Configuration Errors**: ✅ Expected - shows proper error handling
3. **Tool Registration**: ✅ Should pass - all 11 tools available
4. **Parameter Validation**: ✅ Should pass - validates input bounds

The tests focus on:
- Protocol compliance
- Testnet safety validation  
- Parameter validation
- Error handling
- Tool registration and discovery

Rather than actual network operations (which require valid tokens and configuration).

## Continuous Integration

These tests are designed to run in CI environments without external dependencies:
- No network calls to actual Masumi services
- Self-contained test data
- Validates core functionality and safety measures
- Fast execution (< 30 seconds total)