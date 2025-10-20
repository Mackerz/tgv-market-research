#!/bin/bash

# Test runner script for backend unit tests
# Usage: ./run_tests.sh [options]

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Backend Test Suite Runner${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}Error: Poetry is not installed${NC}"
    echo "Install it with: curl -sSL https://install.python-poetry.org | python3 -"
    echo "Or visit: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Check if dependencies are installed
if [ ! -d ".venv" ] && [ ! -f "poetry.lock" ]; then
    echo -e "${YELLOW}Dependencies not installed. Running 'poetry install'...${NC}"
    poetry install
fi

# Default options
COVERAGE=false
VERBOSE=false
MARKERS=""
SPECIFIC_TEST=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage|-c)
            COVERAGE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --unit|-u)
            MARKERS="unit"
            shift
            ;;
        --integration|-i)
            MARKERS="integration"
            shift
            ;;
        --test|-t)
            SPECIFIC_TEST="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: ./run_tests.sh [options]"
            echo ""
            echo "Options:"
            echo "  -c, --coverage       Run tests with coverage report"
            echo "  -v, --verbose        Run tests in verbose mode"
            echo "  -u, --unit           Run only unit tests"
            echo "  -i, --integration    Run only integration tests"
            echo "  -t, --test FILE      Run specific test file"
            echo "  -h, --help           Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./run_tests.sh                    # Run all tests"
            echo "  ./run_tests.sh --coverage         # Run with coverage"
            echo "  ./run_tests.sh --unit             # Run only unit tests"
            echo "  ./run_tests.sh --test test_json_utils.py  # Run specific file"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Build pytest command with Poetry
PYTEST_CMD="poetry run pytest"

if [ "$SPECIFIC_TEST" != "" ]; then
    echo -e "${YELLOW}Running specific test: $SPECIFIC_TEST${NC}"
    PYTEST_CMD="$PYTEST_CMD tests/$SPECIFIC_TEST"
else
    PYTEST_CMD="$PYTEST_CMD tests/"
fi

if [ "$MARKERS" != "" ]; then
    echo -e "${YELLOW}Running $MARKERS tests only${NC}"
    PYTEST_CMD="$PYTEST_CMD -m $MARKERS"
fi

if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -vv"
fi

if [ "$COVERAGE" = true ]; then
    echo -e "${YELLOW}Running with coverage report${NC}"
    PYTEST_CMD="$PYTEST_CMD --cov=. --cov-report=html --cov-report=term-missing"
fi

echo -e "${GREEN}Executing: $PYTEST_CMD${NC}"
echo ""

# Run tests with Poetry
$PYTEST_CMD

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo -e "${GREEN}================================${NC}"

    if [ "$COVERAGE" = true ]; then
        echo ""
        echo -e "${YELLOW}Coverage report generated in htmlcov/index.html${NC}"
    fi
else
    echo ""
    echo -e "${RED}================================${NC}"
    echo -e "${RED}✗ Some tests failed${NC}"
    echo -e "${RED}================================${NC}"
    exit 1
fi
