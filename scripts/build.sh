#!/bin/bash
set -e

echo "Building qwark..."

# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build the package
python -m build

echo "Build complete! Packages created in dist/"