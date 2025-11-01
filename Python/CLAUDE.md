# Python Implementation - CLAUDE.md

This file provides guidance for working with the Python implementation of Chatfield.

## Overview

Chatfield Python (v0.2.0) transforms data gathering from rigid forms into conversational dialogues powered by LLMs. It uses a fluent builder API to define fields and validation rules, then leverages LangGraph to orchestrate natural conversations that collect structured data.

**IMPORTANT**: This is the Python implementation of an **isomorphic library**. The Python and TypeScript implementations are equal first-class citizens, maintaining near-identical code structure, naming, logic, and test suites.

**See**: [../Documentation/Isomorphic_Development.md](../Documentation/Isomorphic_Development.md) for isomorphic development principles.

## Quick Start

```bash
cd Python
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest  # Run tests
```

**See**: [../Documentation/Getting_Started_Python.md](../Documentation/Getting_Started_Python.md) for detailed setup.

## Development Commands

```bash
# Testing
python -m pytest                      # Run all tests
make test-cov                         # Run with coverage

# Code Quality
make format                           # Format with black & isort
make lint                             # Run flake8 linting
make typecheck                        # Run mypy type checking

# Examples
cd examples && python job_interview.py
```

**See**: [../Documentation/Commands.md](../Documentation/Commands.md) for complete command reference.

## Project Structure

```
Python/
├── chatfield/               # Core Python package
│   ├── interview.py         # Base Interview class
│   ├── interviewer.py       # LangGraph orchestration
│   ├── field_proxy.py       # FieldProxy string subclass
│   ├── builder.py           # Fluent builder API
│   ├── serialization.py     # State serialization
│   ├── presets.py           # Common presets
│   └── visualization.py     # Graph visualization
├── tests/                   # pytest test suite
└── examples/                # Usage examples
```

**See**: [../Documentation/Project_Structure.md](../Documentation/Project_Structure.md) for complete structure.

## Core Architecture

### Key Components

1. **Interview** (`interview.py`): Base class with field discovery and _chatfield dictionary structure
2. **Interviewer** (`interviewer.py`): LangGraph-based conversation orchestration
3. **FieldProxy** (`field_proxy.py`): String subclass providing transformation access via attributes
4. **Builder** (`builder.py`): Fluent builder API for defining interviews

### Data Flow

1. **Definition Phase**: Builder pattern creates Interview with field definitions
2. **Conversation Phase**: LangGraph orchestrates state machine (initialize → think → listen → tools → teardown)
3. **Collection Phase**: LLM validates responses and computes transformations
4. **Access Phase**: FieldProxy provides string values with transformation attributes

**See**: [../Documentation/Architecture.md](../Documentation/Architecture.md) for detailed architecture.

## Builder API

```python
from chatfield import chatfield

interview = (chatfield()
    .field("age")
        .desc("Your age")
        .must("be specific")
        .as_int()
        .as_lang("fr")
    .build())

# After collection
interview.age              # "25" (base string value)
interview.age.as_int       # 25 (integer)
interview.age.as_lang_fr   # "vingt-cinq" (French translation)
interview.age.as_quote     # "I am 25 years old" (original quote)
```

**See**: [../Documentation/Builder_Api.md](../Documentation/Builder_Api.md) for complete API reference.

## API Configuration

```python
from chatfield import Interviewer, chatfield

interview = chatfield().field("name").build()

# Option 1: Use environment variable (default)
interviewer = Interviewer(interview)

# Option 2: Explicit API key
interviewer = Interviewer(interview, api_key='your-api-key')

# Option 3: Custom base URL (e.g., LiteLLM proxy)
interviewer = Interviewer(
    interview,
    api_key='your-api-key',
    base_url='https://my-litellm-proxy.com/v1'
)
```

**See**: [../Documentation/Api_Configuration.md](../Documentation/Api_Configuration.md) for detailed configuration options and security modes.

## Testing

Tests use pytest with pytest-describe for BDD-style organization matching TypeScript:

```bash
python -m pytest                                    # Run all tests
python -m pytest tests/test_interview.py            # Run specific file
python -m pytest -k "test_name"                     # Run specific test
python -m pytest -m "not requires_api_key"          # Skip API tests
make test-cov                                       # Run with coverage
```

**Critical**: Python tests maintain **isomorphic structure** with TypeScript—identical test counts, descriptions, and organization.

**See**:
- [tests/CLAUDE.md](tests/CLAUDE.md) for Python test suite details
- [../Documentation/TESTING_Architecture.md](../Documentation/TESTING_Architecture.md) for testing philosophy

## Isomorphic Development in Python

### Key Principles

1. **Check TypeScript First**: Before implementing features, check `../TypeScript/` for the corresponding implementation
2. **Match Structure**: File names, class names, method names should match TypeScript (accounting for language conventions)
3. **Use "Isomorphic:" Comments**: When Python code must differ from TypeScript, include identical "Isomorphic:" comments in both files
4. **Identical Tests**: Test descriptions, counts, and structure must match TypeScript's Jest tests
5. **Zero Skipped Tests**: Use no-op tests that pass instead of `@pytest.mark.skip`

