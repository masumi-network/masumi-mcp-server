#!/usr/bin/env python3
"""
Test MCP server connection and basic functionality.
"""

import asyncio
import json
import subprocess
import sys
import unittest
from pathlib import Path

class TestMCPConnection(unittest.TestCase):
    """Test MCP server connection and protocol compliance"""
    
    def setUp(self):
        """Set up test environment"""
        self.server_process = None
        
    def tearDown(self):
        """Clean up after tests"""
        if self.server_process:
            self.server_process.terminate()
    
    async def _start_server(self):
        """Start the MCP server process"""
        self.server_process = await asyncio.create_subprocess_exec(
            sys.executable, "server.py",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={"PYTHONPATH": "./"}
        )
        # Give server time to start
        await asyncio.sleep(0.5)
        return self.server_process
    
    async def _send_request(self, request_dict):
        """Send JSON-RPC request to server"""
        if not self.server_process:
            raise RuntimeError("Server not started")
        
        request_json = json.dumps(request_dict) + "\n"
        self.server_process.stdin.write(request_json.encode())
        await self.server_process.stdin.drain()
        
        # Read response
        response_line = await self.server_process.stdout.readline()
        if response_line:
            return json.loads(response_line.decode())
        return None
    
    async def test_server_initialization(self):
        """Test server initialization sequence"""
        await self._start_server()
        
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = await self._send_request(init_request)
        
        # Verify response
        self.assertIsNotNone(response)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], 1)
        self.assertIn("result", response)
        
        result = response["result"]
        self.assertEqual(result["protocolVersion"], "2024-11-05")
        self.assertIn("capabilities", result)
        self.assertIn("serverInfo", result)
        self.assertEqual(result["serverInfo"]["name"], "Masumi Agent Manager")
    
    async def test_tools_list(self):
        """Test tools listing functionality"""
        await self._start_server()
        
        # Initialize server
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
        
        # Request tools list
        tools_response = await self._send_request({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        })
        
        # Verify tools response
        self.assertIsNotNone(tools_response)
        self.assertIn("result", tools_response)
        self.assertIn("tools", tools_response["result"])
        
        tools = tools_response["result"]["tools"]
        self.assertEqual(len(tools), 11)  # All 11 tools should be available
        
        # Check for expected tools
        tool_names = [tool["name"] for tool in tools]
        expected_tools = [
            "list_agents", "get_agent_input_schema", "hire_agent",
            "check_job_status", "get_job_full_result", "query_payments",
            "get_purchase_history", "query_registry", "register_agent",
            "unregister_agent", "get_agents_by_wallet"
        ]
        
        for expected_tool in expected_tools:
            self.assertIn(expected_tool, tool_names)
    
    async def test_testnet_safety_validation(self):
        """Test testnet safety validation in tools"""
        await self._start_server()
        
        # Initialize server
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
        
        # Test mainnet rejection
        mainnet_response = await self._send_request({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "query_payments",
                "arguments": {
                    "network": "Mainnet",
                    "limit": 5
                }
            }
        })
        
        # Should succeed (tool executes) but return testnet safety error
        self.assertIsNotNone(mainnet_response)
        if "result" in mainnet_response:
            result = mainnet_response["result"]
            if "content" in result and len(result["content"]) > 0:
                content_text = result["content"][0].get("text", "")
                self.assertIn("Mainnet operations not allowed", content_text)

def run_async_test(test_method):
    """Helper to run async test methods"""
    async def wrapper(self):
        await test_method(self)
    return wrapper

class TestMCPConnectionSync(unittest.TestCase):
    """Synchronous wrapper for async MCP tests"""
    
    def test_server_initialization(self):
        """Test server initialization"""
        async def test():
            test_instance = TestMCPConnection()
            test_instance.setUp()
            try:
                await test_instance.test_server_initialization()
            finally:
                test_instance.tearDown()
        
        asyncio.run(test())
    
    def test_tools_list(self):
        """Test tools listing"""
        async def test():
            test_instance = TestMCPConnection()
            test_instance.setUp()
            try:
                await test_instance.test_tools_list()
            finally:
                test_instance.tearDown()
        
        asyncio.run(test())
    
    def test_testnet_safety(self):
        """Test testnet safety validation"""
        async def test():
            test_instance = TestMCPConnection()
            test_instance.setUp()
            try:
                await test_instance.test_testnet_safety_validation()
            finally:
                test_instance.tearDown()
        
        asyncio.run(test())

if __name__ == "__main__":
    print("🧪 Running MCP Connection Tests")
    print("=" * 50)
    unittest.main(verbosity=2)