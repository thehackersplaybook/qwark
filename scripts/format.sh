#!/bin/bash
set -e

echo "Formatting code with black..."

# Format Python code
black qwark tests

echo "Code formatting complete!"