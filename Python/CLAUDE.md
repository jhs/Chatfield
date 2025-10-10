# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Chatfield is a Python package (v0.2.0) that transforms data gathering from rigid forms into conversational dialogues powered by LLMs. It uses a fluent builder API to define fields and validation rules, then leverages LangGraph to orchestrate natural conversations that collect structured data.

## Project Architecture

### Core Components

1. **Interview System** (`chatfield/`)
   - `interview.py` - Base Interview class with field discovery and _chatfield dictionary structure
   - `interviewer.py` - LangGraph-based conversation orchestration with state management
   - `field_proxy.py` - FieldProxy string subclass providing transformation access via attributes
   - `builder.py` - Fluent builder API for defining interviews
   - `serialization.py` - Interview state serialization for LangGraph
   - `presets.py` - Common preset configurations
   - `visualization.py` - Graph visualization utilities

2. **Security Evaluation Suite** (`evals/`)
   - `eval_cast_security.py` - Main evaluation runner for security testing
   - `test_*.py` - DeepEval-based test modules for various security aspects
   - `metrics/` - Custom DeepEval metrics for security and compliance
   - `datasets/` - Test datasets and attack patterns
   - `attacks.json` - 16 different attack patterns for security testing

3. **Results Visualization** (`streamlit_results.py`)
   - Streamlit dashboard for visualizing DeepEval security test results
   - Displays model performance across different attack patterns
   - Provides interactive filtering and export capabilities
   - Visualizes success rates, score distributions, and cost analysis

### Data Flow Architecture

1. **Definition Phase**: Builder pattern creates Interview with field definitions and validation rules
2. **Conversation Phase**: LangGraph orchestrates state machine with nodes (initialize → think → listen → tools → teardown)
3. **Collection Phase**: LLM validates responses and computes transformations
4. **Access Phase**: FieldProxy provides string values with transformation attributes
5. **Evaluation Phase**: DeepEval tests security against attack patterns
6. **Visualization Phase**: Streamlit dashboard presents evaluation results

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install package with dev dependencies
pip install -e ".[dev]"
```

### Core Development
```bash
# Testing
make test               # Run all tests
make test-cov          # Run with coverage report (HTML in htmlcov/)
python -m pytest tests/test_interview.py       # Run specific test file
python -m pytest -k "test_name"                # Run specific test
python -m pytest -m "not requires_api_key"     # Skip API tests

# Code Quality
make format            # Format with Black & isort
make lint             # Run flake8 linting
make typecheck        # Run mypy type checking
make dev              # Run all checks (format, lint, typecheck, test)

# Build & Distribution
make build            # Build distribution packages
make clean            # Clean build artifacts
```

### Security Evaluation
```bash
# Run security evaluations (requires OPENAI_API_KEY)
cd evals
python eval_cast_security.py                    # Run full evaluation suite
python eval_cast_security.py --build             # Build golden dataset
python eval_cast_security.py --evaluate          # Run evaluation only
python eval_cast_security.py --model gpt-4      # Test specific model

# View evaluation results
streamlit run ../streamlit_results.py           # Launch results dashboard
```

### Running Examples
```bash
cd examples
python job_interview.py        # Job application interview
python restaurant_order.py      # Restaurant ordering conversation
python tech_request.py         # Technical support request
python favorite_number.py      # Simple validation example
```

## Key Implementation Details

### Interview Structure (_chatfield dictionary)
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

### LangGraph State Machine
- **initialize**: Setup conversation, generate system prompt
- **think**: LLM generates next message or decides to use tools
- **listen**: Wait for user input (interrupt point)
- **tools**: Process field updates with validation
- **teardown**: Complete conversation, final message

### Security Evaluation Structure
- Tests 16 attack patterns against exam security
- Uses 7 different LLM models as evaluators
- Generates `results.json` with detailed metrics
- Tracks success rates, scores, costs, and failure reasons

## Testing Philosophy

### Test Organization
- Uses pytest with pytest-describe for BDD-style tests
- Test harmonization with TypeScript implementation (matching test names)
- Categories: Unit tests, Integration tests, Conversation tests, Live API tests

### Security Testing Focus
- **Field Extraction**: Accurate extraction from conversations
- **Validation Compliance**: Enforcement of must/reject rules
- **Information Security**: Prevention of cast/transformation leakage
- **Exam Security**: Protection against answer extraction attacks
- **Conversation Quality**: Natural flow and compliance

## Dependencies

### Core Libraries
- `langchain` (0.3.27+): LLM abstractions and tools
- `langgraph` (1.0.0a3+): Conversation state machine
- `langchain-openai` (0.3.29+): OpenAI integration
- `pydantic` (2.11.7+): Data validation and serialization
- `deepdiff` (6.0.0+): State comparison utilities

### Evaluation & Visualization
- `deepeval`: LLM evaluation framework
- `streamlit`: Interactive dashboard for results
- `plotly`: Data visualization charts
- `pandas`: Data manipulation for analysis

## Important Patterns

### Builder Pattern Usage
```python
interview = chatfield()\
    .field("age", "Your age")\
        .must("be specific")\
        .as_int()\
        .as_lang("fr")\
    .build()

