# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Chatfield is a dual-implementation library that transforms data collection from rigid forms into natural conversations powered by LLMs. It provides both Python (v0.2.0) and TypeScript/JavaScript (v0.1.0) implementations with feature parity as a goal.

**Core Concept**: Replace traditional form fields with conversational dialogues that intelligently gather, validate, and transform structured data through natural language interactions.

**Key Features**:
- LLM-powered conversational data collection
- Smart validation and transformation of responses
- LangGraph-based conversation orchestration
- Fluent builder pattern API
- Full TypeScript type safety
- React and CopilotKit integrations

## Isomorphic Development Philosophy

**CRITICAL: Chatfield is an isomorphic library—both Python and TypeScript implementations are treated as equal first-class implementations.** This is a fundamental design principle that permeates every aspect of the project.

### What "Isomorphic" Means in Chatfield

1. **Identical Concepts**: Both languages implement identical concepts, architecture, and patterns
2. **Near-Identical Code**: Code structure, naming, and logic are nearly identical across languages
3. **Documented Deviations**: Language-specific differences are explicitly documented with "Isomorphic:" comments
4. **Identical Test Suites**: Test files, test names, test descriptions, and test counts are identical
5. **Zero Skipped Tests**: Both implementations maintain identical test counts with zero skipped tests
6. **Shared Documentation**: Both implementations share consistent documentation patterns

### The "Isomorphic:" Comment Pattern

When code must differ between Python and TypeScript due to language-specific requirements, both implementations MUST include an identical "Isomorphic:" comment explaining the difference:

```python
# Python example
def some_method(self):
    # Isomorphic: Python uses snake_case for method names, TypeScript uses camelCase.
    # Both implementations have identical logic and behavior.
    return self._do_something()
```

```typescript
// TypeScript example
someMethod() {
  // Isomorphic: Python uses snake_case for method names, TypeScript uses camelCase.
  // Both implementations have identical logic and behavior.
  return this._doSomething()
}
```

**Key Rules**:
- Both languages MUST contain the identical "Isomorphic:" comment
- The comment appears before the code that differs
- The comment explains WHY the code differs and confirms behavior is identical
- Without an "Isomorphic:" comment, code should be identical across languages

### Isomorphic Test Suites

**Goal**: New developers see literally identical test output in both languages, building confidence in Chatfield's genuine two-language commitment.

**Requirements**:
- Test file names match (e.g., `test_builder.py` → `builder.test.ts`)
- Test descriptions are identical across languages
- Test counts are identical (zero skipped tests)
- Test structure mirrors each other (pytest-describe in Python, Jest describe/it in TypeScript)
- When language differences prevent identical tests, use no-op tests that pass

### Benefits of Isomorphic Development

1. **Developer Confidence**: Identical behavior across languages builds trust
2. **Easy Context Switching**: Developers can work in either language seamlessly
3. **Feature Parity**: No language is second-class; both receive equal attention
4. **Reduced Bugs**: Differences are explicit and documented
5. **Better Collaboration**: Team members can review code in either language

### Examples of Isomorphic Implementation

See the latest `interviewer.py` and `interviewer.ts` files for extensive examples of "Isomorphic:" comments documenting language-specific differences while maintaining conceptual identity.

## Project Structure

