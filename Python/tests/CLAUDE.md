# CLAUDE.md

This file provides guidance to Claude Code when working with the Python test suite in this directory.

## Overview

This directory contains the comprehensive test suite for the Chatfield Python library, covering unit tests, integration tests, and conversation flow tests. The tests validate decorator functionality, field discovery, interview orchestration, and transformation capabilities. The test suite uses pytest with pytest-describe for BDD-style test organization that harmonizes with the TypeScript implementation.

## Project Structure

```
Python/tests/
├── __init__.py                      # Test package initialization
├── test_interview.py                # Core Interview class tests
├── test_interviewer.py              # Interviewer orchestration tests
├── test_interviewer_conversation.py # Conversation flow and state tests
├── test_builder.py                  # Builder API and chaining tests
├── test_field_proxy.py              # FieldProxy string subclass tests
├── test_custom_transformations.py   # Transformation decorator tests
├── test_conversations.py            # Full conversation integration tests
└── CLAUDE.md                        # This documentation file
```

## Key Files

### test_interview.py
- **Purpose**: Tests the core Interview class functionality
- **Coverage**: Field discovery, property access, state management
- **Structure**: Uses `describe_interview` with nested `describe_*` and `it_*` functions
- **Test Examples**:
  - `describe_field_discovery` → `it_uses_field_name_when_no_description`
  - `describe_field_access` → `it_returns_none_for_uncollected_fields`
  - `describe_completion_state` → `it_starts_with_done_as_false`
- **Focus**: Base class behavior without LLM interaction

### test_interviewer.py
- **Purpose**: Tests the Interviewer class that orchestrates conversations
- **Coverage**: LangGraph integration, tool binding, state transitions
- **Structure**: BDD-style with `describe_interviewer` and nested functions
- **Test Examples**:
  - `describe_initialization` → `it_creates_interviewer_with_default_model`
  - `describe_tool_generation` → `it_generates_tools_for_all_fields`
- **Mock Strategy**: Uses mock LLM backends for fast, deterministic tests

### test_interviewer_conversation.py
- **Purpose**: Tests conversation flow and message handling
- **Coverage**: State management, field collection, validation flow
- **Structure**: BDD-style organization matching TypeScript tests
- **Test Examples**:
  - `describe_conversation_flow` → `it_handles_multi_turn_conversations`
  - `describe_field_progression` → `it_collects_fields_in_order`
- **Focus**: Multi-turn conversation dynamics

### test_builder.py
- **Purpose**: Tests the fluent builder API
- **Coverage**: Method chaining, field configuration, decorator application
- **Structure**: `describe_builder` with nested test functions
- **Test Examples**:
  - `describe_chaining` → `it_supports_method_chaining`
  - `describe_field_configuration` → `it_applies_must_rules`
  - `describe_transformations` → `it_adds_type_transformations`
- **Validation**: Ensures builder creates correct Interview instances

### test_field_proxy.py
- **Purpose**: Tests the FieldProxy string subclass
- **Coverage**: String behavior, transformation properties, attribute access
- **Structure**: `describe_field_proxy` with nested describe blocks
- **Test Examples**:
  - `describe_string_behavior` → `it_acts_as_normal_string`
  - `describe_transformations` → `it_provides_transformation_access`
  - `describe_attribute_access` → `it_returns_transformation_values`
- **Special**: Tests dynamic property generation (`.as_int`, `.as_lang_fr`, etc.)

### test_custom_transformations.py
- **Purpose**: Tests transformation decorators
- **Coverage**: `@as_int`, `@as_float`, `@as_bool`, `@as_lang.*`, cardinality
- **Structure**: `describe_transformations` with type-specific describe blocks
- **Test Examples**:
  - `describe_numeric_transformations` → `it_transforms_to_int`
  - `describe_language_transformations` → `it_translates_to_french`
  - `describe_cardinality` → `it_chooses_one_option`
- **Validation**: Ensures transformations are properly registered

### test_conversations.py
- **Purpose**: Integration tests with real conversation scenarios
- **Coverage**: End-to-end conversation flows, complex validations
- **Structure**: `describe_conversations` with scenario-based tests
- **Test Examples**:
  - `describe_full_conversations` → `it_completes_job_interview`
  - `describe_edge_cases` → `it_handles_invalid_responses`
  - `describe_validation` → `it_enforces_must_rules`
- **Note**: May use `@pytest.mark.requires_api_key` for live API tests

## Development Commands

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_interview.py

# Run specific test class
python -m pytest tests/test_interview.py::TestInterviewBasics

# Run specific test method
python -m pytest tests/test_interview.py::TestInterviewBasics::test_field_access_before_collection

# Run tests matching pattern
python -m pytest -k "test_field"

# Run with verbose output
python -m pytest -v

# Run with coverage report
python -m pytest --cov=chatfield --cov-report=html

# Run excluding slow/API tests
python -m pytest -m "not slow and not requires_api_key"
```

### Test Markers

```bash
# Skip tests requiring API key
python -m pytest -m "not requires_api_key"

# Run only fast unit tests
python -m pytest -m "not slow"

