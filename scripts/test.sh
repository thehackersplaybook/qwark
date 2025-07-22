#!/bin/bash
set -e

echo "Running tests for qwark..."

# Run pytest with coverage
pytest -v --cov=qwark --cov-report=term-missing

echo "Tests completed!"