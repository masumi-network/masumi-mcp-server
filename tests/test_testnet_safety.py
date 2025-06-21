#!/usr/bin/env python3
"""
Dedicated tests for testnet safety validation across all tools.
"""

import asyncio
import json
import subprocess
import sys
import unittest
from pathlib import Path

class TestTestnetSafety(unittest.TestCase):
    """Test testnet safety validation for all tools that interact with networks"""
    
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
                "clientInfo": {"name": "safety-test", "version": "1.0"}
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
        
        # Read response with timeout
        try:
            response_line = await asyncio.wait_for(
                self.server_process.stdout.readline(), 
                timeout=3.0
            )
            if response_line:
                return json.loads(response_line.decode())
        except asyncio.TimeoutError:
            return {"error": "timeout"}
        return None
    
    async def _call_tool_and_check_safety(self, tool_name, mainnet_args, preprod_args):
        """Helper to test both mainnet blocking and preprod allowing"""
        # Test mainnet blocking
        mainnet_response = await self._send_request({
            "jsonrpc": "2.0",
            "id": 100,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": mainnet_args
            }
        })
        
        self.assertIsNotNone(mainnet_response, f"No response for {tool_name} mainnet test")
        if "result" in mainnet_response:
            result = mainnet_response["result"]
            self.assertIn("content", result)
            content_text = result["content"][0].get("text", "")
            self.assertIn("Mainnet operations not allowed", content_text, 
                         f"{tool_name} should block mainnet operations")
        
        # Test preprod allowing (should proceed to next validation/error)
        preprod_response = await self._send_request({
            "jsonrpc": "2.0",
            "id": 101,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": preprod_args
            }
        })
        
        self.assertIsNotNone(preprod_response, f"No response for {tool_name} preprod test")
        if "result" in preprod_response:
            result = preprod_response["result"]
            self.assertIn("content", result)
            content_text = result["content"][0].get("text", "")
            # Should not contain mainnet blocking message
            self.assertNotIn("Mainnet operations not allowed", content_text, 
                           f"{tool_name} should allow preprod operations")
            # Should proceed to next validation (URL/token not configured)
            self.assertTrue(
                "not configured" in content_text or 
                "Error" in content_text,
                f"{tool_name} should proceed past testnet safety to next validation"
            )
    
    async def test_query_payments_safety(self):
        """Test query_payments testnet safety"""
        await self._start_server_and_initialize()
        
        mainnet_args = {"network": "Mainnet", "limit": 5}
        preprod_args = {"network": "Preprod", "limit": 5}
        
        await self._call_tool_and_check_safety("query_payments", mainnet_args, preprod_args)
    
    async def test_get_purchase_history_safety(self):
        """Test get_purchase_history testnet safety"""
        await self._start_server_and_initialize()
        
        mainnet_args = {"network": "Mainnet", "limit": 10}
        preprod_args = {"network": "Preprod", "limit": 10}
        
        await self._call_tool_and_check_safety("get_purchase_history", mainnet_args, preprod_args)
    
    async def test_query_registry_safety(self):
        """Test query_registry testnet safety"""
        await self._start_server_and_initialize()
        
        mainnet_args = {"network": "Mainnet"}
        preprod_args = {"network": "Preprod"}
        
        await self._call_tool_and_check_safety("query_registry", mainnet_args, preprod_args)
    
    async def test_register_agent_safety(self):
        """Test register_agent testnet safety"""
        await self._start_server_and_initialize()
        
        base_args = {
            "name": "masumi-test-safety-001",
            "api_base_url": "https://test.com",
            "selling_wallet_vkey": "vkey123",
            "capability_name": "Test",
            "capability_version": "1.0.0",
            "base_price": 1000000
        }
        
        mainnet_args = {**base_args, "network": "Mainnet"}
        preprod_args = {**base_args, "network": "Preprod"}
        
        await self._call_tool_and_check_safety("register_agent", mainnet_args, preprod_args)
    
    async def test_unregister_agent_safety(self):
        """Test unregister_agent testnet safety"""
        await self._start_server_and_initialize()
        
        mainnet_args = {"agent_identifier": "masumi-test-agent", "network": "Mainnet"}
        preprod_args = {"agent_identifier": "masumi-test-agent", "network": "Preprod"}
        
        await self._call_tool_and_check_safety("unregister_agent", mainnet_args, preprod_args)
    
    async def test_get_agents_by_wallet_safety(self):
        """Test get_agents_by_wallet testnet safety"""
        await self._start_server_and_initialize()
        
        mainnet_args = {"network": "Mainnet", "wallet_vkey": "vkey_test"}
        preprod_args = {"network": "Preprod", "wallet_vkey": "vkey_test"}
        
        await self._call_tool_and_check_safety("get_agents_by_wallet", mainnet_args, preprod_args)
    
    async def test_invalid_network_safety(self):
        """Test invalid network names are rejected"""
        await self._start_server_and_initialize()
        
        # Test invalid network name
        response = await self._send_request({
            "jsonrpc": "2.0",
            "id": 200,
            "method": "tools/call",
            "params": {
                "name": "query_payments",
                "arguments": {
                    "network": "InvalidNetwork",
                    "limit": 5
                }
            }
        })
        
        self.assertIsNotNone(response)
        if "result" in response:
            result = response["result"]
            self.assertIn("content", result)
            content_text = result["content"][0].get("text", "")
            # Should reject invalid network
            self.assertTrue(
                "Preprod" in content_text or 
                "Invalid" in content_text or
                "not allowed" in content_text,
                "Should reject invalid network names"
            )
    
    async def test_agent_name_safety_validation(self):
        """Test agent names must start with masumi-test- for testing"""
        await self._start_server_and_initialize()
        
        # Test invalid agent name (doesn't start with masumi-test-)
        response = await self._send_request({
            "jsonrpc": "2.0",
            "id": 300,
            "method": "tools/call",
            "params": {
                "name": "register_agent",
                "arguments": {
                    "network": "Preprod",
                    "name": "invalid-production-agent",  # Should start with masumi-test-
                    "api_base_url": "https://test.com",
                    "selling_wallet_vkey": "vkey123",
                    "capability_name": "Test",
                    "capability_version": "1.0.0",
                    "base_price": 1000000
                }
            }
        })
        
        self.assertIsNotNone(response)
        if "result" in response:
            result = response["result"]
            self.assertIn("content", result)
            content_text = result["content"][0].get("text", "")
            # Should require masumi-test- prefix
            self.assertIn("masumi-test-", content_text,
                         "Should require masumi-test- prefix for agent names")
    
    async def test_parameter_validation_safety(self):
        """Test parameter validation prevents unsafe values"""
        await self._start_server_and_initialize()
        
        # Test limit too high
        response = await self._send_request({
            "jsonrpc": "2.0",
            "id": 400,
            "method": "tools/call",
            "params": {
                "name": "query_payments",
                "arguments": {
                    "network": "Preprod",
                    "limit": 999999  # Way too high
                }
            }
        })
        
        self.assertIsNotNone(response)
        if "result" in response:
            result = response["result"]
            self.assertIn("content", result)
            content_text = result["content"][0].get("text", "")
            self.assertIn("between 1 and 100", content_text,
                         "Should validate limit parameter bounds")