```
Chatfield/
├── Documentation/               # Project-wide documentation
│   └── TEST_HARMONIZATION.md    # Test harmonization guide and progress tracking
├── Python/                      # Python implementation (v0.2.0)
│   ├── chatfield/               # Core Python package
│   │   ├── __init__.py          # Main exports and public API
│   │   ├── interview.py         # Base Interview class with field discovery
│   │   ├── interviewer.py       # LangGraph-based conversation orchestration
│   │   ├── field_proxy.py       # FieldProxy string subclass for transformations
│   │   ├── builder.py           # Fluent builder API
│   │   ├── serialization.py     # Interview state serialization
│   │   ├── presets.py           # Common preset configurations
│   │   └── visualization.py     # Graph visualization utilities
│   ├── tests/                   # Test suite (test_*.py naming, pytest-describe structure)
│   │   ├── test_interview.py    # Interview class tests
│   │   ├── test_interviewer.py  # Interviewer orchestration tests
│   │   ├── test_interviewer_conversation.py # Conversation flow tests
│   │   ├── test_builder.py      # Builder API tests
│   │   ├── test_field_proxy.py  # FieldProxy tests
│   │   ├── test_custom_transformations.py # Transformation system tests
│   │   ├── test_conversations.py # End-to-end conversation tests
│   │   └── CLAUDE.md            # Test suite documentation
│   ├── examples/                # Python usage examples
│   │   ├── job_interview.py     # Job application interview example
│   │   ├── restaurant_order.py  # Restaurant ordering conversation
│   │   ├── tech_request.py      # Technical support request form
│   │   └── favorite_number.py   # Simple number collection with validation
│   ├── Makefile                 # Python development shortcuts
│   ├── pyproject.toml           # Python package configuration
│   └── CLAUDE.md                # Python-specific implementation guide
│
└── TypeScript/                  # TypeScript/JavaScript implementation (v0.1.0)
    ├── chatfield/               # TypeScript source code
    │   ├── index.ts             # Main exports and public API
    │   ├── interview.ts         # Base Interview class (mirrors Python)
    │   ├── interviewer.ts       # LangGraph conversation orchestration
    │   ├── field-proxy.ts       # FieldProxy for transformations
    │   ├── builder.ts           # Primary fluent builder API
    │   ├── builder-types.ts     # TypeScript type definitions for builder
    │   ├── types.ts             # Core type definitions
    │   └── integrations/        # Framework integrations
    │       ├── react.ts         # React hooks
    │       ├── react-components.tsx # UI components
    │       └── copilotkit.tsx   # CopilotKit integration
    ├── tests/                   # Jest test suite (*.test.ts naming, mirrors Python)
    │   ├── interview.test.ts    # Interview class tests (mirrors test_interview.py)
    │   ├── interviewer.test.ts  # Interviewer orchestration tests
    │   ├── interviewer_conversation.test.ts # Conversation flow tests
    │   ├── builder.test.ts      # Builder API tests
    │   ├── field_proxy.test.ts  # FieldProxy implementation tests
    │   ├── custom_transformations.test.ts # Transformation system tests
    │   ├── conversations.test.ts # End-to-end conversation tests
    │   ├── integration/         # Integration test scenarios
    │   │   └── react.ts        # React hooks integration tests
    │   └── CLAUDE.md            # Test suite documentation
    ├── examples/                # TypeScript/JavaScript examples
    │   ├── basic-usage.ts       # Simple builder pattern example
    │   ├── job-interview.ts     # Job application (mirrors Python)
    │   ├── restaurant-order.ts  # Restaurant ordering
    │   ├── schema-based.ts      # Schema-driven approach
    │   └── type-safe-demo.ts    # TypeScript type inference demo
    ├── package.json             # Node package configuration
    ├── tsconfig.json            # TypeScript compiler configuration
    ├── jest.config.js           # Jest testing configuration
    ├── minimal.ts               # Minimal OpenAI API test script
    └── CLAUDE.md                # TypeScript-specific implementation guide
```

## Development Commands

### Python Implementation (Python/)

```bash
# Setup & Installation
cd Python
python -m venv .venv                                # Create virtual environment
source .venv/bin/activate                           # Activate venv (Linux/Mac)
pip install -e ".[dev]"                             # Install with dev dependencies

# Testing
python -m pytest                                    # Run all tests
python -m pytest tests/test_interview.py            # Run specific test file
python -m pytest -k "test_name"                     # Run specific test by name
python -m pytest -m "not slow"                      # Skip slow tests
python -m pytest -m "requires_api_key"              # Run only API tests

# Code Quality
make format                                          # Format with black & isort
make lint                                            # Run flake8 linting
make typecheck                                       # Run mypy type checking
make test-cov                                        # Run tests with coverage report

# Build & Distribution
make build                                           # Build distribution packages
pip install -e .                                     # Development install

# Running Examples
cd examples && python job_interview.py              # Run any example
python -c "from chatfield import Interview"         # Quick import test
```

### TypeScript/JavaScript Implementation (TypeScript/)

```bash
# Setup & Installation
cd TypeScript
npm install                                          # Install dependencies

# Development & Build
npm run build                                        # Compile TypeScript to dist/
npm run dev                                          # Watch mode compilation
npm run clean                                        # Remove dist/ directory

# Testing
npm test                                             # Run Jest test suite
npm run test:watch                                   # Watch mode testing
npm test -- interview.test.ts                       # Run specific test file

# Code Quality
npm run lint                                        # ESLint checks

# Running Examples
npm run min                                          # Run minimal.ts OpenAI test
npx tsx examples/basic-usage.ts                     # Run any example directly
node dist/examples/basic-usage.js                   # Run compiled example

# Quick Tests
npx tsx minimal.ts                                  # Test OpenAI API connection
```

