# Qwark

A Python module for SQL query optimization.

**⚠️ Project not released yet.**

## Installation

```bash
pip install -e .
```

## Usage

```python
from qwark import optimize_query

# Will raise NotImplementedError
config = {"your": "config"}
result = optimize_query(config)
```

## Development

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd qwark

# Install with development dependencies
pip install -e ".[dev]"
```

### Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=qwark

# Run linting
flake8 qwark tests
black --check qwark tests
mypy qwark
```

## Requirements

- Python 3.10+ (Latest LTS version supported)

## License

MIT