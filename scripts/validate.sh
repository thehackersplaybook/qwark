#!/bin/bash
set -e

echo "Validating qwark..."

# Format check (without modifying)
echo "Checking code formatting..."
black --check qwark tests

# Run linting
echo "Running lint checks..."
"${BASH_SOURCE%/*}/lint.sh"

# Run tests
echo "Running tests..."
"${BASH_SOURCE%/*}/test.sh"

# Check package structure
echo "Checking package structure..."
python -c "
import qwark
from qwark import optimize_query
print('✓ Package imports correctly')
print(f'✓ Version: {qwark.__version__}')
"

echo "All validation checks passed!"