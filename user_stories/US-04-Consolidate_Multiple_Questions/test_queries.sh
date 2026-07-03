#!/bin/bash

################################################################################
# Integration Test Runner for US-04: Consolidate Multiple Questions
#
# Usage:
#   ./test_queries.sh                      # Run all tests
#   ./test_queries.sh --verbose            # Verbose output
#   ./test_queries.sh --test CONSOLIDATE_001  # Run specific test
#
# Requirements:
#   - Python 3.8+
#   - test_queries.py in same directory
#
################################################################################

# Set script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to script directory
cd "$SCRIPT_DIR" || exit 1

# Print header
echo "================================================================================"
echo "US-04 Integration Test Suite"
echo "Consolidate Multiple Questions"
echo "================================================================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check if test_queries.py exists
if [ ! -f "test_queries.py" ]; then
    echo "Error: test_queries.py not found in $SCRIPT_DIR"
    exit 1
fi

# Run the test suite
echo "Running tests..."
echo ""

python3 test_queries.py "$@"
exit_code=$?

echo ""
echo "================================================================================"

if [ $exit_code -eq 0 ]; then
    echo "✓ All tests passed!"
else
    echo "✗ Some tests failed"
fi

echo "================================================================================"

exit $exit_code
