#!/usr/bin/env python3
"""Run all miner-v2 tests."""
import sys, unittest
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT))

def run_all_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_dir = Path(__file__).parent
    for test_file in sorted(test_dir.glob("test_*.py")):
        if test_file.name == "__init__.py":
            continue
        module_name = f"tests.{test_file.stem}"
        try:
            __import__(module_name)
            module = sys.modules[module_name]
            tests = loader.loadTestsFromModule(module)
            suite.addTests(tests)
        except Exception as e:
            print(f"Error loading {test_file.name}: {e}")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    print(f"Total: {result.testsRun} tests")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 50)
    
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
