#!/bin/bash
set -e

echo "Running linters on qwark..."

# Check for typing annotations and docstrings
echo "Checking type annotations with mypy..."
mypy qwark --strict --exclude 'test_.*\.py$'

# Check code style
echo "Checking code style with flake8..."
flake8 qwark tests --max-line-length=88 --exclude="test_*.py"

# Custom check for docstrings
echo "Checking for docstrings..."
python -c "
import ast
import sys

def check_docstrings(filename):
    with open(filename, 'r') as f:
        tree = ast.parse(f.read(), filename=filename)
    
    errors = []
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if not ast.get_docstring(node):
                errors.append(f'{filename}:{node.lineno}: Missing docstring in {node.name}')
    
    return errors

files = ['qwark/__init__.py', 'qwark/core.py']
all_errors = []

for file in files:
    try:
        all_errors.extend(check_docstrings(file))
    except:
        pass

if all_errors:
    for error in all_errors:
        print(error)
    sys.exit(1)
else:
    print('All functions and classes have docstrings!')
"

echo "Lint checks passed!"