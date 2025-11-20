#!/bin/bash

# Run All Tests Script
# Executes all test suites and generates reports

set -e

echo "=========================================="
echo "  VPBank Voice Agent v2.0"
echo "  Test Suite Runner"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q pytest pytest-cov pytest-asyncio

echo ""
echo "=========================================="
echo "  Running Test Suites"
echo "=========================================="
echo ""

# Run unit tests
echo "🧪 Running Unit Tests..."
pytest tests/test_utils.py -v --tb=short --cov=src/utils --cov-report=term-missing
UNIT_EXIT=$?

echo ""
echo "=========================================="
echo ""

# Run integration tests
echo "🔗 Running Integration Tests..."
pytest tests/test_integration.py -v --tb=short
INTEGRATION_EXIT=$?

echo ""
echo "=========================================="
echo ""

# Run feature tests
echo "✨ Running Feature Tests..."
pytest tests/test_new_features.py -v --tb=short
FEATURE_EXIT=$?

echo ""
echo "=========================================="
echo ""

# Run all tests with coverage
echo "📊 Running All Tests with Coverage..."
pytest tests/test_utils.py tests/test_integration.py tests/test_new_features.py \
    -v --tb=short \
    --cov=src/utils \
    --cov=src/browser_agent \
    --cov=src/dynamodb_service \
    --cov-report=html \
    --cov-report=term
ALL_EXIT=$?

echo ""
echo "=========================================="
echo "  Test Results Summary"
echo "=========================================="
echo ""

# Check results
if [ $UNIT_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅ Unit Tests: PASSED${NC}"
else
    echo -e "${RED}❌ Unit Tests: FAILED${NC}"
fi

if [ $INTEGRATION_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅ Integration Tests: PASSED${NC}"
else
    echo -e "${RED}❌ Integration Tests: FAILED${NC}"
fi

if [ $FEATURE_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅ Feature Tests: PASSED${NC}"
else
    echo -e "${RED}❌ Feature Tests: FAILED${NC}"
fi

echo ""

if [ $ALL_EXIT -eq 0 ]; then
    echo -e "${GREEN}=========================================="
    echo -e "  ✅ ALL TESTS PASSED"
    echo -e "==========================================${NC}"
    echo ""
    echo "📊 Coverage report generated: htmlcov/index.html"
    echo "🎉 System is ready for deployment!"
    exit 0
else
    echo -e "${RED}=========================================="
    echo -e "  ❌ SOME TESTS FAILED"
    echo -e "==========================================${NC}"
    echo ""
    echo "Please fix failing tests before deployment."
    exit 1
fi
