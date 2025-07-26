#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Running security scans on qwark..."

# Run Bandit security scanner
echo "Checking for security vulnerabilities with Bandit..."
bandit -r qwark/ -f json -o bandit-report.json || true

# Parse and display results
if [ -f bandit-report.json ]; then
    # Check if there are any issues
    ISSUES=$(python -c "import json; data = json.load(open('bandit-report.json')); print(len(data.get('results', [])))")
    
    if [ "$ISSUES" -gt 0 ]; then
        echo -e "${YELLOW}Security issues found:${NC}"
        
        # Display formatted results
        python -c "
import json

with open('bandit-report.json', 'r') as f:
    data = json.load(f)
    
for issue in data.get('results', []):
    print(f\"\\n{issue['filename']}:{issue['line_number']}: {issue['issue_severity']} - {issue['issue_text']}\")
    print(f\"  Test: {issue['test_id']} - {issue['test_name']}\")
    if issue.get('more_info'):
        print(f\"  More info: {issue['more_info']}\")
"
        
        # Exit with error if high severity issues found
        HIGH_SEVERITY=$(python -c "import json; data = json.load(open('bandit-report.json')); print(sum(1 for r in data.get('results', []) if r['issue_severity'] == 'HIGH'))")
        
        # Clean up report file
        rm -f bandit-report.json
        
        if [ "$HIGH_SEVERITY" -gt 0 ]; then
            echo -e "\n${RED}Found $HIGH_SEVERITY high severity issues!${NC}"
            exit 1
        else
            echo -e "\n${YELLOW}Found $ISSUES low/medium severity issues. Please review.${NC}"
        fi
    else
        echo -e "${GREEN}No security issues found!${NC}"
        rm -f bandit-report.json
    fi
else
    # Run bandit with console output as fallback
    bandit -r qwark/ -ll
fi

echo "Security checks completed!"