### Python-Specific Conventions

- **Naming**: Use `snake_case` for methods (vs TypeScript's `camelCase`)
- **Async**: Python implementation is primarily synchronous (TypeScript is async by default)
- **Types**: Use type hints where beneficial, but not required
- **Imports**: Use relative imports within the package
- **Testing**: Use pytest-describe to mirror TypeScript's Jest describe/it structure

### Example: Isomorphic Comment Pattern

```python
# Isomorphic: Python uses snake_case for method names, TypeScript uses camelCase.
# Both implementations have identical logic and behavior.
def get_field_value(self, field_name: str) -> Optional[str]:
    return self._chatfield['fields'].get(field_name, {}).get('value')
```

**See**: [../Documentation/Isomorphic_Development.md](../Documentation/Isomorphic_Development.md) for complete details.

## Interview Structure (_chatfield dictionary)

```python
{
    'type': 'InterviewType',
    'desc': 'Interview description',
    'roles': {
        'alice': {'type': 'Interviewer', 'traits': []},
        'bob': {'type': 'Interviewee', 'traits': []}
    },
    'fields': {
        'field_name': {
            'desc': 'Field description',
            'specs': {'must': [], 'reject': [], 'hint': []},
            'casts': {'as_int': {}, 'as_lang_fr': {}},
            'value': {
                'value': 'string value',
                'context': 'conversation context',
                'as_quote': 'direct quote',
                'as_int': 25,
                'as_lang_fr': 'vingt-cinq'
            }
        }
    }
}
```

**See**: [../Documentation/Architecture.md](../Documentation/Architecture.md) for detailed data structures.

## Field Access Patterns

Python supports two methods for accessing field values: dot notation for regular fields and bracket notation for fields with special characters.

### Regular Fields (Alphanumeric + Underscores)

```python
interview.field_name              # Dot notation
interview.field_name.as_int       # With transformations
```

### Special Character Fields

Fields with brackets, dots, spaces, or reserved words require **bracket notation**:

```python
interview["field[0]"]                               # Brackets in field name
interview["topmostSubform[0].Page1[0].f1_01[0]"]   # PDF form fields
interview["user.name"]                              # Dots in field name
interview["full name"]                              # Spaces in field name
interview["class"]                                  # Python reserved words
```

### Implementation Details

- **`__getattr__`**: Intercepts dot notation access (e.g., `interview.name`)
- **`__getitem__`**: Intercepts bracket notation access (e.g., `interview["name"]`)
- Both methods return `FieldProxy` instances or `None`
- PDF forms commonly use hierarchical names with special characters

**Example with PDF form**:

```python
from chatfield import chatfield

# Define interview with PDF-style field names
interview = (chatfield()
    .field("topmostSubform[0].Page1[0].f1_01[0]")
        .desc("Full legal name")
    .field("topmostSubform[0].Page1[0].f1_02[0]")
        .desc("Social Security Number")
    .build())

# Access via bracket notation
name = interview["topmostSubform[0].Page1[0].f1_01[0]"]
ssn = interview["topmostSubform[0].Page1[0].f1_02[0]"]
```

**See**: [../Documentation/Builder_Api.md](../Documentation/Builder_Api.md) for complete field naming documentation.

## Dependencies

### Core Libraries
- `langchain` (0.3.27+): LLM abstractions and tools
- `langgraph` (1.0.0a3+): Conversation state machine
- `langchain-openai` (0.3.29+): OpenAI integration
- `pydantic` (2.11.7+): Data validation and serialization
- `deepdiff` (6.0.0+): State comparison utilities

## Environment

- **Python Version**: 3.8+ required
- **Command**: Use `python` (not `python3`) with activated venv
- **Virtual Environment**: `.venv/` in Python directory
- **Package Mode**: Editable install with `pip install -e .`

## Key Considerations

1. **Isomorphic Implementation**: This Python code mirrors TypeScript—check both implementations when making changes
2. **Test Isomorphism**: Test names, counts, and descriptions must match TypeScript implementation exactly
3. **Naming Conventions**: Use snake_case (Python) vs camelCase (TypeScript), documented with "Isomorphic:" comments
4. **Transformation Computation**: All transformations computed during collection by LLM
5. **Thread Safety**: Each Interviewer maintains separate thread ID
6. **Field Discovery**: Fields defined via builder pattern, not method inspection

## Additional Resources

- **Main Documentation**: [../CLAUDE.md](../CLAUDE.md) for project overview
- **Architecture**: [../Documentation/Architecture.md](../Documentation/Architecture.md)
- **Cookbook**: [../Documentation/Cookbook.md](../Documentation/Cookbook.md) for common patterns
- **Design Decisions**: [../Documentation/Design_Decisions.md](../Documentation/Design_Decisions.md)
