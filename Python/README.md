# Chatfield Python

Python implementation of conversational data collection.

## Development Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_interview.py

# Run specific test by name
python -m pytest -k "test_name"

# Skip slow tests
python -m pytest -m "not slow"

# Run only API tests
python -m pytest -m "requires_api_key"

# Run with coverage
python -m pytest --cov=chatfield --cov-report=html
# Coverage report will be in htmlcov/index.html
```

## Code Quality

```bash
# Format code with Black and isort
make format

# Run linting with flake8
make lint

# Run type checking with mypy
make typecheck

# Run all quality checks
make quality
```

## Build and Distribution

```bash
# Build distribution packages
make build

# Clean build artifacts
make clean

# Build and check package
python -m build
twine check dist/*
```

## Makefile Commands

The Makefile provides shortcuts for common tasks:

- `make test` - Run all tests
- `make test-fast` - Run tests excluding slow/API tests
- `make test-cov` - Run tests with coverage report
- `make format` - Format code with Black and isort
- `make lint` - Run flake8 linting
- `make typecheck` - Run mypy type checking
- `make quality` - Run all quality checks (format, lint, typecheck)
- `make build` - Build distribution packages
- `make clean` - Clean build artifacts

## Project Structure

```
Python/
├── chatfield/              # Core package
│   ├── __init__.py        # Main exports
│   ├── interview.py       # Interview base class
│   ├── interviewer.py     # Conversation orchestration
│   ├── field_proxy.py     # FieldProxy implementation
│   ├── builder.py         # Builder API
│   ├── serialization.py   # State serialization
│   ├── presets.py         # Common presets
│   └── visualization.py   # Graph visualization
├── tests/                  # Test suite
│   ├── test_*.py          # Test files
│   └── conftest.py        # Test configuration
├── examples/              # Example scripts
├── Makefile               # Development shortcuts
├── pyproject.toml         # Package configuration
└── setup.cfg              # Additional configuration
```

## Environment Variables

Set in `.env` file or export:

```bash
OPENAI_API_KEY=your-api-key
LANGCHAIN_TRACING_V2=true  # Optional: Enable LangSmith tracing
```

## Python Version

Requires Python 3.8 or higher.

## Dependencies

Core dependencies are managed in `pyproject.toml`. Key packages:
- langchain (0.3.27+)
- langgraph (1.0.0a3+)
- langchain-openai (0.3.29+)
- pydantic (2.11.7+)
- openai (1.99.6+)

Development dependencies include:
- pytest
- pytest-describe
- black
- isort
- flake8
- mypy