# After collection:
interview.age              # "25" (string)
interview.age.as_int       # 25
interview.age.as_lang_fr   # "vingt-cinq"
```

### Mock LLM for Testing
```python
class MockLLM:
    def invoke(self, messages):
        return AIMessage(content="mocked response")
    def bind_tools(self, tools):
        self.tools = tools
        return self
```

### Streamlit Dashboard Usage
```python
# Load and visualize results
results = load_results("results.json")
df = extract_model_performance(results)
summary = calculate_model_summary(df)
# Interactive charts and filters in Streamlit UI
```

## Environment Configuration

### API Keys
```bash
export OPENAI_API_KEY=your-api-key  # Required for LLM operations
```

### API Initialization Options

The `Interviewer` constructor supports flexible API configuration for different deployment scenarios:

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

# Option 4: Both custom base URL and API key
interviewer = Interviewer(
    interview,
    base_url='https://my-proxy.com/openai',
    api_key='proxy-api-key'
)
```

**Constructor Parameters:**
- `interview` (Interview): The interview instance to orchestrate
- `thread_id` (Optional[str]): Custom thread ID for conversation tracking
- `llm` (Optional): Custom LLM instance (overrides all other LLM config)
- `llm_id` (Optional[str]): LLM model identifier (default: 'openai:gpt-4o')
- `temperature` (Optional[float]): Temperature for LLM generation (default: 0.0)
- `base_url` (Optional[str]): Custom API endpoint (e.g., for LiteLLM proxies)
- `api_key` (Optional[str]): API key (falls back to OPENAI_API_KEY env var)
- `endpoint_security` (Optional[EndpointSecurityMode]): Security mode for endpoint validation ('strict', 'warn', or 'disabled', default: 'disabled')

**Use Cases:**
- **Production**: Use `base_url` to point to a LiteLLM proxy that handles authentication
- **Development**: Use environment variables for simplicity
- **Testing**: Pass explicit `api_key` and `base_url` for test environments
- **Multi-tenant**: Different API keys per Interviewer instance

### Endpoint Security Modes

The `endpoint_security` parameter controls how the Interviewer validates API endpoints to prevent accidental exposure of API keys:

```python
from chatfield import Interviewer, chatfield

interview = chatfield().field("name").build()

# Option 1: Disabled mode (default for server-side Python)
# Allows official endpoints like api.openai.com
interviewer = Interviewer(
    interview,
    api_key='your-api-key',
    base_url='https://api.openai.com/v1',
    endpoint_security='disabled'  # or omit, as this is the default
)

# Option 2: Strict mode
# Blocks official endpoints, requires proxy
interviewer = Interviewer(
    interview,
    api_key='your-api-key',
    base_url='https://my-proxy.com/v1',
    endpoint_security='strict'  # Raises ValueError for api.openai.com, api.anthropic.com
)

# Option 3: Warn mode
# Warns about official endpoints but allows them
interviewer = Interviewer(
    interview,
    api_key='your-api-key',
    base_url='https://api.openai.com/v1',
    endpoint_security='warn'  # Logs warning but continues
)
```

**Security Mode Behavior:**
- **`'disabled'`** (default for Python/server): Detection logic runs and logs debug messages, but allows all endpoints including official ones. Use for server-side applications where API keys are protected.
- **`'warn'`**: Logs warnings to console when official endpoints are detected (api.openai.com, api.anthropic.com), but allows the connection. Useful for development with awareness of potential issues.
- **`'strict'`**: Raises `ValueError` when official endpoints are detected. Forces use of a backend proxy. Recommended for browser deployments (automatically enabled in TypeScript browser environment).

**Dangerous Endpoints Detected:**
- `api.openai.com`
- `api.anthropic.com`

**Note:** Python runs server-side only, so the default is `'disabled'`. The TypeScript implementation defaults to `'strict'` in browser environments where API keys could be exposed to end users.

### Python Version
- Requires Python 3.8+
- Use `python` command (not `python3`) with activated venv
- Virtual environment in `.venv/`

## Known Considerations

1. **Test Harmonization**: Test names must match TypeScript implementation
2. **Security Focus**: Evaluation suite specifically tests information protection
3. **Large Result Files**: `results.json` can be 300KB+, consider pagination
4. **Transformation Computation**: All transformations computed during collection by LLM
5. **Thread Safety**: Each Interviewer maintains separate thread ID
6. **Cost Tracking**: Evaluations track API costs (visible in dashboard)
7. **Field Discovery**: Fields defined via builder pattern, not method inspection