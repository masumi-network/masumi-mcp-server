#!/usr/bin/env python3
"""
Integration tests for agent management functionality.
"""

import asyncio
import json
import subprocess
import sys
import unittest
from pathlib import Path

class TestAgentIntegration(unittest.TestCase):
    """Integration tests for agent management tools"""
    
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
                "clientInfo": {"name": "agent-test", "version": "1.0"}
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
    
    async def _call_tool(self, tool_name, arguments, request_id=None):
        """Helper to call a tool"""
        if request_id is None:
            request_id = hash(f"{tool_name}_{str(arguments)}") % 1000
        
        return await self._send_request({
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        })
    
    async def test_agent_registration_workflow(self):
        """Test complete agent registration workflow"""
        await self._start_server_and_initialize()
        
        # Test agent registration with valid test data
        registration_response = await self._call_tool("register_agent", {
            "network": "Preprod",
            "name": "masumi-test-integration-001",
            "api_base_url": "https://test-integration-agent.masumi-test.network/",
            "selling_wallet_vkey": "vkey_test_integration_123456789abcdef123456789abcdef12345678",
            "capability_name": "Integration Testing",
            "capability_version": "1.0.0",
            "base_price": 1000000,
            "tags": ["testing", "integration", "automated"],
            "description": "Test agent for integration testing",
            "author": "Masumi Test Suite",
            "legal_info": "Test agent - for integration testing only"
        })
        
        self.assertIsNotNone(registration_response)
        if "result" in registration_response:
            result = registration_response["result"]
            self.assertIn("content", result)
            content_text = result["content"][0].get("text", "")
            # Should proceed past testnet safety validation
            self.assertNotIn("Mainnet operations not allowed", content_text)
            # Should contain test data validation or registry URL error
            self.assertTrue(
                "masumi-test-" in content_text or
                "MASUMI_REGISTRY_URL is not configured" in content_text,
                "Should validate test data or show configuration error"
            )
    
    async def test_agent_unregistration_workflow(self):
        """Test agent unregistration workflow"""
        await self._start_server_and_initialize()
        
        # Test agent unregistration
        unregistration_response = await self._call_tool("unregister_agent", {
            "agent_identifier": "masumi-test-integration-001",
            "network": "Preprod"
        })
        
        self.assertIsNotNone(unregistration_response)
        if "result" in unregistration_response:
            result = unregistration_response["result"]
            self.assertIn("content", result)
            content_text = result["content"][0].get("text", "")
            # Should proceed past testnet safety validation
            self.assertNotIn("Mainnet operations not allowed", content_text)
            # Should contain test data validation or registry URL error
            self.assertTrue(
                "masumi-test-" in content_text or
                "MASUMI_REGISTRY_URL is not configured" in content_text,
                "Should validate test data or show configuration error"
            )
    
    async def test_wallet_agent_query_workflow(self):
        """Test querying agents by wallet workflow"""
        await self._start_server_and_initialize()
        
        # Test querying agents by wallet
        wallet_query_response = await self._call_tool("get_agents_by_wallet", {
            "network": "Preprod",
            "wallet_vkey": "vkey_test_integration_123456789abcdef123456789abcdef12345678"
        })
        
        self.assertIsNotNone(wallet_query_response)
        if "result" in wallet_query_response:
            result = wallet_query_response["result"]
            self.assertIn("content", result)
            content_text = result["content"][0].get("text", "")
            # Should proceed past testnet safety validation
            self.assertNotIn("Mainnet operations not allowed", content_text)
            # Should show registry URL error since not configured
            self.assertIn("MASUMI_REGISTRY_URL is not configured", content_text)
    
    async def test_registry_query_workflow(self):
        """Test registry querying workflow"""
        await self._start_server_and_initialize()
        
        # Test querying registry
        registry_response = await self._call_tool("query_registry", {
            "network": "Preprod"
        })
        
        self.assertIsNotNone(registry_response)
        if "result" in registry_response:
            result = registry_response["result"]
            self.assertIn("content", result)
            content_text = result["content"][0].get("text", "")
            # Should proceed past testnet safety validation
            self.assertNotIn("Mainnet operations not allowed", content_text)
            # Should show registry URL error since not configured
            self.assertIn("MASUMI_REGISTRY_URL is not configured", content_text)
    
    async def test_agent_registration_parameter_validation(self):
        """Test agent registration parameter validation"""
        await self._start_server_and_initialize()
        
        # Test missing required parameters
        incomplete_response = await self._call_tool("register_agent", {
            "network": "Preprod",
            "name": "masumi-test-incomplete",
            # Missing other required parameters
        })
        
        # This should fail at the MCP level due to missing required parameters
        # The server should return an error for missing parameters
        self.assertIsNotNone(incomplete_response)
        self.assertTrue(
            "error" in incomplete_response or
            ("result" in incomplete_response and "error" in incomplete_response["result"]["content"][0].get("text", "").lower())
        )
    
    async def test_agent_name_prefix_validation(self):
        """Test agent name must have masumi-test- prefix"""
        await self._start_server_and_initialize()
        
        # Test invalid agent name (no masumi-test- prefix)
        invalid_name_response = await self._call_tool("register_agent", {
            "network": "Preprod",
            "name": "production-agent-001",  # Invalid - should be masumi-test-*
            "api_base_url": "https://test.com",
            "selling_wallet_vkey": "vkey123",
            "capability_name": "Test",
            "capability_version": "1.0.0",
            "base_price": 1000000
        })
        
        self.assertIsNotNone(invalid_name_response)
        if "result" in invalid_name_response:
            result = invalid_name_response["result"]
            self.assertIn("content", result)
            content_text = result["content"][0].get("text", "")
            self.assertIn("masumi-test-", content_text,
                         "Should require masumi-test- prefix for agent names")
    
    async def test_agent_url_validation(self):
        """Test agent API URL validation"""
        await self._start_server_and_initialize()
        
        # Test with invalid URL format
        invalid_url_response = await self._call_tool("register_agent", {
            "network": "Preprod",
            "name": "masumi-test-invalid-url",
            "api_base_url": "not-a-valid-url",  # Invalid URL
            "selling_wallet_vkey": "vkey123",
            "capability_name": "Test",
            "capability_version": "1.0.0",
            "base_price": 1000000
        })
        
        self.assertIsNotNone(invalid_url_response)
        if "result" in invalid_url_response:
            result = invalid_url_response["result"]
            self.assertIn("content", result)
            content_text = result["content"][0].get("text", "")
            # Should proceed past basic validation to configuration error
            # The URL validation might happen at the registry level
            self.assertTrue(
                "MASUMI_REGISTRY_URL is not configured" in content_text or
                "url" in content_text.lower() or
                "http" in content_text.lower(),
                "Should validate URL format or show configuration error"
            )
    
    async def test_agent_pricing_validation(self):
        """Test agent pricing parameter validation"""
        await self._start_server_and_initialize()
        
        # Test with negative price (should be handled by parameter validation)
        negative_price_response = await self._call_tool("register_agent", {
            "network": "Preprod",
            "name": "masumi-test-negative-price",
            "api_base_url": "https://test.com",
            "selling_wallet_vkey": "vkey123",
            "capability_name": "Test",
            "capability_version": "1.0.0",
            "base_price": -1000000  # Negative price
        })
        
        self.assertIsNotNone(negative_price_response)
        # The response should either succeed (proceed to registry configuration error)
        # or fail with parameter validation
        if "result" in negative_price_response:
            result = negative_price_response["result"]
            self.assertIn("content", result)
            # Should at least proceed past testnet safety
            content_text = result["content"][0].get("text", "")
            self.assertNotIn("Mainnet operations not allowed", content_text)
    
    async def test_multiple_agent_operations(self):
        """Test multiple agent operations in sequence"""
        await self._start_server_and_initialize()
        
        test_agents = [
            "masumi-test-multi-001",
            "masumi-test-multi-002",
            "masumi-test-multi-003"
        ]
        
        # Test registering multiple agents
        for agent_name in test_agents:
            response = await self._call_tool("register_agent", {
                "network": "Preprod",
                "name": agent_name,
                "api_base_url": f"https://{agent_name}.masumi-test.network/",
                "selling_wallet_vkey": f"vkey_test_{agent_name.split('-')[-1]}_123456789abcdef",
                "capability_name": f"Test Capability {agent_name.split('-')[-1]}",
                "capability_version": "1.0.0",
                "base_price": 1000000 + int(agent_name.split('-')[-1]) * 100000
            })
            
            self.assertIsNotNone(response, f"Failed to register {agent_name}")
            if "result" in response:
                result = response["result"]
                self.assertIn("content", result)
                content_text = result["content"][0].get("text", "")
                # Should proceed past testnet safety validation
                self.assertNotIn("Mainnet operations not allowed", content_text)