## Architecture Overview

### Core Concepts (Both Implementations)

1. **Interview**: Main class that defines fields to collect via builder API
2. **Field Definitions**: Builder calls that define data fields
3. **Field Specifications**: Validation rules (must, reject, hint) applied to fields
4. **Field Transformations**: Type casts (as_int, as_bool, etc.) computed by LLM
5. **Interviewer**: Orchestrates conversation flow using LangGraph and LLMs
6. **FieldProxy**: String subclass providing dot-access to transformations
7. **State Management**: LangGraph manages conversation state and transitions

### Python Implementation Details

- **Primary API**: Fluent builder pattern (`chatfield().field().must()`)
- **Orchestration**: LangGraph state machine with nodes and edges
- **Field Discovery**: Via builder pattern calls
- **Data Storage**: `_chatfield` dictionary structure on Interview instances
- **Transformations**: FieldProxy provides `field.as_int`, `field.as_lang_fr`, etc.
- **Testing**: pytest with pytest-describe for BDD-style test organization
- **Dependencies**: langchain (0.3.27+), langgraph (1.0.0a3+), langchain-openai (0.3.29+), openai (1.99.6+), pydantic (2.11.7+)

### TypeScript Implementation Details

- **Primary API**: Fluent builder pattern (`chatfield().field().must()`)
- **Alternative APIs**: Schema-based
- **Orchestration**: LangGraph TypeScript with state management (1.0.0a3+)
- **Type Safety**: Full TypeScript type inference and checking
- **React Integration**: Hooks (`useConversation`) and components
- **CopilotKit**: Sidebar component for conversational UI
- **Testing**: Jest with test structure mirroring Python implementation
- **Dependencies**: @langchain/core (0.3.72+), @langchain/langgraph (1.0.0a3+), @langchain/openai (0.6.9+), openai (4.70.0+), zod, reflect-metadata

### Isomorphic Synchronization Requirements

**CRITICAL**: Both implementations follow isomorphic development principles:
- **File names**: Match across languages (e.g., `interview.py` → `interview.ts`)
- **Class/function names**: Identical names (e.g., `Interview`, `Interviewer`, `FieldProxy`)
- **Method names**: Preserved across languages (e.g., `_name()`, `_pretty()`, `as_int`)
- **Logic**: Identical algorithms and control flow
- **Test structure**: Mirror each other (e.g., `test_builder.py` → `builder.test.ts`)
- **Test descriptions**: Match exactly between implementations
- **Test counts**: Identical (zero skipped tests)
- **Deviations**: Only for language-specific requirements (e.g., async/await, TypeScript types)
- **Documentation**: Use "Isomorphic:" comments in both languages for any differences
- **Test organization**: Both use BDD-style (pytest-describe in Python, nested describe/it in Jest)

## Key Files to Understand

### Python Core Files
- `chatfield/interview.py`: Base Interview class, field discovery, _chatfield structure
- `chatfield/interviewer.py`: LangGraph orchestration, tool generation, state management
- `chatfield/builder.py`: Fluent builder API
- `chatfield/field_proxy.py`: String subclass for transformation access
- `chatfield/serialization.py`: State serialization for LangGraph

### TypeScript Core Files
- `chatfield/interview.ts`: Base Interview class (mirrors Python implementation)
- `chatfield/interviewer.ts`: LangGraph TypeScript orchestration
- `chatfield/builder.ts`: Primary fluent builder API
- `chatfield/field-proxy.ts`: FieldProxy implementation for transformations
- `chatfield/types.ts`: Core TypeScript type definitions

## Testing Approach

### Test Harmonization Philosophy

**CRITICAL**: Both implementations maintain **identical test suite structure** with **zero skipped tests**. This is a core principle of the Chatfield project.

**No-Skip Policy**:
- **NEVER use `@pytest.mark.skip` or `it.skip()` in test suites**
- When language differences prevent identical behavior, implement a **no-op test that passes** rather than skipping
- The test should document the difference with comments but still execute and pass
- **Goal**: New developers see literally identical test counts and outcomes in both languages
- **Rationale**: Builds confidence in Chatfield's genuine two-language commitment

**Example Pattern for Language Differences**:
```python
# Python: API key validation happens lazily, not at initialization
def it_throws_when_no_api_key_provided():
    """Throws when no api key provided."""
    # NOTE: Python's init_chat_model validates lazily at invocation.
    # TypeScript validates at initialization. This test documents
    # the difference but implements no-op behavior.
    interview = chatfield().field("name").build()
    interviewer = Interviewer(interview, base_url='https://proxy.com')
    assert interviewer is not None  # Passes - documents difference
```

