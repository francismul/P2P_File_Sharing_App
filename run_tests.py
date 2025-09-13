#!/usr/bin/env python3
"""
Test runner for P2P File Sharing App
Runs all unit tests and generates a test report
"""

import unittest
import sys
import os
from datetime import datetime


def run_tests():
    """Run all unit tests and return results"""
    # Discover all tests in the tests directory
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


def generate_report(result):
    """Generate a test report"""
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors

    report = f"""
{'='*60}
P2P FILE SHARING APP - TEST REPORT
{'='*60}
Test Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY:
--------
Total Tests: {total_tests}
Passed: {passed}
Failed: {failures}
Errors: {errors}
Success Rate: {(passed/total_tests*100):.1f}%

DETAILED RESULTS:
-----------------
"""

    if result.failures:
        report += "\nFAILURES:\n"
        for test, traceback in result.failures:
            report += f"- {test}\n"

    if result.errors:
        report += "\nERRORS:\n"
        for test, traceback in result.errors:
            report += f"- {test}\n"

    if passed == total_tests:
        report += "\n🎉 ALL TESTS PASSED! 🎉\n"
    else:
        report += "\n⚠️  SOME TESTS FAILED - PLEASE REVIEW ⚠️\n"

    report += "="*60

    return report


def main():
    """Main function to run tests and generate report"""
    print("Running P2P File Sharing App Tests...")
    print("="*60)

    try:
        result = run_tests()
        report = generate_report(result)

        print("\n" + report)

        # Save report to file
        with open('test_report.txt', 'w') as f:
            f.write(report)

        print("\nTest report saved to: test_report.txt")

        # Return appropriate exit code
        return 0 if result.wasSuccessful() else 1

    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())