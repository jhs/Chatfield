# CLAUDE.md

This file provides guidance to Claude Code when working with the Python implementation of Chatfield.

## Overview

Chatfield is a Python package (v0.2.0) that transforms data gathering from rigid forms into conversational dialogues powered by LLMs. It uses a fluent builder API to define fields and validation rules, then leverages LangGraph to orchestrate natural conversations that collect structured data.

## Core Architecture

### Key Design Principles

1. **Builder-based API** - All configuration through fluent method chains
2. **String-based fields** - All field values are strings with transformation access
3. **LLM-powered validation** - Validation through conversational guidance
4. **Stateful conversation** - LangGraph manages conversation state and flow
5. **Transformation proxies** - Field values provide transformed access via attributes

## Project Structure

```
Python/
├── chatfield/                   # Core Python package
│   ├── __init__.py             # Main exports and public API
│   ├── interview.py            # Interview base class with field discovery
│   ├── interviewer.py          # LangGraph-based conversation orchestration
│   ├── field_proxy.py          # FieldProxy string subclass for transformations
│   ├── builder.py              # Fluent builder API
│   ├── serialization.py        # Interview state serialization
│   ├── presets.py              # Common preset configurations
│   └── visualization.py        # Graph visualization utilities
├── tests/                       # Test suite (pytest-describe structure)
│   ├── test_interview.py       # Interview class tests
│   ├── test_interviewer.py     # Interviewer orchestration tests
│   ├── test_interviewer_conversation.py # Conversation flow tests
│   ├── test_builder.py         # Builder API tests
│   ├── test_field_proxy.py     # FieldProxy tests
│   ├── test_custom_transformations.py # Transformation system tests
│   ├── test_conversations.py   # End-to-end conversation tests
│   └── CLAUDE.md               # Test suite documentation
├── examples/                    # Usage examples
│   ├── job_interview.py        # Job application example
│   ├── restaurant_order.py     # Restaurant ordering
│   ├── tech_request.py         # Technical support request
│   └── favorite_number.py      # Simple validation example
├── Makefile                     # Development shortcuts
├── pyproject.toml              # Package configuration
└── README.md                   # User documentation
```

## Core Components

### 1. Interview Class (`interview.py`)

The `Interview` base class manages field definitions and collected data:

```python
class Interview:
    """Base class for conversational data collection."""
    
    def __init__(self, **kwargs):
        # Initialize _chatfield dictionary structure
        self._chatfield = {
            'type': self.__class__.__name__,
            'desc': self.__doc__,
            'roles': {
                'alice': {'type': None, 'traits': []},
                'bob': {'type': None, 'traits': []}
            },
            'fields': {
                # field_name: {
                #     'desc': field description,
                #     'specs': {category: [rules]},  # from must(), reject(), hint()
                #     'casts': {name: cast_info},    # from as_*() methods
                #     'value': None or {value, context, as_quote, ...}
                # }
            }
        }
```

Key features:
- Discovers fields via method definitions
- Stores all metadata in `_chatfield` dictionary
- Provides `__getattribute__` override to return field values as `FieldProxy` instances
- Implements `_done` property to check completion
- Supports serialization via `model_dump()` for LangGraph state

### 2. FieldProxy Class (`interview.py`)

`FieldProxy` is a string subclass that provides transformation access:

```python
class FieldProxy(str):
    """String that provides transformation access via attributes."""
    
    def __new__(cls, value: str, chatfield: Dict):
        # Create string instance with the base value
        instance = str.__new__(cls, value)
        return instance
    
    def __getattr__(self, attr_name: str):
        # Return transformation values
        # e.g., field.as_int, field.as_lang_fr
        llm_value = self._chatfield.get('value')
        if attr_name in llm_value:
            return llm_value[attr_name]
```

This allows natural access patterns:
- `field` - base string value
- `field.as_int` - integer transformation
- `field.as_lang_fr` - French translation
- All string methods work normally

### 3. Builder API (`builder.py`)

Alternative fluent API for defining interviews:

