#!/usr/bin/env python3
"""
Simple MCP client to test the Masumi MCP Server.
"""

import asyncio
import subprocess
import json
import sys
from typing import Any, Dict

class MCPClient:
    def __init__(self):
        self.server_process = None
        self.request_id = 0
    
    async def start_server(self):
        """Start the MCP server process"""
        self.server_process = await asyncio.create_subprocess_exec(
            sys.executable, 'server.py',
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={'PYTHONPATH': './'}
        )
        print("🚀 MCP Server started")
    
    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request to the server"""
        if not self.server_process:
            raise RuntimeError("Server not started")
        
        self.request_id += 1
        request = {
            'jsonrpc': '2.0',
            'id': self.request_id,
            'method': method,
            'params': params or {}
        }
        
        request_json = json.dumps(request) + '\n'
        self.server_process.stdin.write(request_json.encode())
        await self.server_process.stdin.drain()
        
        # Read response
        response_line = await self.server_process.stdout.readline()
        if response_line:
            try:
                response = json.loads(response_line.decode())
                return response
            except json.JSONDecodeError as e:
                print(f"Failed to parse response: {e}")
                print(f"Raw response: {response_line}")
                return {"error": "Invalid JSON response"}
        else:
            return {"error": "No response from server"}
    
    async def initialize(self):
        """Initialize the MCP connection"""
        response = await self.send_request('initialize', {
            'protocolVersion': '2024-11-05',
            'capabilities': {},
            'clientInfo': {'name': 'test-client', 'version': '1.0.0'}
        })
        
        if 'error' not in response:
            print("✅ MCP connection initialized")
            return True
        else:
            print(f"❌ Failed to initialize: {response}")
            return False
    
    async def list_tools(self):
        """List available tools"""
        response = await self.send_request('tools/list', {})
        if 'result' in response and 'tools' in response['result']:
            tools = response['result']['tools']
            print(f"\n📋 Available Tools ({len(tools)}):")
            for tool in tools:
                print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
            return tools
        else:
            print(f"❌ Failed to list tools: {response}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]):
        """Call a specific tool"""
        response = await self.send_request('tools/call', {
            'name': tool_name,
            'arguments': arguments
        })
        
        if 'result' in response:
            result = response['result']
            print(f"\n🔧 Tool '{tool_name}' result:")
            if 'content' in result:
                for content in result['content']:
                    if content['type'] == 'text':
                        print(content['text'])
            return result
        else:
            print(f"❌ Tool call failed: {response}")
            return None
    
    async def cleanup(self):
        """Clean up the server process"""
        if self.server_process:
            self.server_process.terminate()
            await self.server_process.wait()
            print("🛑 Server stopped")

async def main():
    """Main test function"""
    client = MCPClient()
    
    try:
        # Start server and initialize
        await client.start_server()
        await asyncio.sleep(1)  # Give server time to start
        
        if not await client.initialize():
            return
        
        # List available tools
        tools = await client.list_tools()
        
        if tools:
            # Test a simple tool (list_agents)
            print("\n🧪 Testing list_agents tool...")
            await client.call_tool('list_agents', {})
            
            # Test query_payments with testnet safety
            print("\n🧪 Testing query_payments tool with testnet safety...")
            await client.call_tool('query_payments', {
                'network': 'Preprod',
                'limit': 5
            })
            
            # Test mainnet safety (should fail)
            print("\n🧪 Testing mainnet safety validation...")
            await client.call_tool('query_payments', {
                'network': 'Mainnet',
                'limit': 5
            })
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        await client.cleanup()

if __name__ == "__main__":
    print("🧪 MCP Client Test")
    print("=" * 50)
    asyncio.run(main())