# Run integration tests only
python -m pytest -m "integration"
```

## Architecture Notes

### Test Organization

1. **Unit Tests**: Test individual components in isolation
   - Use mocks for external dependencies
   - Focus on single responsibility
   - Fast execution (< 1 second per test)

2. **Integration Tests**: Test component interactions
   - May use real LangGraph but mock LLM
   - Test state transitions and data flow
   - Medium execution time

3. **End-to-End Tests**: Test complete workflows
   - May use real OpenAI API (marked appropriately)
   - Test full conversation flows
   - Slower execution, optional in CI

### Mocking Strategy

```python
# Common mock patterns used:

# 1. Mock LLM Backend
class MockLLM:
    def invoke(self, messages):
        return AIMessage(content="mocked response")

# 2. Mock Interviewer with predetermined responses
mock_responses = {
    'field_name': 'predetermined value'
}

# 3. Patch decorators for testing
@patch('chatfield.decorators.must')
def test_validation(mock_must):
    # Test validation logic
```

### State Management Testing

- Tests verify proper state initialization
- Validate state transitions during collection
- Ensure field values are properly stored
- Check completion detection logic

## Testing Approach

### BDD Test Structure

Tests use pytest-describe for BDD-style organization that matches TypeScript:

```python
def describe_component():
    """Tests for the Component."""
    
    def describe_feature():
        """Tests for specific feature."""
        
        def it_does_something_specific():
            """Clear description of expected behavior."""
            # Arrange - Set up test data and mocks
            interview = create_test_interview()
            
            # Act - Perform the operation
            result = interview.some_method()
            
            # Assert - Verify the outcome
            assert result == expected_value
```

### Test Naming Convention
- **Describe blocks**: `describe_*` functions group related tests
- **Test functions**: `it_*` functions describe specific behaviors
- **Docstrings**: Provide clear descriptions matching TypeScript test names

### Coverage Goals

- Unit test coverage > 80%
- Integration test coverage for all major workflows
- Edge cases and error conditions tested
- Performance regression tests for critical paths

### Mock vs Real Testing

1. **Always Mock**: External API calls, file I/O, network requests
2. **Sometimes Mock**: LangGraph components (for speed)
3. **Never Mock**: Core business logic, decorators, field discovery

## Important Patterns

### Fixture Usage

```python
@pytest.fixture
def basic_interview():
    """Standard interview fixture for testing."""
    return (chatfield()
        .type("TestInterview")
        .field("name").desc("Your name")
        .build())

# Used within describe blocks:
def describe_with_fixtures():
    @pytest.fixture
    def interview():
        return create_test_interview()
    
    def it_uses_fixture(interview):
        assert interview is not None
```

### Parameterized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("42", 42),
    ("3.14", 3),
    ("-10", -10),
])
def test_as_int_transformation(input, expected):
    # Test transformation with multiple inputs
```

### Async Test Support

```python
@pytest.mark.asyncio
async def test_async_interview():
    # Test async interview operations
    result = await interviewer.arun()
```

## Known Considerations

1. **Test Harmonization**: Test names and descriptions match TypeScript exactly
2. **BDD Structure**: Use pytest-describe for consistent organization
3. **Test Isolation**: Each test should be independent and not affect others
4. **Mock Cleanup**: Ensure mocks are properly reset between tests
5. **API Key Tests**: Tests requiring real API keys are marked and skippable
6. **Performance**: Keep unit tests fast (< 10 seconds for entire suite)
7. **Determinism**: Tests should produce same results on every run
8. **Python Path**: Tests may need to add parent directory to sys.path
9. **State Leakage**: Be careful with class-level attributes in Interview
10. **LangGraph State**: Test state reducers and merging logic carefully

## Adding New Tests

When creating new tests:

1. Place in appropriate test file based on component being tested
2. Follow BDD structure with `describe_*` and `it_*` functions
3. Match TypeScript test descriptions exactly for corresponding tests
4. Use descriptive names that explain what's being tested
5. Include docstrings that match TypeScript test descriptions
6. Add appropriate markers (`@pytest.mark.slow`, `@pytest.mark.requires_api_key`)
7. Use fixtures for common setup
8. Mock external dependencies
9. Test both success and failure cases
10. Update this CLAUDE.md file if adding new test files

### Example of Harmonized Test:
```python
# Python (test_interview.py)
def describe_interview():
    def describe_field_discovery():
        def it_uses_field_name_when_no_description():
            """Uses field name as description when none provided."""
            # Test implementation

# TypeScript (interview.test.ts)
describe('Interview', () => {
  describe('field discovery', () => {
    it('uses field name when no description', () => {
      // Test implementation
    })
  })
})
```

## Common Issues and Solutions

- **ImportError**: Ensure chatfield package is installed: `pip install -e ..`
- **Missing API Key**: Set OPENAI_API_KEY or mark test with `@pytest.mark.requires_api_key`
- **Flaky Tests**: Use mocks instead of real API calls for determinism
- **Slow Tests**: Mark with `@pytest.mark.slow` and optimize or mock
- **State Pollution**: Use fixtures and proper test isolation

## Test Data

Common test data patterns:

```python
# Standard test interview
TEST_FIELDS = {
    'name': 'Your full name',
    'email': 'Your email address',
    'age': 'Your age'
}

# Mock responses for testing
MOCK_RESPONSES = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'age': '30'
}

# Validation test cases
VALIDATION_CASES = [
    ('valid@email.com', True),
    ('invalid-email', False)
]
```