```python
from chatfield.builder import chatfield

interview = (chatfield()
    .type("InterviewType")
    .desc("Interview description")
    .alice("Interviewer role")
    .bob("Interviewee role")
    .field("field_name")
        .desc("Field description")
        .must("validation rule")
        .reject("pattern to avoid")
        .hint("user guidance")
        .as_int()  # Type transformation
    .build())
```

The builder:
- Provides method chaining for field configuration
- Generates Interview instances with proper metadata
- Provides all field configuration options as methods
- Offers excellent IDE autocomplete support

### 4. Interviewer Class (`interviewer.py`)

Manages conversation flow using LangGraph:

```python
class Interviewer:
    """Orchestrates conversational data collection."""
    
    def __init__(self, interview: Interview, thread_id: str = None):
        self.interview = interview
        self.llm = init_chat_model('openai:gpt-4')
        self.graph = self._build_graph()
        
    def _build_graph(self):
        # LangGraph state machine with nodes:
        # - initialize: Setup conversation
        # - think: LLM generates next message
        # - listen: Wait for user input (interrupt)
        # - tools: Process field updates
        # - teardown: Complete conversation
        
    def go(self, user_input: Optional[str]) -> Optional[str]:
        # Process one conversation turn
        # Returns the AI's message as a string
```

The Interviewer:
- Creates LangGraph workflow with conversation nodes
- Generates dynamic tools for each field
- Manages conversation state and checkpointing
- Returns messages for the UI to display

### 4. Builder System (`builder.py`)

The builder system provides a fluent API for defining interviews:

```python
from chatfield import chatfield

interview = chatfield()\
    .type("JobInterview")\
    .desc("Collect job application information")\
    .alice("Interviewer")\
    .bob("Candidate")\
    .field("position", "What position are you applying for?")\
        .must("include company name")\
        .hint("Be specific about role and company")\
    .field("experience", "Years of relevant experience")\
        .as_int()\
        .must("be realistic number")\
    .build()
```

The builder supports:
- **Interview metadata**: `.type()`, `.desc()`, `.alice()`, `.bob()`
- **Field definitions**: `.field(name, description)`
- **Validation rules**: `.must()`, `.reject()`, `.hint()`
- **Type transformations**: `.as_int()`, `.as_float()`, `.as_bool()`, etc.
- **Choice cardinality**: `.as_one()`, `.as_multi()`, `.as_maybe()`, `.as_any()`

## Data Flow

1. **Definition Phase**
   - User defines interview using builder pattern
   - Builder methods configure metadata and field definitions

2. **Initialization Phase**
   - Builder creates Interview instance
   - Builds _chatfield structure from builder configuration
   - Creates field definitions with specs and casts

3. **Conversation Phase**
   - Interviewer creates LangGraph workflow
   - Generates tools for field validation/collection
   - Orchestrates conversation via state machine

4. **Collection Phase**
   - User responses validated by LLM
   - Valid data stored in _chatfield['fields'][name]['value']
   - Includes base value and all transformations

5. **Access Phase**
   - Field access returns FieldProxy instances
   - FieldProxy provides string value and transformation attributes
   - All transformations computed by LLM during collection

## State Management

The system uses LangGraph's state management with custom reducers:

```python
class State(TypedDict):
    messages: Annotated[List[Any], add_messages]
    interview: Annotated[Interview, merge_interviews]

def merge_interviews(a: Interview, b: Interview) -> Interview:
    # Custom reducer that merges Interview states
    # Handles field value updates
```

## Tool Generation

For each field, the Interviewer generates a Pydantic model for tool arguments:

```python
# For a field with as_int() and as_lang('fr') methods:
class FieldModel(BaseModel):
    value: str = Field(description="Natural value")
    context: str = Field(description="Conversational context")
    as_quote: str = Field(description="Direct quote")
    as_int: int = Field(description="Parse as integer")
    as_lang_fr: str = Field(description="Translate to French")
```

## Key Implementation Details

### Field Discovery
Fields are defined through the builder pattern:
- Fields defined via `.field(name, description)` calls
- Builder stores field metadata during construction
- No method inspection required

