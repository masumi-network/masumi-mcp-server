#!/usr/bin/env python3
"""
Test runner for all Masumi MCP Server tests.
"""

import sys
import unittest
import importlib.util
from pathlib import Path

def load_test_module(module_path):
    """Load a test module from file path"""
    spec = importlib.util.spec_from_file_location("test_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def discover_and_run_tests():
    """Discover and run all tests in the tests directory"""
    tests_dir = Path(__file__).parent
    test_files = [
        "test_mcp_connection.py",
        "test_tools_comprehensive.py", 
        "test_testnet_safety.py",
        "test_agent_integration.py"
    ]
    
    print("🧪 Masumi MCP Server Test Suite")
    print("=" * 60)
    print(f"Running tests from: {tests_dir}")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests from each file
    for test_file in test_files:
        test_path = tests_dir / test_file
        if test_path.exists():
            print(f"📋 Loading tests from {test_file}...")
            try:
                # Load the module
                module = load_test_module(test_path)
                
                # Find test classes ending with 'Sync' for synchronous execution
                for name in dir(module):
                    obj = getattr(module, name)
                    if (isinstance(obj, type) and 
                        issubclass(obj, unittest.TestCase) and 
                        name.endswith('Sync')):
                        tests = loader.loadTestsFromTestCase(obj)
                        suite.addTests(tests)
                        print(f"  ✅ Added {tests.countTestCases()} tests from {name}")
                        
            except Exception as e:
                print(f"  ❌ Failed to load {test_file}: {e}")
        else:
            print(f"  ⚠️  Test file not found: {test_file}")
    
    # Run the tests
    print("\n" + "=" * 60)
    print("🚀 Running Tests...")
    print("=" * 60)
    
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip() if 'AssertionError:' in traceback else 'See details above'}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip() if 'Exception:' in traceback else 'See details above'}")
    
    if result.wasSuccessful():
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {len(result.failures + result.errors)} test(s) failed")
        return 1

def run_specific_test_suite(suite_name):
    """Run a specific test suite"""
    test_files = {
        "connection": "test_mcp_connection.py",
        "tools": "test_tools_comprehensive.py",
        "safety": "test_testnet_safety.py", 
        "agent": "test_agent_integration.py",
        "simple": "simple_test.py"
    }
    
    if suite_name not in test_files:
        print(f"❌ Unknown test suite: {suite_name}")
        print(f"Available suites: {', '.join(test_files.keys())}")
        return 1
    
    test_file = test_files[suite_name]
    tests_dir = Path(__file__).parent
    test_path = tests_dir / test_file
    
    if not test_path.exists():
        print(f"❌ Test file not found: {test_path}")
        return 1
    
    print(f"🧪 Running {suite_name} test suite: {test_file}")
    print("=" * 50)
    
    if suite_name == "simple":
        # Run simple_test.py directly
        import subprocess
        result = subprocess.run([sys.executable, str(test_path)], 
                              cwd=tests_dir.parent,
                              env={"PYTHONPATH": str(tests_dir.parent)})
        return result.returncode
    else:
        # Run unittest tests
        module = load_test_module(test_path)
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Find sync test classes
        for name in dir(module):
            obj = getattr(module, name)
            if (isinstance(obj, type) and 
                issubclass(obj, unittest.TestCase) and 
                name.endswith('Sync')):
                tests = loader.loadTestsFromTestCase(obj)
                suite.addTests(tests)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test suite
        suite_name = sys.argv[1].lower()
        exit_code = run_specific_test_suite(suite_name)
    else:
        # Run all tests
        exit_code = discover_and_run_tests()
    
    sys.exit(exit_code)