class TestTestnetSafetySync(unittest.TestCase):
    """Synchronous wrapper for async testnet safety tests"""
    
    def _run_async_test(self, test_method):
        """Helper to run async test methods"""
        async def wrapper():
            test_instance = TestTestnetSafety()
            test_instance.setUp()
            try:
                await test_method(test_instance)
            finally:
                test_instance.tearDown()
        
        asyncio.run(wrapper())
    
    def test_query_payments_safety(self):
        """Test query_payments testnet safety"""
        self._run_async_test(TestTestnetSafety.test_query_payments_safety)
    
    def test_get_purchase_history_safety(self):
        """Test get_purchase_history testnet safety"""
        self._run_async_test(TestTestnetSafety.test_get_purchase_history_safety)
    
    def test_query_registry_safety(self):
        """Test query_registry testnet safety"""
        self._run_async_test(TestTestnetSafety.test_query_registry_safety)
    
    def test_register_agent_safety(self):
        """Test register_agent testnet safety"""
        self._run_async_test(TestTestnetSafety.test_register_agent_safety)
    
    def test_unregister_agent_safety(self):
        """Test unregister_agent testnet safety"""
        self._run_async_test(TestTestnetSafety.test_unregister_agent_safety)
    
    def test_get_agents_by_wallet_safety(self):
        """Test get_agents_by_wallet testnet safety"""
        self._run_async_test(TestTestnetSafety.test_get_agents_by_wallet_safety)
    
    def test_invalid_network_safety(self):
        """Test invalid network safety"""
        self._run_async_test(TestTestnetSafety.test_invalid_network_safety)
    
    def test_agent_name_safety_validation(self):
        """Test agent name safety validation"""
        self._run_async_test(TestTestnetSafety.test_agent_name_safety_validation)
    
    def test_parameter_validation_safety(self):
        """Test parameter validation safety"""
        self._run_async_test(TestTestnetSafety.test_parameter_validation_safety)

if __name__ == "__main__":
    print("🛡️  Running Testnet Safety Validation Tests")
    print("=" * 50)
    unittest.main(verbosity=2)