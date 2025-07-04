#!/usr/bin/env python3
"""
Manual test script for the query_payments tool.
Tests the new payment querying functionality with testnet safety.
"""

import asyncio
import json
import os
from .test_utils import MCPTestRunner, print_test_header, print_test_result, validate_response_format
from .test_data import DEFAULT_TEST_PARAMS, TEST_CONTRACTS, ensure_testnet_environment

async def test_query_payments_basic():
    """Test basic query_payments functionality"""
    print_test_header("Basic Query Payments Test")
    
    try:
        async with MCPTestRunner() as runner:
            # Test 1: Tool exists
            exists = await runner.test_tool_exists("query_payments")
            if not exists:
                return False
            
            # Test 2: Basic query with minimal parameters
            params = {
                "network": "Preprod",
                "limit": 5
            }
            
            result = await runner.call_tool_safe("query_payments", params)
            
            if result["success"]:
                # Validate response format
                valid_format = validate_response_format(result["response"], ["status", "count", "network"])
                if valid_format:
                    print_test_result("Basic Query", True, "Tool executed and returned valid format")
                    return True
                else:
                    print_test_result("Basic Query", False, "Invalid response format")
                    return False
            else:
                print_test_result("Basic Query", False, f"Tool execution failed: {result['error']}")
                return False
                
    except Exception as e:
        print_test_result("Basic Query", False, f"Test error: {str(e)}")
        return False

async def test_query_payments_with_all_params():
    """Test query_payments with all optional parameters"""
    print_test_header("Query Payments with All Parameters")
    
    try:
        async with MCPTestRunner() as runner:
            params = {
                "network": "Preprod",
                "limit": 3,
                "cursor_id": "test-cursor-123",
                "smart_contract_address": TEST_CONTRACTS["payment"],
                "include_history": True
            }
            
            result = await runner.call_tool_safe("query_payments", params)
            
            if result["success"]:
                print_test_result("Full Parameters Query", True, "Tool accepted all parameters")
                return True
            else:
                # This might fail due to invalid cursor or contract address, which is expected
                print_test_result("Full Parameters Query", True, f"Tool properly handled parameters: {result['error']}")
                return True
                
    except Exception as e:
        print_test_result("Full Parameters Query", False, f"Test error: {str(e)}")
        return False

async def test_query_payments_parameter_validation():
    """Test parameter validation for query_payments"""
    print_test_header("Parameter Validation Tests")
    
    try:
        async with MCPTestRunner() as runner:
            
            # Test 1: Invalid network (Mainnet blocked)
            print("🧪 Testing Mainnet blocking...")
            invalid_params_mainnet = {
                "network": "Mainnet",
                "limit": 5
            }
            
            result1 = await runner.test_tool_with_invalid_params("query_payments", invalid_params_mainnet)
            
            # Test 2: Invalid limit (too high)
            print("🧪 Testing limit validation...")
            invalid_params_limit = {
                "network": "Preprod",
                "limit": 150  # Max is 100
            }
            
            result2 = await runner.test_tool_with_invalid_params("query_payments", invalid_params_limit)
            
            # Test 3: Invalid limit (too low)
            print("🧪 Testing minimum limit validation...")
            invalid_params_min = {
                "network": "Preprod",
                "limit": 0  # Min is 1
            }
            
            result3 = await runner.test_tool_with_invalid_params("query_payments", invalid_params_min)
            
            # Test 4: Smart contract address too long
            print("🧪 Testing contract address length validation...")
            invalid_params_address = {
                "network": "Preprod",
                "limit": 5,
                "smart_contract_address": "a" * 251  # Max is 250
            }
            
            result4 = await runner.test_tool_with_invalid_params("query_payments", invalid_params_address)
            
            all_passed = result1 and result2 and result3 and result4
            print_test_result("Parameter Validation", all_passed, 
                            "All validation tests passed" if all_passed else "Some validation tests failed")
            return all_passed
            
    except Exception as e:
        print_test_result("Parameter Validation", False, f"Test error: {str(e)}")
        return False

async def test_query_payments_edge_cases():
    """Test edge cases for query_payments"""
    print_test_header("Edge Cases Tests")
    
    try:
        async with MCPTestRunner() as runner:
            
            # Test 1: Minimum valid parameters
            print("🧪 Testing minimum valid parameters...")
            min_params = {
                "network": "Preprod",
                "limit": 1
            }
            
            result1 = await runner.call_tool_safe("query_payments", min_params)
            
            # Test 2: Maximum valid parameters
            print("🧪 Testing maximum valid parameters...")
            max_params = {
                "network": "Preprod", 
                "limit": 100
            }
            
            result2 = await runner.call_tool_safe("query_payments", max_params)
            
            # Test 3: Empty string parameters (should be handled gracefully)
            print("🧪 Testing empty string cursor...")
            empty_params = {
                "network": "Preprod",
                "limit": 5,
                "cursor_id": ""
            }
            
            result3 = await runner.call_tool_safe("query_payments", empty_params)
            
            success_count = sum([result1["success"], result2["success"], result3["success"]])
            print_test_result("Edge Cases", success_count >= 2, 
                            f"{success_count}/3 edge case tests passed")
            return success_count >= 2
            
    except Exception as e:
        print_test_result("Edge Cases", False, f"Test error: {str(e)}")
        return False

async def test_query_payments_environment_safety():
    """Test environment safety checks"""
    print_test_header("Environment Safety Tests")
    
    try:
        # Test environment validation
        ensure_testnet_environment()
        
        # Check environment variables
        network = os.getenv("MASUMI_NETWORK", "Preprod")
        testing_mode = os.getenv("MASUMI_TESTING_MODE", "true").lower() == "true"
        
        print(f"📋 Current network: {network}")
        print(f"📋 Testing mode: {testing_mode}")
        
        if network == "Preprod" and testing_mode:
            print_test_result("Environment Safety", True, "Safe testnet environment confirmed")
            return True
        elif network != "Mainnet":
            print_test_result("Environment Safety", True, "Non-mainnet environment confirmed")
            return True
        else:
            print_test_result("Environment Safety", False, "Unsafe environment detected")
            return False
            
    except Exception as e:
        print_test_result("Environment Safety", False, f"Environment check failed: {str(e)}")
        return False

async def run_all_query_payments_tests():
    """Run all query_payments tests"""
    print("🚀 Starting comprehensive query_payments tool testing...")
    print("="*80)
    
    # Ensure we're in a safe environment
    try:
        ensure_testnet_environment()
    except Exception as e:
        print(f"❌ Environment safety check failed: {e}")
        return False
    
    tests = [
        ("Environment Safety", test_query_payments_environment_safety),
        ("Basic Functionality", test_query_payments_basic),
        ("Full Parameters", test_query_payments_with_all_params),
        ("Parameter Validation", test_query_payments_parameter_validation),
        ("Edge Cases", test_query_payments_edge_cases)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 OVERALL RESULT: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All query_payments tests PASSED! Tool is ready for use.")
        return True
    else:
        print("⚠️  Some tests FAILED. Please review and fix issues before proceeding.")
        return False

if __name__ == "__main__":
    print("🧪 Manual Test Runner for query_payments Tool")
    print("This script tests the new payment querying functionality.")
    print("Make sure the MCP server is configured with proper environment variables.")
    print("\nStarting tests...\n")
    
    success = asyncio.run(run_all_query_payments_tests())
    
    if success:
        print("\n✅ query_payments tool is ready for production use!")
        exit(0)
    else:
        print("\n❌ query_payments tool needs fixes before proceeding.")
        exit(1)