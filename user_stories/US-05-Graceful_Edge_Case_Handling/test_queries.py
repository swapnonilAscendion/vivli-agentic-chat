"""
Test Queries Script for US-05: Graceful Edge Case Handling
Run automated tests against the /chat endpoint

Usage:
    python test_queries.py
    python test_queries.py --server http://localhost:8000
    python test_queries.py --category VALID_QUERIES
    python test_queries.py --category INVALID_BLANK --verbose
"""

import json
import requests
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Tuple
from collections import defaultdict

class TestRunner:
    def __init__(self, server_url: str, verbose: bool = False):
        self.server_url = server_url.rstrip('/')
        self.endpoint = "/chat"
        self.verbose = verbose
        self.results = defaultdict(list)
        self.total = 0
        self.passed = 0
        self.failed = 0

    def load_test_queries(self) -> Dict:
        """Load test queries from JSON file"""
        with open('test_queries.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_query(self, test_id: str, query: str, expected_status: str,
                   description: str, category: str) -> Tuple[bool, str]:
        """Test a single query against the endpoint"""
        self.total += 1

        try:
            response = requests.post(
                f"{self.server_url}{self.endpoint}",
                json={"query": query},
                timeout=10
            )

            if response.status_code != 200:
                result = f"✗ FAIL - HTTP {response.status_code}"
                self.failed += 1
                return False, result

            data = response.json()
            validation_status = data.get('metadata', {}).get('validation_status', 'unknown')

            if validation_status == expected_status:
                result = f"✓ PASS"
                self.passed += 1
                return True, result
            else:
                result = f"✗ FAIL - Expected '{expected_status}', got '{validation_status}'"
                self.failed += 1
                return False, result

        except requests.exceptions.ConnectionError:
            result = f"✗ ERROR - Cannot connect to {self.server_url}"
            self.failed += 1
            return False, result
        except Exception as e:
            result = f"✗ ERROR - {str(e)}"
            self.failed += 1
            return False, result

    def run_category(self, category: str, tests: List[Dict]) -> None:
        """Run all tests in a category"""
        print(f"\n{'='*70}")
        print(f"Testing Category: {category}")
        print(f"{'='*70}\n")

        category_passed = 0
        category_failed = 0

        for test in tests:
            test_id = test['id']
            query = test['query']
            expected_status = test['expected_status']
            description = test['description']

            success, result = self.test_query(
                test_id, query, expected_status, description, category
            )

            if success:
                category_passed += 1
                status_symbol = "✓"
                color_code = "\033[92m"  # Green
            else:
                category_failed += 1
                status_symbol = "✗"
                color_code = "\033[91m"  # Red

            reset_code = "\033[0m"

            # Print compact output
            output = f"{color_code}{status_symbol}{reset_code} [{test_id}] {description}"

            if self.verbose or not success:
                output += f"\n  Query: {query[:50]}..." if len(query) > 50 else f"\n  Query: {query}"
                output += f"\n  Result: {result}"

            print(output)

            self.results[category].append({
                'id': test_id,
                'description': description,
                'success': success,
                'result': result
            })

        print(f"\nCategory Summary: {category_passed} passed, {category_failed} failed\n")

    def run_all_tests(self, specific_category: str = None) -> None:
        """Run all tests or specific category"""
        test_data = self.load_test_queries()
        categories = test_data.get('categories', {})

        if specific_category:
            if specific_category not in categories:
                print(f"Error: Category '{specific_category}' not found")
                print(f"Available categories: {', '.join(categories.keys())}")
                sys.exit(1)
            categories_to_run = {specific_category: categories[specific_category]}
        else:
            categories_to_run = categories

        print(f"\n{'='*70}")
        print(f"Test Execution Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Server: {self.server_url}")
        print(f"{'='*70}\n")

        for category, category_data in categories_to_run.items():
            tests = category_data.get('tests', [])
            self.run_category(category, tests)

        self.print_summary()

    def print_summary(self) -> None:
        """Print test summary"""
        print(f"\n{'='*70}")
        print("FINAL TEST SUMMARY")
        print(f"{'='*70}\n")

        print(f"Total Tests Run:  {self.total}")
        print(f"Passed:           \033[92m{self.passed}\033[0m")
        print(f"Failed:           \033[91m{self.failed}\033[0m")
        print(f"Success Rate:     {(self.passed/self.total*100):.1f}%\n")

        # Category breakdown
        print("Breakdown by Category:")
        for category, results in self.results.items():
            category_passed = sum(1 for r in results if r['success'])
            category_total = len(results)
            print(f"  {category}: {category_passed}/{category_total} passed")

        print(f"\n{'='*70}\n")

        if self.failed == 0:
            print("\033[92m✓ All tests passed!\033[0m")
        else:
            print(f"\033[91m✗ {self.failed} test(s) failed\033[0m")

    def save_results(self, filename: str = "test_results.json") -> None:
        """Save detailed results to JSON file"""
        output = {
            "timestamp": datetime.now().isoformat(),
            "server": self.server_url,
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "success_rate": (self.passed / self.total * 100) if self.total > 0 else 0,
            "results": dict(self.results)
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)

        print(f"\nDetailed results saved to: {filename}")

def main():
    parser = argparse.ArgumentParser(
        description="Test runner for US-05 Input Validation queries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_queries.py
  python test_queries.py --server http://localhost:8000
  python test_queries.py --category VALID_QUERIES
  python test_queries.py --category INVALID_BLANK --verbose
  python test_queries.py --verbose --save results.json
        """
    )

    parser.add_argument(
        '--server',
        default='http://localhost:8000',
        help='Server URL (default: http://localhost:8000)'
    )
    parser.add_argument(
        '--category',
        help='Run specific category (leave blank to run all)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--save',
        metavar='FILENAME',
        help='Save results to JSON file'
    )

    args = parser.parse_args()

    runner = TestRunner(args.server, args.verbose)

    try:
        runner.run_all_tests(args.category)
        if args.save:
            runner.save_results(args.save)
    except KeyboardInterrupt:
        print("\n\nTest execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
