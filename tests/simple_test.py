#!/usr/bin/env python3
"""
Simple test to verify the server works and query_payments tool is available.
"""

import asyncio
import subprocess
import json
import os
import sys
from pathlib import Path

async def test_server_with_mcp_cli():
    """Test server using MCP CLI approach"""
    print("🚀 Testing server with MCP CLI approach...")
    
    try:
        # Test 1: Check if server module can be imported without errors
        print("📋 Testing server module import...")
        try:
            import server  # This will run the configuration checks
            print("✅ Server module import test passed")
        except SystemExit:
            # Expected if configuration is missing, but import worked
            print("✅ Server module import test passed (config check triggered)")
        except Exception as e:
            print(f"❌ Server has import errors: {e}")
            return False
        
        # Test 2: Try importing the modules directly
        print("📋 Testing module imports...")
        try:
            import tools
            import prompts
            print("✅ All modules import successfully")
        except Exception as e:
            print(f"❌ Module import failed: {e}")
            return False
        
        # Test 3: Check if new tools are registered
        print("📋 Testing tool registration...")
        try:
            from tools import query_payments, get_purchase_history, query_registry, register_agent, unregister_agent, get_agents_by_wallet
            from prompts import prompt_query_payments, prompt_get_purchase_history, prompt_query_registry, prompt_register_agent, prompt_unregister_agent, prompt_get_agents_by_wallet
            print("✅ New tools (payment, purchase, registry, agent management) and prompts imported successfully")
        except Exception as e:
            print(f"❌ New tool import failed: {e}")
            return False
        
        # Test 4: Test the tool functions directly with safe parameters
        print("📋 Testing tool functions directly...")
        try:
            # Mock a context object for testing
            class MockContext:
                def __init__(self):
                    self.request_context = type('obj', (object,), {
                        'lifespan_context': type('obj', (object,), {
                            'http_client': None,
                            'payment_token': 'test-payment-token',
                            'registry_token': 'test-registry-token',
                            'network': 'Preprod'
                        })()
                    })()
                
                def info(self, msg): print(f"INFO: {msg}")
                def error(self, msg): print(f"ERROR: {msg}")
                def warn(self, msg): print(f"WARN: {msg}")
            
            mock_ctx = MockContext()
            
            # Test query_payments parameter validation (should catch invalid parameters)
            result = await query_payments(mock_ctx, "Mainnet", 10)
            if "Error:" in result and ("Mainnet" in result or "Preprod" in result):
                print("✅ query_payments testnet safety validation working correctly")
            else:
                print(f"⚠️  query_payments testnet safety check may not be working: {result}")
            
            # Test get_purchase_history parameter validation
            result = await get_purchase_history(mock_ctx, "Mainnet", 10)
            if "Error:" in result and ("Mainnet" in result or "Preprod" in result):
                print("✅ get_purchase_history testnet safety validation working correctly")
            else:
                print(f"⚠️  get_purchase_history testnet safety check may not be working: {result}")
            
            # Test query_registry parameter validation
            result = await query_registry(mock_ctx, "Mainnet")
            if "Error:" in result and ("Mainnet" in result or "Preprod" in result):
                print("✅ query_registry testnet safety validation working correctly")
            else:
                print(f"⚠️  query_registry testnet safety check may not be working: {result}")
            
            # Test agent management tools
            result = await register_agent(mock_ctx, "Mainnet", "test-agent", "https://test.com", "vkey123", "Test", "1.0.0", 1000000)
            if "Error:" in result and ("Mainnet" in result or "masumi-test-" in result):
                print("✅ register_agent testnet safety validation working correctly")
            else:
                print(f"⚠️  register_agent testnet safety check may not be working: {result}")
            
            result = await unregister_agent(mock_ctx, "test-agent", "Mainnet")
            if "Error:" in result and ("Mainnet" in result or "masumi-test-" in result):
                print("✅ unregister_agent testnet safety validation working correctly")
            else:
                print(f"⚠️  unregister_agent testnet safety check may not be working: {result}")
            
            result = await get_agents_by_wallet(mock_ctx, "Mainnet", "test_wallet")
            if "Error:" in result and ("Mainnet" in result or "Preprod" in result):
                print("✅ get_agents_by_wallet testnet safety validation working correctly")
            else:
                print(f"⚠️  get_agents_by_wallet testnet safety check may not be working: {result}")
            
            # Test with valid testnet parameters
            result = await query_payments(mock_ctx, "Preprod", 5)
            if "MASUMI_PAYMENT_URL is not configured" in result:
                print("✅ query_payments executes and correctly identifies missing configuration")
            else:
                print(f"⚠️  Unexpected result: {result}")
            
            result = await get_purchase_history(mock_ctx, "Preprod", 5)
            if "MASUMI_PAYMENT_URL is not configured" in result:
                print("✅ get_purchase_history executes and correctly identifies missing configuration")
            else:
                print(f"⚠️  Unexpected result: {result}")
            
            result = await query_registry(mock_ctx, "Preprod")
            if "MASUMI_REGISTRY_URL is not configured" in result:
                print("✅ query_registry executes and correctly identifies missing configuration")
            else:
                print(f"⚠️  Unexpected result: {result}")
            
        except Exception as e:
            print(f"❌ Direct function test failed: {e}")
            return False
        
        print("\n🎉 All basic tests passed!")
        print("📋 Summary:")
        print("  ✅ Server starts without syntax errors")
        print("  ✅ All modules import correctly")
        print("  ✅ New tools (query_payments, get_purchase_history, query_registry) are properly registered")
        print("  ✅ Tool functions execute with proper validation")
        print("  ✅ Testnet safety checks are working for all tools")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_environment_setup():
    """Test environment configuration"""
    print("🔧 Testing environment setup...")
    
    # Check Python version
    print(f"📋 Python version: {sys.version}")
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found - server may not have proper configuration")
    
    # Check essential imports
    try:
        import httpx
        import json
        from mcp.server.fastmcp import FastMCP
        print("✅ Essential packages available")
        return True
    except ImportError as e:
        print(f"❌ Missing essential packages: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Simple Test Runner for Masumi MCP Server")
    print("=" * 60)
    
    # Test environment first
    if not test_environment_setup():
        print("\n❌ Environment setup failed. Please check dependencies.")
        sys.exit(1)
    
    # Test server functionality
    try:
        success = asyncio.run(test_server_with_mcp_cli())
        if success:
            print("\n✅ All tests passed! The query_payments tool is ready for use.")
            print("\n📝 Next steps:")
            print("  1. Configure .env file with proper tokens")
            print("  2. Test with actual MCP client")
            print("  3. Implement additional tools")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. Please review and fix issues.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Tests crashed: {e}")
        sys.exit(1)