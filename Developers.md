# Chatfield Developer Guide

Welcome to the Chatfield project! This guide will help you get started with development, testing, and contributing to both the Python and TypeScript/JavaScript implementations.

## Table of Contents

- [Project Overview](#project-overview)
- [Prerequisites](#prerequisites)
- [Setting Up Development Environment](#setting-up-development-environment)
  - [Python Setup](#python-setup)
  - [TypeScript/JavaScript Setup](#typescriptjavascript-setup)
- [API Keys and Environment Variables](#api-keys-and-environment-variables)
- [Running Test Suites](#running-test-suites)
  - [Python Tests](#python-tests)
  - [TypeScript Tests](#typescript-tests)
- [Development Workflow](#development-workflow)
- [Code Quality Tools](#code-quality-tools)
- [Project Structure](#project-structure)
- [Debugging Tips](#debugging-tips)
- [Contributing Guidelines](#contributing-guidelines)

## Project Overview

Chatfield is a dual-implementation library that transforms data collection from rigid forms into natural conversations powered by LLMs. It provides both Python (v1.0.0a2) and TypeScript/JavaScript (v1.0.0a2) implementations with feature parity as the goal.

**Core Features:**
- LLM-powered conversational data collection
- Smart validation and transformation of responses
- LangGraph-based conversation orchestration
- Fluent builder pattern API
- Full TypeScript type safety
- React and CopilotKit integrations

## Prerequisites

### General Requirements
- Git
- Node.js 20.0.0+ (for TypeScript implementation)
- Python 3.8+ (for Python implementation)
- OpenAI API key (or other supported LLM provider)

### Recommended Tools
- VSCode with Python and TypeScript extensions
- Docker (optional, for containerized development)
- Make (for Python development shortcuts)

## Setting Up Development Environment

### Python Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/chatfield.git
cd chatfield/Python
```

2. **Create and activate a virtual environment:**
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

3. **Install the package with development dependencies:**
```bash
# Install in editable mode with all dev dependencies
pip install -e ".[dev]"

# Or use the Makefile shortcut:
make install-dev
```

4. **Set up pre-commit hooks (optional but recommended):**
```bash
pre-commit install
```

### TypeScript/JavaScript Setup

1. **Navigate to the TypeScript directory:**
```bash
cd chatfield/TypeScript
```

2. **Install dependencies:**
```bash
npm install
```

3. **Build the project:**
```bash
npm run build
```

4. **Set up watch mode for development:**
```bash
npm run dev  # Watches for changes and rebuilds automatically
```

## API Keys and Environment Variables

### Setting up API Keys

Chatfield requires an OpenAI API key (or other LLM provider keys). You have three options for configuration:

#### Option 1: Environment Variable
```bash
export OPENAI_API_KEY="your-api-key-here"
```

#### Option 2: .env File (Recommended for Development)
Create a `.env` file in the project root:
```bash
# /home/dev/src/Chatfield/.env
OPENAI_API_KEY=your-api-key-here

# Optional: LangSmith tracing configuration
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_PROJECT=chatfield
LANGSMITH_API_KEY=your-langsmith-api-key  # If you have a LangSmith account
```

#### Option 3: Pass to Interviewer Constructor
```python
# Python
from chatfield import Interviewer
interviewer = Interviewer(interview, api_key="your-api-key")
```

```typescript
// TypeScript
import { Interviewer } from '@chatfield/core'
const interviewer = new Interviewer(interview, { apiKey: "your-api-key" })
```

### Security Best Practices

⚠️ **IMPORTANT**: Never commit API keys to version control!

1. **Add `.env` to `.gitignore`** (should already be configured)
2. **Use `.env.example`** for documenting required variables:
```bash
# Create .env.example with dummy values
OPENAI_API_KEY=your-api-key-here
LANGSMITH_API_KEY=your-langsmith-key-here
```

3. **For production**, use secure secret management:
   - Environment variables from CI/CD
   - Secret management services (AWS Secrets Manager, Azure Key Vault, etc.)
   - Kubernetes secrets

## Running Test Suites

### Python Tests

The Python test suite uses pytest with pytest-describe for BDD-style test organization.

#### Running All Tests
```bash
# Using pytest directly
python -m pytest

# Using Makefile
make test

# With coverage report
make test-cov
# HTML coverage report will be in htmlcov/index.html
```

#### Running Specific Tests
```bash
# Run specific test file
python -m pytest tests/test_interview.py

# Run specific test by name pattern
python -m pytest -k "test_field_validation"

# Run tests in a describe block
python -m pytest tests/test_builder.py::describe_builder
```

#### Test Categories
```bash
# Skip tests that require API keys
python -m pytest -m "not requires_api_key"

# Skip slow tests
python -m pytest -m "not slow"

# Run only unit tests
python -m pytest -m "unit"

# Run only integration tests
python -m pytest -m "integration"
```

#### Viewing Test Coverage
```bash
# Generate HTML coverage report
python -m pytest --cov=chatfield --cov-report=html

# Open coverage report
# Linux/Mac:
open htmlcov/index.html
# Windows:
start htmlcov/index.html
```

### TypeScript Tests

The TypeScript test suite uses Jest with a structure that mirrors the Python tests.

#### Running All Tests
```bash
# Run all tests
npm test

# Run tests in watch mode (re-runs on file changes)
npm run test:watch

# Run with coverage
npm test -- --coverage
# Coverage report will be in coverage/lcov-report/index.html
```

#### Running Specific Tests
```bash
# Run specific test file
npm test interview.test.ts

# Run tests matching a pattern
npm test -- --testNamePattern="field validation"

# Run integration tests only
npm test -- integration/
```

#### Debugging Tests
```bash
# Run tests with verbose output
npm test -- --verbose

# Debug with Node inspector
node --inspect-brk node_modules/.bin/jest --runInBand

# Run single test file in band (sequential)
npm test -- --runInBand interview.test.ts
```

## Development Workflow

### Python Development Commands

```bash
# Format code with Black and isort
make format

# Run linting checks
make lint

# Run type checking with mypy
make typecheck

# Run all checks (format, lint, typecheck, test)
make dev

# Build distribution packages
make build

# Clean build artifacts
make clean
```

### TypeScript Development Commands

```bash
# Build TypeScript to JavaScript
npm run build

# Watch mode (rebuilds on changes)
npm run dev

# Run linting
npm run lint

# Clean build directory
npm run clean

# Run minimal OpenAI test
npm run min
```

### Running Examples

#### Python Examples
```bash
cd Python/examples
python job_interview.py
python restaurant_order.py
python tech_request.py
python favorite_number.py
```

#### TypeScript Examples
```bash
cd TypeScript
npx tsx examples/basic-usage.ts
npx tsx examples/job-interview.ts
npx tsx examples/restaurant-order.ts
npx tsx examples/schema-based.ts
```

## Code Quality Tools

### Python Tools

- **Black**: Code formatter (line length: 100)
- **isort**: Import sorter
- **flake8**: Linting tool
- **mypy**: Static type checker
- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting

Configuration files:
- `pyproject.toml`: Main Python project configuration
- `Makefile`: Development command shortcuts

### TypeScript Tools

- **ESLint**: Linting and code quality
- **TypeScript**: Strict mode with all checks enabled
- **Jest**: Testing framework
- **ts-jest**: TypeScript support for Jest

Configuration files:
- `package.json`: Node.js project configuration
- `tsconfig.json`: TypeScript compiler configuration
- `jest.config.js`: Jest testing configuration

## Project Structure

```
Chatfield/
├── Documentation/              # Project-wide documentation
│   └── TEST_HARMONIZATION.md  # Test synchronization guide
├── Python/                     # Python implementation (v1.0.0a2)
│   ├── chatfield/             # Core package
│   ├── tests/                 # Test suite (pytest-describe)
│   ├── examples/              # Usage examples
│   ├── evals/                 # Security evaluation suite
│   ├── Makefile              # Development shortcuts
│   └── pyproject.toml        # Package configuration
└── TypeScript/                # TypeScript implementation (v1.0.0a2)
    ├── src/                   # Source code
    ├── tests/                 # Test suite (Jest)
    ├── examples/              # Usage examples
    ├── package.json          # Package configuration
    └── tsconfig.json         # TypeScript configuration
```

## Debugging Tips

### Python Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Inspect Interview structure
print(interview._chatfield)

# Check LangGraph state
print(interviewer.graph.get_state())
```

### TypeScript Debugging

```typescript
// Enable LangSmith tracing
process.env.LANGCHAIN_TRACING_V2 = "true"

// Inspect Interview state
console.log(interview._chatfield)

// Debug in VSCode
// Add breakpoints and use Debug > Start Debugging
```

### Common Issues and Solutions

#### Python
- **ImportError**: Ensure package is installed: `pip install -e .`
- **Missing API Key**: Set `OPENAI_API_KEY` environment variable
- **Slow Tests**: Mark with `@pytest.mark.slow` and skip with `-m "not slow"`

#### TypeScript
- **Module not found**: Run `npm install` and `npm run build`
- **Type errors**: Check `tsconfig.json` and ensure strict mode settings
- **Test timeout**: Increase timeout with `jest.setTimeout(10000)`

## Contributing Guidelines

### Before You Start

1. **Check existing issues** on GitHub
2. **Read the CLAUDE.md files** for implementation details
3. **Ensure tests pass** before making changes

### Making Changes

1. **Maintain feature parity** between Python and TypeScript
2. **Follow existing patterns** and conventions
3. **Write tests** for new features using BDD style
4. **Update documentation** when adding features
5. **Use descriptive commit messages**

### Test Guidelines

- **Test names must match** between Python and TypeScript implementations
- Use BDD-style organization (describe/it blocks)
- Write both unit and integration tests
- Mock external dependencies for unit tests
- Mark API-dependent tests appropriately

### Code Style

#### Python
- Use Black formatter (100 char line limit)
- Follow PEP 8 with Black's modifications
- Use type hints where appropriate
- Write docstrings for public methods

#### TypeScript
- Follow ESLint configuration
- Use strict TypeScript settings
- Provide full type coverage
- Document with JSDoc comments

### Submitting Changes

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Make your changes** with appropriate tests
4. **Run all checks**:
   - Python: `make dev`
   - TypeScript: `npm run lint && npm test`
5. **Commit with clear messages**: `git commit -m "Add feature: description"`
6. **Push to your fork**: `git push origin feature/your-feature`
7. **Create a Pull Request** with:
   - Clear description of changes
   - Link to related issues
   - Test results/coverage

### Version Synchronization

When making changes that affect the API:
1. Update **both** Python and TypeScript implementations
2. Ensure test parity (see `Documentation/TEST_HARMONIZATION.md`)
3. Update version numbers in both `pyproject.toml` and `package.json`

## Additional Resources

### Documentation
- Main CLAUDE.md: Project overview and architecture
- Python/CLAUDE.md: Python-specific implementation details
- TypeScript/CLAUDE.md: TypeScript-specific implementation details
- Documentation/TEST_HARMONIZATION.md: Test synchronization guide

### External Resources
- [LangGraph Documentation](https://www.langchain.com/langgraph)
- [LangChain Documentation](https://www.langchain.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Jest Testing Documentation](https://jestjs.io/)
- [Pytest Documentation](https://docs.pytest.org/)

### Getting Help
- GitHub Issues: Report bugs or request features
- Discussions: Ask questions and share ideas
- YouTube Streams: Watch development in progress

## Quick Reference

### Essential Commands Cheat Sheet

```bash
# Python
cd Python
source .venv/bin/activate     # Activate virtual environment
pip install -e ".[dev]"        # Install with dev dependencies
make dev                       # Run all checks
python -m pytest               # Run tests
make test-cov                  # Run tests with coverage

# TypeScript
cd TypeScript
npm install                    # Install dependencies
npm run dev                    # Watch mode
npm test                       # Run tests
npm test -- --coverage         # Run with coverage
npm run build                  # Build project

# Both
export OPENAI_API_KEY="..."   # Set API key
```

Happy coding! 🚀