### Transformation Naming
Transformations follow consistent naming:
- Simple: `as_int`, `as_float`
- Sub-attributes: `as_lang_fr`, `as_bool_even`
- Choices: `as_one_priority`, `as_multi_components`

### Thread Safety
Each Interviewer maintains its own:
- LangGraph checkpointer
- Thread ID for conversation isolation
- Independent state management

## Usage Patterns

### Basic Interview
```python
interview = chatfield()\
    .field("name", "Your name")\
    .field("email", "Your email")\
    .build()

interviewer = Interviewer(interview)

while not interview._done:
    ai_message = interviewer.go(user_input)
    if ai_message:
        print(f"AI: {ai_message}")
    user_input = input("> ")
```

### With Full Builder Configuration
```python
interview = chatfield()\
    .alice("Interviewer")\
    .bob("Candidate")\
    .field("years_experience", "Years of experience")\
        .must("specific role")\
        .as_int()\
        .as_lang("fr")\
    .build()
```

### Accessing Data
```python
# After collection:
interview.years_experience          # "5" (string)
interview.years_experience.as_int   # 5
interview.years_experience.as_lang_fr # "cinq"
```

## Testing Approach

### Test Organization
The test suite uses pytest with pytest-describe for BDD-style test organization:

```python
def describe_interview():
    """Tests for the Interview class."""
    
    def describe_field_discovery():
        """Tests for field discovery and defaults."""
        
        def it_uses_field_name_when_no_description():
            """Uses field name as description when none provided."""
            # Test implementation
```

### Test Categories
1. **Unit tests** - Test individual components in isolation
2. **Integration tests** - Test component interactions with mocked LLMs
3. **Conversation tests** - Test full conversation flows
4. **Live API tests** - Tests with real OpenAI API (marked with `@pytest.mark.requires_api_key`)

### Test Synchronization
Test names and descriptions are harmonized with the TypeScript implementation to ensure feature parity:
- Python: `describe_*` and `it_*` functions
- TypeScript: `describe()` and `it()` blocks
- Both use identical test descriptions for corresponding tests

### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_interview.py

# Run with coverage
python -m pytest --cov=chatfield --cov-report=html

# Skip API tests
python -m pytest -m "not requires_api_key"
```

## Development Commands

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Testing
make test           # Run all tests
make test-cov       # Run with coverage report
make test-fast      # Skip slow/API tests

# Code Quality
make format         # Format with Black & isort
make lint          # Run flake8 linting
make typecheck     # Run mypy type checking

# Build
make build         # Build distribution packages
make clean         # Clean build artifacts
```

## Architecture Notes

### Dependencies
- **langchain** (0.3.27+): LLM abstractions and tools
- **langgraph** (0.6.4+): Conversation state machine
- **langchain-openai** (0.3.29+): OpenAI integration
- **openai** (1.99.6+): Direct OpenAI API client
- **pydantic** (2.11.7+): Data validation and serialization
- **deepdiff** (6.0.0+): State comparison utilities

### Builder API
Chatfield provides a fluent builder API:

```python
from chatfield import chatfield

interview = (chatfield()
    .type("JobApplication")
    .field("position")
        .desc("Desired position")
        .must("include company name")
        .as_string()
    .field("experience")
        .desc("Years of experience")
        .as_int()
        .must("be realistic")
    .build())
```

## Important Patterns

### Mock LLM for Testing
```python
class MockLLM:
    def invoke(self, messages):
        return AIMessage(content="mocked response")
    
    def bind_tools(self, tools):
        self.tools = tools
        return self
```

### State Serialization
Interview instances can be serialized for LangGraph state:
```python
state = interview.model_dump()  # Serialize to dict
interview.model_validate(state)  # Restore from dict
```

## Known Considerations

1. **Python command**: Always use `python`, not `python3` (venv configured)
2. **Test harmonization**: Test names match TypeScript implementation exactly
3. **Import style**: Use relative imports within the package
4. **Field discovery**: Fields defined via builder pattern calls
5. **Transformation naming**: Consistent `as_*` pattern for all transformations
6. **Thread safety**: Each Interviewer maintains separate thread ID
7. **LLM computation**: All transformations computed during collection, not post-processing