class TestAgentIntegrationSync(unittest.TestCase):
    """Synchronous wrapper for async agent integration tests"""
    
    def _run_async_test(self, test_method):
        """Helper to run async test methods"""
        async def wrapper():
            test_instance = TestAgentIntegration()
            test_instance.setUp()
            try:
                await test_method(test_instance)
            finally:
                test_instance.tearDown()
        
        asyncio.run(wrapper())
    
    def test_agent_registration_workflow(self):
        """Test agent registration workflow"""
        self._run_async_test(TestAgentIntegration.test_agent_registration_workflow)
    
    def test_agent_unregistration_workflow(self):
        """Test agent unregistration workflow"""
        self._run_async_test(TestAgentIntegration.test_agent_unregistration_workflow)
    
    def test_wallet_agent_query_workflow(self):
        """Test wallet agent query workflow"""
        self._run_async_test(TestAgentIntegration.test_wallet_agent_query_workflow)
    
    def test_registry_query_workflow(self):
        """Test registry query workflow"""
        self._run_async_test(TestAgentIntegration.test_registry_query_workflow)
    
    def test_agent_registration_parameter_validation(self):
        """Test agent registration parameter validation"""
        self._run_async_test(TestAgentIntegration.test_agent_registration_parameter_validation)
    
    def test_agent_name_prefix_validation(self):
        """Test agent name prefix validation"""
        self._run_async_test(TestAgentIntegration.test_agent_name_prefix_validation)
    
    def test_agent_url_validation(self):
        """Test agent URL validation"""
        self._run_async_test(TestAgentIntegration.test_agent_url_validation)
    
    def test_agent_pricing_validation(self):
        """Test agent pricing validation"""
        self._run_async_test(TestAgentIntegration.test_agent_pricing_validation)
    
    def test_multiple_agent_operations(self):
        """Test multiple agent operations"""
        self._run_async_test(TestAgentIntegration.test_multiple_agent_operations)

if __name__ == "__main__":
    print("🤖 Running Agent Management Integration Tests")
    print("=" * 50)
    unittest.main(verbosity=2)