See `Documentation/TEST_HARMONIZATION.md` for the complete harmonization guide, naming conventions, and progress tracking.

### Python Tests
- **Framework**: pytest with pytest-describe for BDD-style organization
- **Structure**: Nested `describe_*` and `it_*` functions for test organization
- **Unit Tests**: Individual component testing (builder API, field discovery)
- **Integration Tests**: Component interaction testing with mock LLMs
- **Live API Tests**: Real OpenAI API tests (marked with `@pytest.mark.requires_api_key`)
- **Coverage**: Run `make test-cov` for HTML coverage report in `htmlcov/`
- **Test Files**: `test_*.py` naming convention in `tests/` directory
- **Test Harmonization**: Test names and descriptions match TypeScript implementation exactly
- **No Skips**: Zero skipped tests - use no-op tests instead

### TypeScript Tests
- **Framework**: Jest with ts-jest for TypeScript support
- **Structure**: Nested `describe/it` blocks mirroring Python's pytest-describe
- **Unit Tests**: Component testing with mock backends
- **Integration Tests**: End-to-end scenarios in `tests/integration/`
- **Coverage**: Generated in `coverage/` directory
- **Test Files**: `*.test.ts` naming convention (mirrors Python's `test_*.py`)
- **Configuration**: `jest.config.js` and `tsconfig.test.json`
- **Test Harmonization**: Test names and descriptions match Python implementation exactly
- **No Skips**: Zero skipped tests - use no-op tests instead

## API Key Configuration

Both implementations require OpenAI API key:

```bash
# Option 1: Environment variable
export OPENAI_API_KEY=your-api-key

# Option 2: .env file in project root
echo "OPENAI_API_KEY=your-api-key" > .env

# Option 3: Pass to Interviewer constructor
interviewer = Interviewer(interview, api_key="your-api-key")
```

## Common Development Tasks

### Adding a New Builder Method
1. Add method to builder class in `chatfield/builder.ts`
2. Update type definitions in `chatfield/builder-types.ts`
3. Export from `chatfield/index.ts`
4. Handle in interviewer tool generation
5. Write tests in `tests/builder.test.ts`
6. Add example to `examples/basic-usage.ts`

### Running Examples
```bash
# Python
cd Python/examples
python job_interview.py
python restaurant_order.py

# TypeScript
cd TypeScript
npx tsx examples/basic-usage.ts
npx tsx examples/job-interview.ts
```

## Important Patterns

### Field Value Access (Python)
```python
# During definition
interview = chatfield()\
    .field("age", "Your age")\
    .must("be specific")\
    .as_int()\
    .as_lang("fr")\
    .build()

# After collection
interview.age              # "25" (base string value)
interview.age.as_int       # 25 (integer)
interview.age.as_lang_fr   # "vingt-cinq" (French translation)
interview.age.as_quote     # "I am 25 years old" (original quote)
```

### Builder Pattern (TypeScript)
```typescript
const Form = chatfield()
  .type("Contact Form")
  .desc("Collect contact information")
  .field("name", "Your full name")
    .must("include first and last")
    .hint("Format: First Last")
  .field("email", "Email address")
    .must("be valid email format")
    .as_string()  // Explicit type
  .field("age", "Your age")
    .as_int()
    .must("be between 18 and 120")
  .build()

// After collection
const result = await Interviewer.go()
result.name        // string
result.age         // number (transformed)
```

### Builder Pattern (Python)
```python
interview = chatfield()\
    .alice("Interviewer")\
    .alice_trait("friendly and professional")\
    .bob("Job Candidate")\
    .field("desired_position", "What position are you applying for?")\
        .must("include company name")\
        .must("mention specific role")\
    .field("years_experience", "Years of relevant experience")\
        .as_int()\
        .must("be realistic number")\
    .field("languages", "Programming languages you know")\
        .as_multi(["Python", "JavaScript", "Go", "Rust"])\
    .build()
```

## Validation and Transformation

Both implementations use LLM-powered validation and transformation:

### Validation Methods
- `.must()`: Requirements the response must meet
- `.reject()`: Patterns to avoid in responses  
- `.hint()`: Guidance shown to the user

### Transformation Methods
- `.as_int()`: Parse to integer
- `.as_float()`: Parse to float
- `.as_bool()`: Parse to boolean
- `.as_list()`: Parse to list/array
- `.as_json()`: Parse as JSON object
- `.as_percent()`: Parse to 0.0-1.0 range
- `.as_lang('code')`: Translate to language

### Choice Cardinality
- `.as_one()`: Choose exactly one option
- `.as_maybe()`: Choose zero or one option
- `.as_multi()`: Choose one or more options
- `.as_any()`: Choose zero or more options

## LangGraph Integration

Both implementations use LangGraph for conversation orchestration:

### Graph Structure
```
┌──────────┐     ┌───────┐     ┌────────┐
│initialize│ --> │ think │ --> │ listen │
└──────────┘     └───────┘     └────────┘
                     ^              │
                     │              v
                ┌────────┐     ┌───────┐
                │teardown│ <-- │ tools │
                └────────┘     └───────┘
```

### Node Responsibilities
- **initialize**: Setup conversation, generate system prompt
- **think**: LLM generates next message or decides to use tools
- **listen**: Wait for user input (interrupt point)
- **tools**: Process field updates with validation
- **teardown**: Complete conversation, final message

## Environment Configuration

### VSCode Settings (.vscode/settings.json)
- Python interpreter: Uses `python` command (not python3)
- Python testing: pytest enabled with chatfield/tests path
- Auto-formatting: Black and isort on save
- Type checking: Basic mode with auto-imports

### Python Environment
- Virtual environment: `.venv` in Python/
- Python version: 3.8+ required
- Package mode: Editable install with `pip install -e .`

### TypeScript Environment  
- Node version: 20.0.0+ recommended
- TypeScript: 5.0.0+ with strict mode
- Module resolution: CommonJS for compatibility

## Known Considerations

1. **Python uses `python` command**: Always use `python`, not `python3`, as .venv is configured for `python`
2. **Test harmonization**: Both implementations use BDD-style test organization with matching test descriptions
3. **LangGraph versions**: Python uses langgraph 1.0.0a3+, TypeScript uses @langchain/langgraph 1.0.0a3+
4. **React focus**: TypeScript implementation prioritizes React/UI integration
5. **API rate limits**: Consider rate limiting for production use
6. **Thread safety**: Each Interviewer maintains separate thread ID
7. **Transformation computation**: All transformations computed by LLM during collection, not post-processing
8. **Field discovery**: Both implementations use builder calls for field definition
9. **State persistence**: LangGraph checkpointer allows conversation resumption
10. **Prompt engineering**: Validation quality depends on prompt crafting
11. **Import differences**: Python uses relative imports, TypeScript uses absolute from chatfield/
12. **Async patterns**: TypeScript uses async/await throughout, Python uses sync with async options

## Debugging Tips

### Python Debugging
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Inspect Interview structure
print(interview._chatfield)

# Check field metadata
print(interview._chatfield['fields']['field_name'])

# View LangGraph state
print(interviewer.graph.get_state())
```

### TypeScript Debugging
```typescript
// Enable LangSmith tracing
process.env.LANGCHAIN_TRACING_V2 = "true"

// Inspect Interview state
console.log(interview._chatfield)

// View generated tools
console.log(interviewer.tools)

// Check graph execution
const result = await interviewer.graph.invoke(...)
console.log(result)
```

## Contributing Guidelines

1. **Isomorphic first**: Maintain the isomorphic principle—both implementations are equal first-class citizens
2. **Synchronize implementations**: Keep Python and TypeScript code structures, names, and logic identical
3. **Document deviations**: Use "Isomorphic:" comments in both languages for any necessary differences
4. **Test coverage**: Write tests for all new features using BDD style with identical structure
5. **Test naming**: Use identical test descriptions between Python and TypeScript
6. **No-skip policy**: NEVER skip tests - use no-op tests that pass to maintain identical test counts
7. **Parallel development**: Implement features in both languages simultaneously when possible
8. **Documentation**: Update CLAUDE.md files when adding features, maintaining consistency
9. **Examples**: Provide example usage for new functionality in both languages
10. **Type safety**: Ensure full type coverage in TypeScript
11. **Prompt quality**: Test prompts with various LLM providers
12. **Error handling**: Gracefully handle API failures and edge cases
13. **Code style**: Follow language-specific conventions (Black for Python, ESLint for TypeScript)
14. **Version sync**: Update version numbers in both pyproject.toml and package.json together
15. **GitHub issues**: Keep issues concise (~100-200 words), with clear title, structured sections (using headers/bullets), and focused on a single concern