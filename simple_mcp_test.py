#!/usr/bin/env python3
"""
Simple MCP server test using subprocess and manual JSON-RPC.
"""

import asyncio
import json
import subprocess
import sys

async def test_mcp_connection():
    """Test basic MCP server connection and tool listing"""
    print("🧪 Simple MCP Connection Test")
    print("=" * 50)
    
    # Start the server
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "server.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env={"PYTHONPATH": "./"}
    )
    
    print("🚀 MCP Server started")
    
    try:
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "simple-test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        request_line = json.dumps(init_request) + "\n"
        proc.stdin.write(request_line.encode())
        await proc.stdin.drain()
        
        # Read initialization response
        response_line = await proc.stdout.readline()
        if response_line:
            response = json.loads(response_line.decode())
            if 'result' in response:
                print("✅ Server initialized successfully")
                server_info = response['result']
                print(f"📋 Server: {server_info.get('serverInfo', {}).get('name', 'Unknown')}")
                
                # List tools
                tools_request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {}
                }
                
                request_line = json.dumps(tools_request) + "\n"
                proc.stdin.write(request_line.encode())
                await proc.stdin.drain()
                
                # Read tools response
                tools_response_line = await proc.stdout.readline()
                if tools_response_line:
                    tools_response = json.loads(tools_response_line.decode())
                    if 'result' in tools_response and 'tools' in tools_response['result']:
                        tools = tools_response['result']['tools']
                        print(f"\n📋 Available Tools ({len(tools)}):")
                        for tool in tools:
                            name = tool.get('name', 'Unknown')
                            description = tool.get('description', 'No description')
                            print(f"  - {name}")
                            if description:
                                print(f"    {description}")
                        
                        # Test a tool call (list_agents)
                        if any(t.get('name') == 'list_agents' for t in tools):
                            print("\n🧪 Testing list_agents tool...")
                            
                            tool_request = {
                                "jsonrpc": "2.0",
                                "id": 3,
                                "method": "tools/call",
                                "params": {
                                    "name": "list_agents",
                                    "arguments": {}
                                }
                            }
                            
                            request_line = json.dumps(tool_request) + "\n"
                            proc.stdin.write(request_line.encode())
                            await proc.stdin.drain()
                            
                            # Read tool response
                            tool_response_line = await proc.stdout.readline()
                            if tool_response_line:
                                tool_response = json.loads(tool_response_line.decode())
                                if 'result' in tool_response:
                                    result = tool_response['result']
                                    print("✅ list_agents executed successfully")
                                    if 'content' in result:
                                        for content in result['content']:
                                            if content.get('type') == 'text':
                                                text = content.get('text', '')
                                                print(f"Result: {text[:200]}...")
                                else:
                                    print(f"❌ Tool call failed: {tool_response}")
                        
                        # Test testnet safety
                        if any(t.get('name') == 'query_payments' for t in tools):
                            print("\n🧪 Testing testnet safety with query_payments...")
                            
                            safety_request = {
                                "jsonrpc": "2.0",
                                "id": 4,
                                "method": "tools/call",
                                "params": {
                                    "name": "query_payments",
                                    "arguments": {
                                        "network": "Mainnet",
                                        "limit": 5
                                    }
                                }
                            }
                            
                            request_line = json.dumps(safety_request) + "\n"
                            proc.stdin.write(request_line.encode())
                            await proc.stdin.drain()
                            
                            # Read safety test response
                            safety_response_line = await proc.stdout.readline()
                            if safety_response_line:
                                safety_response = json.loads(safety_response_line.decode())
                                if 'result' in safety_response:
                                    result = safety_response['result']
                                    print("✅ Testnet safety check result:")
                                    if 'content' in result:
                                        for content in result['content']:
                                            if content.get('type') == 'text':
                                                text = content.get('text', '')
                                                print(f"Safety response: {text}")
                        
                        print("\n🎉 MCP connection test completed successfully!")
                        
                    else:
                        print(f"❌ Failed to list tools: {tools_response}")
                else:
                    print("❌ No response to tools/list request")
            else:
                print(f"❌ Initialization failed: {response}")
        else:
            print("❌ No response to initialization request")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    finally:
        # Clean up
        proc.terminate()
        await proc.wait()
        print("🛑 Server stopped")

if __name__ == "__main__":
    asyncio.run(test_mcp_connection())