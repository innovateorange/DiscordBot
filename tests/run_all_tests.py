#!/usr/bin/env python3
# run_all_tests.py
# Comprehensive test runner for Discord bot test suites
# Runs all test files and generates detailed reports

import unittest
import sys
import os
import time
import argparse
from io import StringIO
import importlib.util

# Add the parent directory to the path so we can import bot.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test modules to run
TEST_MODULES = [
    'bot_test',
    'test_bot_extended', 
    'test_bot_performance',
    'test_bot_integration'
]

class ColoredTextTestResult(unittest.TextTestResult):
    """Custom test result class with colored output"""
    
    def __init__(self, stream, descriptions, verbosity, use_colors=True):
        super().__init__(stream, descriptions, verbosity)
        self.success_count = 0
        self.use_colors = use_colors
    
    def addSuccess(self, test):
        super().addSuccess(test)
        self.success_count += 1
        if self.verbosity > 1:
            if self.use_colors:
                self.stream.writeln(f"\033[92m✓ {self.getDescription(test)}\033[0m")
            else:
                self.stream.writeln(f"✓ {self.getDescription(test)}")
    
    def addError(self, test, err):
        super().addError(test, err)
        if self.verbosity > 1:
            if self.use_colors:
                self.stream.writeln(f"\033[91m✗ {self.getDescription(test)} - ERROR\033[0m")
            else:
                self.stream.writeln(f"✗ {self.getDescription(test)} - ERROR")
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.verbosity > 1:
            if self.use_colors:
                self.stream.writeln(f"\033[91m✗ {self.getDescription(test)} - FAILED\033[0m")
            else:
                self.stream.writeln(f"✗ {self.getDescription(test)} - FAILED")
    
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if self.verbosity > 1:
            if self.use_colors:
                self.stream.writeln(f"\033[93m- {self.getDescription(test)} - SKIPPED\033[0m")
            else:
                self.stream.writeln(f"- {self.getDescription(test)} - SKIPPED")

class ColoredTextTestRunner(unittest.TextTestRunner):
    """Custom test runner with colored output"""
    resultclass = ColoredTextTestResult


def load_test_module(module_name):
    """Load a test module by name"""
    try:
        spec = importlib.util.spec_from_file_location(
            module_name, 
            os.path.join(os.path.dirname(__file__), f"{module_name}.py")
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load spec for {module_name}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"\033[91mError loading {module_name}: {e}\033[0m")
        return None


def run_test_suite(module_name, verbosity: int = 2, pattern: str | None = None, cli_args=None):
    """Run tests for a specific module"""
    print(f"\n\033[94m{'='*60}\033[0m")
    print(f"\033[94mRunning tests from: {module_name}\033[0m")
    print(f"\033[94m{'='*60}\033[0m")
    
    module = load_test_module(module_name)
    if not module:
        return None
    
    # Create test loader
    loader = unittest.TestLoader()
    
    # Load tests from module
    if pattern:
        suite = loader.loadTestsFromModule(module)
        # Filter tests by pattern
        filtered_suite = unittest.TestSuite()
        for test_group in suite:
            for test in test_group:
                if pattern.lower() in str(test).lower():
                    filtered_suite.addTest(test)
        suite = filtered_suite
    else:
        suite = loader.loadTestsFromModule(module)
    
    # Run tests
    use_colors = not getattr(cli_args, 'no_color', False)
    runner = ColoredTextTestRunner(verbosity=verbosity, stream=sys.stdout, use_colors=use_colors)
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # Print summary for this module
    print(f"\n\033[96mSummary for {module_name}:\033[0m")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Successes: {getattr(result, 'success_count', result.testsRun - len(result.failures) - len(result.errors))}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Skipped: {len(result.skipped)}")
    print(f"  Time: {end_time - start_time:.2f}s")
    
    return result


