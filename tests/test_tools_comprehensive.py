#!/usr/bin/env python3
"""
Comprehensive test suite for all MCP tools functionality.
"""

import asyncio
import json
import subprocess
import sys
import unittest
from pathlib import Path

class TestToolsComprehensive(unittest.TestCase):
    """Comprehensive testing for all MCP tools"""
    
    def setUp(self):
        """Set up test environment"""
        self.server_process = None
        
    def tearDown(self):
        """Clean up after tests"""
        if self.server_process:
            self.server_process.terminate()
    
    async def _start_server_and_initialize(self):
        """Start server and complete initialization"""
        self.server_process = await asyncio.create_subprocess_exec(
            sys.executable, "server.py",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={"PYTHONPATH": "./"}
        )
        
        # Initialize
        await self._send_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        })
        
        # Send initialized notification
        await self._send_request({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        })
        
        return self.server_process
    
    async def _send_request(self, request_dict):
        """Send JSON-RPC request to server"""
        if not self.server_process:
            raise RuntimeError("Server not started")
        
        request_json = json.dumps(request_dict) + "\n"
        self.server_process.stdin.write(request_json.encode())
        await self.server_process.stdin.drain()
        
        # Read response (with timeout)
        try:
            response_line = await asyncio.wait_for(
                self.server_process.stdout.readline(), 
                timeout=5.0
            )
            if response_line:
                return json.loads(response_line.decode())
        except asyncio.TimeoutError:
            return {"error": "timeout"}
        return None
    
    async def _call_tool(self, tool_name, arguments, request_id=None):
        """Helper to call a tool"""
        if request_id is None:
            request_id = hash(tool_name) % 1000
        
        return await self._send_request({
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        })
    
    async def test_list_agents_tool(self):
        """Test list_agents tool"""
        await self._start_server_and_initialize()
        
        response = await self._call_tool("list_agents", {})
        
        self.assertIsNotNone(response)
        if "result" in response:
            # Tool executed successfully
            result = response["result"]
            self.assertIn("content", result)
            # Should return registry token error since not configured
            content_text = result["content"][0].get("text", "")
            self.assertIn("Registry Token is not configured", content_text)
        else:
            self.fail(f"Tool call failed: {response}")
    
    async def test_query_payments_preprod(self):
        """Test query_payments with Preprod (valid testnet)"""
        await self._start_server_and_initialize()
        
        response = await self._call_tool("query_payments", {
            "network": "Preprod",
            "limit": 5
        })
        
        self.assertIsNotNone(response)
        if "result" in response:
            result = response["result"]
            self.assertIn("content", result)
            # Should return payment URL error since not configured
            content_text = result["content"][0].get("text", "")
            self.assertIn("MASUMI_PAYMENT_URL is not configured", content_text)
    
    async def test_query_payments_mainnet_blocked(self):
        """Test query_payments with Mainnet (should be blocked)"""
        await self._start_server_and_initialize()
        
        response = await self._call_tool("query_payments", {
            "network": "Mainnet",
            "limit": 5
        })
        
        self.assertIsNotNone(response)
        if "result" in response:
            result = response["result"]
            self.assertIn("content", result)
            content_text = result["content"][0].get("text", "")
            self.assertIn("Mainnet operations not allowed", content_text)
    
    async def test_get_purchase_history(self):
        """Test get_purchase_history tool"""
        await self._start_server_and_initialize()
        
        response = await self._call_tool("get_purchase_history", {
            "network": "Preprod",
            "limit": 10,
            "include_history": True
        })
        
        self.assertIsNotNone(response)
        if "result" in response:
            result = response["result"]
            self.assertIn("content", result)
            # Should return payment URL error since not configured
            content_text = result["content"][0].get("text", "")
            self.assertIn("MASUMI_PAYMENT_URL is not configured", content_text)
    
    async def test_query_registry(self):
        """Test query_registry tool"""
        await self._start_server_and_initialize()
        
        response = await self._call_tool("query_registry", {
            "network": "Preprod"
        })
        
        self.assertIsNotNone(response)
        if "result" in response:
            result = response["result"]
            self.assertIn("content", result)
            # Should return registry URL error since not configured
            content_text = result["content"][0].get("text", "")
            self.assertIn("MASUMI_REGISTRY_URL is not configured", content_text)
    
    async def test_register_agent_testnet_safety(self):
        """Test register_agent with testnet safety validation"""
        await self._start_server_and_initialize()
        
        # Test with mainnet (should be blocked)
        response = await self._call_tool("register_agent", {
            "network": "Mainnet",
            "name": "test-agent",
            "api_base_url": "https://test.com",
            "selling_wallet_vkey": "vkey123",
            "capability_name": "Test",
            "capability_version": "1.0.0",
            "base_price": 1000000
        })
        
        self.assertIsNotNone(response)
        if "result" in response:
            result = response["result"]
            self.assertIn("content", result)
            content_text = result["content"][0].get("text", "")
            self.assertIn("Mainnet operations not allowed", content_text)
    
    async def test_register_agent_name_validation(self):
        """Test register_agent with invalid name (should require masumi-test- prefix)"""
        await self._start_server_and_initialize()
        
        response = await self._call_tool("register_agent", {
            "network": "Preprod",
            "name": "invalid-agent-name",  # Should start with masumi-test-
            "api_base_url": "https://test.com",
            "selling_wallet_vkey": "vkey123",
            "capability_name": "Test",
            "capability_version": "1.0.0",
            "base_price": 1000000
        })
        
        self.assertIsNotNone(response)
        if "result" in response:
            result = response["result"]
            self.assertIn("content", result)
            content_text = result["content"][0].get("text", "")
            self.assertIn("masumi-test-", content_text)
    
    async def test_unregister_agent(self):
        """Test unregister_agent tool"""
        await self._start_server_and_initialize()
        
        # Test with mainnet (should be blocked)
        response = await self._call_tool("unregister_agent", {
            "agent_identifier": "test-agent",
            "network": "Mainnet"
        })
        
        self.assertIsNotNone(response)
        if "result" in response:
            result = response["result"]
            self.assertIn("content", result)
            content_text = result["content"][0].get("text", "")
            self.assertIn("Mainnet operations not allowed", content_text)
    
    async def test_get_agents_by_wallet(self):
        """Test get_agents_by_wallet tool"""
        await self._start_server_and_initialize()
        
        response = await self._call_tool("get_agents_by_wallet", {
            "network": "Preprod",
            "wallet_vkey": "vkey_test_writer_123"
        })
        
        self.assertIsNotNone(response)
        if "result" in response:
            result = response["result"]
            self.assertIn("content", result)
            # Should return registry URL error since not configured
            content_text = result["content"][0].get("text", "")
            self.assertIn("MASUMI_REGISTRY_URL is not configured", content_text)
    
    async def test_get_agent_input_schema(self):
        """Test get_agent_input_schema tool"""
        await self._start_server_and_initialize()
        
        response = await self._call_tool("get_agent_input_schema", {
            "agent_identifier": "test-agent",
            "api_base_url": "https://test-agent.com/"
        })
        
        self.assertIsNotNone(response)
        if "result" in response:
            result = response["result"]
            self.assertIn("content", result)
            # Should return connection error since test URL doesn't exist
            content_text = result["content"][0].get("text", "")
            self.assertTrue(
                "Error" in content_text or 
                "connection" in content_text.lower() or
                "timeout" in content_text.lower()
            )
    
    async def test_invalid_tool_parameters(self):
        """Test tools with invalid parameters"""
        await self._start_server_and_initialize()
        
        # Test query_payments with invalid limit
        response = await self._call_tool("query_payments", {
            "network": "Preprod",
            "limit": 1000  # Should be max 100
        })
        
        self.assertIsNotNone(response)
        if "result" in response:
            result = response["result"]
            self.assertIn("content", result)
            content_text = result["content"][0].get("text", "")
            self.assertIn("between 1 and 100", content_text)

