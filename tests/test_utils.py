"""
Test utilities for manual testing of Masumi MCP Server tools.
"""

import asyncio
import json
from typing import Any, Dict, List
from mcp.client import Client
from .test_data import ensure_testnet_environment, DEFAULT_TEST_PARAMS

class MCPTestRunner:
    """Utility class for running MCP tool tests"""
    
    def __init__(self, server_path: str = "server.py"):
        self.server_path = server_path
        self.client = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        ensure_testnet_environment()
        self.client = Client(self.server_path)
        await self.client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def list_tools(self) -> List[str]:
        """List all available tools"""
        if not self.client:
            raise ValueError("Client not initialized. Use within async context manager.")
        
        tools = await self.client.list_tools()
        return [tool.name for tool in tools]
    
    async def test_tool_exists(self, tool_name: str) -> bool:
        """Test if a specific tool exists"""
        tools = await self.list_tools()
        exists = tool_name in tools
        print(f"✅ Tool '{tool_name}' exists" if exists else f"❌ Tool '{tool_name}' not found")
        return exists
    
    async def call_tool_safe(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Safely call a tool with error handling"""
        if not self.client:
            raise ValueError("Client not initialized.")
        
        try:
            print(f"🔧 Calling tool '{tool_name}' with params: {json.dumps(params, indent=2)}")
            result = await self.client.call_tool(tool_name, params)
            
            if result and len(result) > 0:
                response_text = result[0].text
                print(f"✅ Tool '{tool_name}' executed successfully")
                print(f"📄 Response (first 500 chars): {response_text[:500]}...")
                return {"success": True, "response": response_text}
            else:
                print(f"⚠️  Tool '{tool_name}' returned empty result")
                return {"success": False, "error": "Empty result"}
                
        except Exception as e:
            print(f"❌ Tool '{tool_name}' failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_tool_with_invalid_params(self, tool_name: str, invalid_params: Dict[str, Any]) -> bool:
        """Test tool with invalid parameters to verify error handling"""
        print(f"🧪 Testing '{tool_name}' with invalid params: {json.dumps(invalid_params, indent=2)}")
        result = await self.call_tool_safe(tool_name, invalid_params)
        
        if not result["success"]:
            print(f"✅ Tool '{tool_name}' correctly rejected invalid parameters")
            return True
        else:
            print(f"⚠️  Tool '{tool_name}' unexpectedly accepted invalid parameters")
            return False

def print_test_header(test_name: str):
    """Print a formatted test header"""
    print("\n" + "="*60)
    print(f"🚀 TESTING: {test_name}")
    print("="*60)

def print_test_result(test_name: str, success: bool, details: str = ""):
    """Print formatted test result"""
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"\n{status}: {test_name}")
    if details:
        print(f"Details: {details}")

async def run_basic_server_test():
    """Run basic server connectivity test"""
    print_test_header("Basic Server Connectivity")
    
    try:
        async with MCPTestRunner() as runner:
            tools = await runner.list_tools()
            print(f"📋 Available tools: {tools}")
            
            expected_tools = ["list_agents", "get_agent_input_schema", "hire_agent", 
                            "check_job_status", "get_job_full_result"]
            
            missing_tools = [tool for tool in expected_tools if tool not in tools]
            
            if missing_tools:
                print_test_result("Basic Server Test", False, f"Missing tools: {missing_tools}")
                return False
            else:
                print_test_result("Basic Server Test", True, f"All {len(tools)} tools available")
                return True
                
    except Exception as e:
        print_test_result("Basic Server Test", False, f"Server connection failed: {str(e)}")
        return False

def create_test_params(base_params: Dict[str, Any], overrides: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create test parameters by merging base params with overrides"""
    params = {**DEFAULT_TEST_PARAMS, **base_params}
    if overrides:
        params.update(overrides)
    return params

# Validation helpers
def validate_response_format(response: str, expected_keys: List[str] = None) -> bool:
    """Validate that response contains expected data structure"""
    try:
        if response.startswith("Error:"):
            return False
            
        # Try to parse as JSON if expected_keys provided
        if expected_keys:
            data = json.loads(response)
            if isinstance(data, list) and len(data) > 0:
                item = data[0]
                missing_keys = [key for key in expected_keys if key not in item]
                if missing_keys:
                    print(f"⚠️  Missing expected keys: {missing_keys}")
                    return False
        
        return True
    except json.JSONDecodeError:
        # Response might be plain text, which is also valid
        return len(response.strip()) > 0

if __name__ == "__main__":
    # Run basic test when script is executed directly
    asyncio.run(run_basic_server_test())