def run_all_tests(verbosity=2, pattern=None, modules=None, args=None):
    """Run all test suites"""
    print("\033[95m" + "="*80 + "\033[0m")
    print("\033[95mDiscord Bot - Comprehensive Test Suite\033[0m")
    print("\033[95m" + "="*80 + "\033[0m")
    
    if modules is None:
        modules = TEST_MODULES
    
    total_tests = 0
    total_successes = 0
    total_failures = 0
    total_errors = 0
    total_skipped = 0
    start_time = time.time()
    
    results = {}
    
    for module_name in modules:
        result = run_test_suite(module_name, verbosity, pattern, args)
        if result:
            results[module_name] = result
            total_tests += result.testsRun
            total_successes += getattr(result, 'success_count', 
                                     result.testsRun - len(result.failures) - len(result.errors))
            total_failures += len(result.failures)
            total_errors += len(result.errors)
            total_skipped += len(result.skipped)
    
    end_time = time.time()
    
    # Store results for report generation
    run_all_tests._last_results = results
    
    # Print overall summary
    print(f"\n\033[95m{'='*80}\033[0m")
    print(f"\033[95mOVERALL TEST SUMMARY\033[0m")
    print(f"\033[95m{'='*80}\033[0m")
    
    print(f"\033[96mTotal modules tested: {len(results)}\033[0m")
    print(f"\033[96mTotal tests run: {total_tests}\033[0m")
    print(f"\033[92mSuccesses: {total_successes}\033[0m")
    print(f"\033[91mFailures: {total_failures}\033[0m")
    print(f"\033[91mErrors: {total_errors}\033[0m")
    print(f"\033[93mSkipped: {total_skipped}\033[0m")
    print(f"\033[96mTotal time: {end_time - start_time:.2f}s\033[0m")
    
    # Calculate success rate
    if total_tests > 0:
        success_rate = (total_successes / total_tests) * 100
        print(f"\033[96mSuccess rate: {success_rate:.1f}%\033[0m")
        
        if success_rate == 100:
            print(f"\n\033[92m🎉 ALL TESTS PASSED! 🎉\033[0m")
        elif success_rate >= 90:
            print(f"\n\033[93m⚠️  Most tests passed, but some issues found\033[0m")
        else:
            print(f"\n\033[91m❌ Significant test failures detected\033[0m")
    
    # Print detailed failure information
    if total_failures > 0 or total_errors > 0:
        print(f"\n\033[91mDETAILED FAILURE/ERROR INFORMATION:\033[0m")
        print(f"\033[91m{'='*80}\033[0m")
        
        for module_name, result in results.items():
            if result.failures or result.errors:
                print(f"\n\033[91mModule: {module_name}\033[0m")
                
                for test, traceback in result.failures:
                    print(f"\033[91mFAILURE: {test}\033[0m")
                    print(f"  {traceback}")
                
                for test, traceback in result.errors:
                    print(f"\033[91mERROR: {test}\033[0m")
                    print(f"  {traceback}")
    
    return total_failures + total_errors == 0


def generate_test_report(results, filename="test_report.txt"):
    """Generate a detailed test report file"""
    try:
        with open(filename, 'w') as f:
            f.write("Discord Bot - Test Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for module_name, result in results.items():
                f.write(f"Module: {module_name}\n")
                f.write("-" * 30 + "\n")
                f.write(f"Tests run: {result.testsRun}\n")
                f.write(f"Failures: {len(result.failures)}\n")
                f.write(f"Errors: {len(result.errors)}\n")
                f.write(f"Skipped: {len(result.skipped)}\n\n")
                
                if result.failures:
                    f.write("FAILURES:\n")
                    for test, traceback in result.failures:
                        f.write(f"- {test}\n")
                        f.write(f"  {traceback}\n")
                
                if result.errors:
                    f.write("ERRORS:\n")
                    for test, traceback in result.errors:
                        f.write(f"- {test}\n")
                        f.write(f"  {traceback}\n")
                
                f.write("\n")
        return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Run Discord bot tests")
    parser.add_argument('-v', '--verbosity', type=int, default=2, choices=[0, 1, 2],
                       help='Test output verbosity (0=quiet, 1=normal, 2=verbose)')
    parser.add_argument('-p', '--pattern', type=str,
                       help='Run only tests matching this pattern')
    parser.add_argument('-m', '--modules', nargs='+', choices=TEST_MODULES,
                       help='Run only specific test modules')
    parser.add_argument('-r', '--report', action='store_true',
                       help='Generate a test report file')
    parser.add_argument('--no-color', action='store_true',
                       help='Disable colored output')
    parser.add_argument('--performance-only', action='store_true',
                       help='Run only performance tests')
    parser.add_argument('--integration-only', action='store_true',
                       help='Run only integration tests')
    
    args = parser.parse_args()
    
    # Determine which modules to run
    modules_to_run = TEST_MODULES
    if args.modules:
        modules_to_run = args.modules
    elif args.performance_only:
        modules_to_run = ['test_bot_performance']
    elif args.integration_only:
        modules_to_run = ['test_bot_integration']
    
    # Run tests
    success = run_all_tests(
        verbosity=args.verbosity,
        pattern=args.pattern,
        modules=modules_to_run
    )
    
    # Generate report if requested
    if args.report:
        print(f"\n\033[96mGenerating test report...\033[0m")
        # Get results from the run_all_tests function
        if hasattr(run_all_tests, '_last_results'):
            report_success = generate_test_report(run_all_tests._last_results)
            if report_success:
                print(f"\033[96mReport saved to: test_report.txt\033[0m")
            else:
                print(f"\033[91mFailed to generate report\033[0m")
        else:
            print(f"\033[91mNo test results available for report generation\033[0m")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 