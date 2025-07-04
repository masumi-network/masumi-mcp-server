#!/usr/bin/env python3
"""
Test MCP server using the official MCP client library.
"""

import asyncio
import subprocess
import sys
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
from mcp.server.models import StdioServerParameters

async def test_mcp_server():
    """Test the MCP server using official client"""
    print("🧪 Testing MCP Server with Official Client")
    print("=" * 50)
    
    # Start the server process
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["server.py"],
        env={"PYTHONPATH": "./"}
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            print("✅ MCP session initialized")
            
            # List available tools
            tools_result = await session.list_tools()
            tools = tools_result.tools
            print(f"\n📋 Available Tools ({len(tools)}):")
            
            for tool in tools:
                print(f"  - {tool.name}")
                if hasattr(tool, 'description') and tool.description:
                    print(f"    Description: {tool.description}")
                print()
            
            # Test list_agents tool
            if any(tool.name == 'list_agents' for tool in tools):
                print("🧪 Testing list_agents tool...")
                try:
                    result = await session.call_tool('list_agents', {})
                    print("✅ list_agents result:")
                    for content in result.content:
                        if hasattr(content, 'text'):
                            print(content.text[:500] + "..." if len(content.text) > 500 else content.text)
                except Exception as e:
                    print(f"❌ list_agents failed: {e}")
            
            # Test query_payments with testnet parameters
            if any(tool.name == 'query_payments' for tool in tools):
                print("\n🧪 Testing query_payments with testnet parameters...")
                try:
                    result = await session.call_tool('query_payments', {
                        'network': 'Preprod',
                        'limit': 5
                    })
                    print("✅ query_payments result:")
                    for content in result.content:
                        if hasattr(content, 'text'):
                            print(content.text[:300] + "..." if len(content.text) > 300 else content.text)
                except Exception as e:
                    print(f"❌ query_payments failed: {e}")
            
            # Test mainnet safety validation
            if any(tool.name == 'query_payments' for tool in tools):
                print("\n🧪 Testing mainnet safety validation (should fail)...")
                try:
                    result = await session.call_tool('query_payments', {
                        'network': 'Mainnet',
                        'limit': 5
                    })
                    print("✅ Mainnet safety test result:")
                    for content in result.content:
                        if hasattr(content, 'text'):
                            print(content.text)
                except Exception as e:
                    print(f"❌ Mainnet test failed: {e}")
            
            # Test agent management tools
            agent_tools = ['register_agent', 'unregister_agent', 'get_agents_by_wallet']
            for tool_name in agent_tools:
                if any(tool.name == tool_name for tool in tools):
                    print(f"\n🧪 Testing {tool_name} with invalid mainnet parameters...")
                    try:
                        if tool_name == 'register_agent':
                            result = await session.call_tool(tool_name, {
                                'network': 'Mainnet',
                                'name': 'test-agent',
                                'api_base_url': 'https://test.com',
                                'selling_wallet_vkey': 'vkey123',
                                'capability_name': 'Test',
                                'capability_version': '1.0.0',
                                'base_price': 1000000
                            })
                        elif tool_name == 'unregister_agent':
                            result = await session.call_tool(tool_name, {
                                'agent_identifier': 'test-agent',
                                'network': 'Mainnet'
                            })
                        elif tool_name == 'get_agents_by_wallet':
                            result = await session.call_tool(tool_name, {
                                'network': 'Mainnet',
                                'wallet_vkey': 'test_wallet'
                            })
                        
                        print(f"✅ {tool_name} safety validation result:")
                        for content in result.content:
                            if hasattr(content, 'text'):
                                print(content.text)
                    except Exception as e:
                        print(f"❌ {tool_name} test failed: {e}")
            
            print("\n🎉 MCP Server test completed!")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())