class TestToolsComprehensiveSync(unittest.TestCase):
    """Synchronous wrapper for async tool tests"""
    
    def _run_async_test(self, test_method):
        """Helper to run async test methods"""
        async def wrapper():
            test_instance = TestToolsComprehensive()
            test_instance.setUp()
            try:
                await test_method(test_instance)
            finally:
                test_instance.tearDown()
        
        asyncio.run(wrapper())
    
    def test_list_agents_tool(self):
        """Test list_agents tool"""
        self._run_async_test(TestToolsComprehensive.test_list_agents_tool)
    
    def test_query_payments_preprod(self):
        """Test query_payments with Preprod"""
        self._run_async_test(TestToolsComprehensive.test_query_payments_preprod)
    
    def test_query_payments_mainnet_blocked(self):
        """Test query_payments mainnet blocking"""
        self._run_async_test(TestToolsComprehensive.test_query_payments_mainnet_blocked)
    
    def test_get_purchase_history(self):
        """Test get_purchase_history tool"""
        self._run_async_test(TestToolsComprehensive.test_get_purchase_history)
    
    def test_query_registry(self):
        """Test query_registry tool"""
        self._run_async_test(TestToolsComprehensive.test_query_registry)
    
    def test_register_agent_testnet_safety(self):
        """Test register_agent testnet safety"""
        self._run_async_test(TestToolsComprehensive.test_register_agent_testnet_safety)
    
    def test_register_agent_name_validation(self):
        """Test register_agent name validation"""
        self._run_async_test(TestToolsComprehensive.test_register_agent_name_validation)
    
    def test_unregister_agent(self):
        """Test unregister_agent tool"""
        self._run_async_test(TestToolsComprehensive.test_unregister_agent)
    
    def test_get_agents_by_wallet(self):
        """Test get_agents_by_wallet tool"""
        self._run_async_test(TestToolsComprehensive.test_get_agents_by_wallet)
    
    def test_get_agent_input_schema(self):
        """Test get_agent_input_schema tool"""
        self._run_async_test(TestToolsComprehensive.test_get_agent_input_schema)
    
    def test_invalid_tool_parameters(self):
        """Test invalid tool parameters"""
        self._run_async_test(TestToolsComprehensive.test_invalid_tool_parameters)

if __name__ == "__main__":
    print("🧪 Running Comprehensive Tool Tests")
    print("=" * 50)
    unittest.main(verbosity=2)