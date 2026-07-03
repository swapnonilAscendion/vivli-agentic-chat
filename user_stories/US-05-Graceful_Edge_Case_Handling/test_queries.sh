#!/bin/bash

# Test Queries Script for US-05: Graceful Edge Case Handling
# Usage: ./test_queries.sh [category] [server_url]
# Example: ./test_queries.sh VALID_QUERIES http://localhost:8000
#          ./test_queries.sh all http://localhost:8000

set -e

# Configuration
SERVER_URL="${2:-http://localhost:8000}"
CATEGORY="${1:-all}"
ENDPOINT="/chat"
RESULTS_FILE="test_results.log"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Initialize results file
echo "Test Results - $TIMESTAMP" > "$RESULTS_FILE"
echo "Server: $SERVER_URL" >> "$RESULTS_FILE"
echo "Category: $CATEGORY" >> "$RESULTS_FILE"
echo "========================================" >> "$RESULTS_FILE"

# Test counters
TOTAL=0
PASSED=0
FAILED=0

# Function to test a single query
test_query() {
    local id=$1
    local query=$2
    local expected_status=$3
    local description=$4

    TOTAL=$((TOTAL + 1))

    # Escape query for JSON
    query_escaped=$(echo "$query" | sed 's/"/\\"/g')

    # Make the request
    response=$(curl -s -X POST "$SERVER_URL$ENDPOINT" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query_escaped\"}")

    # Extract validation status
    validation_status=$(echo "$response" | grep -o '"validation_status":"[^"]*"' | cut -d'"' -f4)

    # Check if result matches expectation
    if [[ "$validation_status" == "$expected_status" ]]; then
        echo -e "${GREEN}✓ PASS${NC} [$id] $description"
        echo "✓ PASS [$id] $description" >> "$RESULTS_FILE"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗ FAIL${NC} [$id] $description (expected: $expected_status, got: $validation_status)"
        echo "✗ FAIL [$id] $description (expected: $expected_status, got: $validation_status)" >> "$RESULTS_FILE"
        FAILED=$((FAILED + 1))
    fi
}

# Function to run all tests in a category
run_category() {
    local category=$1

    echo ""
    echo -e "${BLUE}========== Testing $category ==========${NC}"
    echo ""

    case $category in
        "VALID_QUERIES")
            test_query "valid_001" "How do I submit a data request?" "passed" "Standard FAQ question"
            test_query "valid_002" "What is the form check process?" "passed" "Form check question"
            test_query "valid_003" "When will my request be approved?" "passed" "Timeline question"
            test_query "valid_004" "Can I download the data after approval?" "passed" "Download permission question"
            test_query "valid_005" "What are the eligibility requirements?" "passed" "Eligibility question"
            test_query "valid_016" "hi" "passed" "Single-word greeting"
            test_query "valid_017" "hello" "passed" "Single-word greeting"
            test_query "valid_018" "help" "passed" "Single-word request"
            ;;
        "INVALID_BLANK")
            test_query "blank_001" "" "failed" "Empty message"
            test_query "blank_002" "   " "failed" "Spaces only"
            test_query "blank_003" "	" "failed" "Tabs only"
            ;;
        "INVALID_HTML")
            test_query "html_001" "<script>alert('xss')</script>" "failed" "Script tag injection"
            test_query "html_002" "Check this <button onclick='alert()'>button</button>" "failed" "Button onclick injection"
            test_query "html_003" "<!DOCTYPE html><html><body>test</body></html>" "failed" "Full HTML document"
            ;;
        "INVALID_CODE")
            test_query "code_001" "def my_function(): pass" "failed" "Python function"
            test_query "code_002" "function test() { return true; }" "failed" "JavaScript function"
            test_query "code_003" "public class Main { }" "failed" "Java class"
            ;;
        "INVALID_SPAM")
            test_query "spam_001" "Click here http://malicious-site.com and check this https://another-bad-site.com for amazing deals" "failed" "Multiple URLs"
            test_query "spam_002" "Buy now! Click here for free offer and get discount today!" "failed" "Commercial spam"
            test_query "spam_003" "Check out http://example.com and http://test.com and http://demo.com" "failed" "Multiple URLs"
            ;;
        "EDGE_CASES")
            test_query "edge_001" "What is the cost? (USD)" "passed" "Special characters"
            test_query "edge_002" "Can I request REQ-123456 or REQ-789?" "passed" "Request IDs"
            test_query "edge_003" "What's the difference between form check and review?" "passed" "Apostrophe contraction"
            test_query "edge_004" "Is it 100% safe? What about 50% cases?" "passed" "Percentage signs"
            ;;
        *)
            echo "Unknown category: $category"
            exit 1
            ;;
    esac
}

# Main execution
if [[ "$CATEGORY" == "all" ]]; then
    echo -e "${BLUE}Starting comprehensive test suite...${NC}"
    echo "Server: $SERVER_URL"
    echo ""

    run_category "VALID_QUERIES"
    run_category "INVALID_BLANK"
    run_category "INVALID_HTML"
    run_category "INVALID_CODE"
    run_category "INVALID_SPAM"
    run_category "EDGE_CASES"
else
    run_category "$CATEGORY"
fi

# Print summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo "Total Tests: $TOTAL"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [[ $FAILED -eq 0 ]]; then
    echo -e "${GREEN}All tests passed!${NC}"
else
    echo -e "${RED}Some tests failed. Check $RESULTS_FILE for details.${NC}"
fi

echo ""
echo "Results saved to: $RESULTS_FILE"
