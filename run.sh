#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="${SCRIPT_DIR}/scripts"

# Function to display help
show_help() {
    echo -e "${BLUE}Qwark Development Tools${NC}"
    echo -e "${BLUE}===========================${NC}"
    echo ""
    echo "Usage: ./run.sh [option]"
    echo ""
    echo -e "${GREEN}Available options:${NC}"
    echo -e "  ${YELLOW}--help${NC}        Show this help message"
    echo -e "  ${YELLOW}--build${NC}       Build the package"
    echo -e "  ${YELLOW}--lint${NC}        Run linting checks (mypy, flake8, docstrings)"
    echo -e "  ${YELLOW}--format${NC}      Format code with black"
    echo -e "  ${YELLOW}--test${NC}        Run tests with pytest"
    echo -e "  ${YELLOW}--validate${NC}    Run all validation checks (format, lint, test)"
    echo ""
    echo -e "${GREEN}Examples:${NC}"
    echo "  ./run.sh --help"
    echo "  ./run.sh --build"
    echo "  ./run.sh --test"
    echo ""
}

# Function to run a script
run_script() {
    local script_name=$1
    local script_path="${SCRIPTS_DIR}/${script_name}.sh"
    
    if [ -f "$script_path" ]; then
        echo -e "${BLUE}Running ${script_name}...${NC}"
        echo ""
        "$script_path"
        local exit_code=$?
        if [ $exit_code -eq 0 ]; then
            echo ""
            echo -e "${GREEN}✓ ${script_name} completed successfully!${NC}"
        else
            echo ""
            echo -e "${RED}✗ ${script_name} failed with exit code $exit_code${NC}"
            exit $exit_code
        fi
    else
        echo -e "${RED}Error: Script ${script_path} not found!${NC}"
        exit 1
    fi
}

# Main script logic
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

case "$1" in
    --help)
        show_help
        ;;
    --build)
        run_script "build"
        ;;
    --lint)
        run_script "lint"
        ;;
    --format)
        run_script "format"
        ;;
    --test)
        run_script "test"
        ;;
    --validate)
        run_script "validate"
        ;;
    *)
        echo -e "${RED}Error: Unknown option '$1'${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac