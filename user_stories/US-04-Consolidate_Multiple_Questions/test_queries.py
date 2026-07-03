#!/usr/bin/env python3
"""
Integration test runner for US-04: Consolidate Multiple Questions

Tests the consolidation logic with realistic researcher queries.
Validates that questions are correctly detected, analyzed, and consolidated.

Usage:
    python test_queries.py                  # Run all tests
    python test_queries.py --verbose        # Verbose output
    python test_queries.py --test CONSOLIDATE_001  # Run specific test
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any

# Add implementation to path
sys.path.insert(0, str(Path(__file__).parent))

from implementation.query_consolidator import consolidate_multiple_questions


class TestResults:
    """Track test results"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.failures = []

    def add_pass(self, test_id: str):
        self.passed += 1
        print(f"  [PASS] {test_id}")

    def add_fail(self, test_id: str, reason: str):
        self.failed += 1
        self.failures.append((test_id, reason))
        print(f"  [FAIL] {test_id}: {reason}")

    def add_skip(self, test_id: str, reason: str = ""):
        self.skipped += 1
        print(f"  [SKIP] {test_id} (skipped): {reason}")

    def print_summary(self):
        """Print test results summary"""
        total = self.passed + self.failed + self.skipped
        print("\n" + "=" * 70)
        print(f"TEST RESULTS: {self.passed}/{total} passed")
        print("=" * 70)

        if self.passed > 0:
            print(f"[PASS] Passed: {self.passed}")
        if self.failed > 0:
            print(f"[FAIL] Failed: {self.failed}")
        if self.skipped > 0:
            print(f"[SKIP] Skipped: {self.skipped}")

        if self.failures:
            print("\nFailures:")
            for test_id, reason in self.failures:
                print(f"  - {test_id}: {reason}")

        return self.failed == 0


def load_test_queries(verbose: bool = False) -> List[Dict[str, Any]]:
    """Load test queries from JSON file"""
    test_file = Path(__file__).parent / "test_queries.json"

    if not test_file.exists():
        print(f"Error: test_queries.json not found at {test_file}")
        sys.exit(1)

    with open(test_file, 'r') as f:
        data = json.load(f)

    if verbose:
        print(f"Loaded {len(data['tests'])} test cases from {test_file}")

    return data['tests']


def run_test(test: Dict[str, Any], verbose: bool = False) -> tuple[bool, str]:
    """
    Run a single test case

    Returns:
        (passed, message)
    """
    test_id = test.get('id', 'UNKNOWN')
    query = test.get('query', '')
    expected_result = test.get('expected_result')
    has_multiple = test.get('has_multiple_questions')
    should_consolidate = test.get('should_consolidate')
    expected_count = test.get('expected_questions_count')

    try:
        # Run consolidation
        result = consolidate_multiple_questions(query)

        # Verify results
        errors = []

        # Check multiple questions detection
        if has_multiple is not None:
            if result.has_multiple_questions != has_multiple:
                errors.append(
                    f"has_multiple={result.has_multiple_questions}, "
                    f"expected={has_multiple}"
                )

        # Check consolidation decision
        if should_consolidate is not None:
            if result.should_consolidate != should_consolidate:
                errors.append(
                    f"consolidate={result.should_consolidate}, "
                    f"expected={should_consolidate}"
                )

        # Check exact question count
        if expected_count is not None:
            if len(result.questions) != expected_count:
                errors.append(
                    f"questions={len(result.questions)}, "
                    f"expected={expected_count}"
                )

        # Check minimum question count
        expected_min = test.get('expected_questions_count_min')
        if expected_min is not None:
            if len(result.questions) < expected_min:
                errors.append(
                    f"questions={len(result.questions)}, "
                    f"min={expected_min}"
                )

        # Check maximum question count
        expected_max = test.get('expected_questions_count_max')
        if expected_max is not None:
            if len(result.questions) > expected_max:
                errors.append(
                    f"questions={len(result.questions)}, "
                    f"max={expected_max}"
                )

        if errors:
            return False, ", ".join(errors)

        if verbose:
            print(f"\n    Query: {query[:60]}...")
            print(f"    Questions: {len(result.questions)}")
            print(f"    Consolidate: {result.should_consolidate}")
            print(f"    Score: {result.consolidation_score:.2f}")

        return True, ""

    except Exception as e:
        return False, f"Exception: {str(e)}"


def run_test_suite(test_filter: str = None, verbose: bool = False) -> bool:
    """
    Run all tests or filter by test ID

    Args:
        test_filter: Optional test ID to run only that test
        verbose: Enable verbose output

    Returns:
        True if all tests passed, False otherwise
    """
    tests = load_test_queries(verbose)
    results = TestResults()

    # Filter tests if requested
    if test_filter:
        tests = [t for t in tests if t['id'] == test_filter]
        if not tests:
            print(f"No test found with ID: {test_filter}")
            return False

    print(f"\nRunning {len(tests)} test case(s)...\n")

    # Group tests by category
    categories = {}
    for test in tests:
        expected = test.get('expected_result', 'unknown')
        if expected not in categories:
            categories[expected] = []
        categories[expected].append(test)

    # Run tests by category
    for category in sorted(categories.keys()):
        print(f"\n{category.upper()} Tests:")

        for test in categories[category]:
            test_id = test['id']
            name = test.get('name', 'Unknown')

            passed, error = run_test(test, verbose)

            if passed:
                results.add_pass(test_id)
            else:
                results.add_fail(test_id, error)

            if verbose and name:
                print(f"    {name}")

    # Print summary
    success = results.print_summary()

    return success


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Integration tests for US-04: Consolidate Multiple Questions'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--test',
        help='Run specific test by ID'
    )

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("US-04 Integration Test Suite")
    print("Consolidate Multiple Questions")
    print("=" * 70)

    success = run_test_suite(
        test_filter=args.test,
        verbose=args.verbose
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
