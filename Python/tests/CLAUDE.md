# Python Test Suite - CLAUDE.md

This file provides guidance for working with the Python test suite.

## Overview

This directory contains the comprehensive test suite for Chatfield Python, using pytest with pytest-describe for BDD-style organization. Tests validate builder functionality, field discovery, interview orchestration, and transformation capabilities.

**CRITICAL**: These tests are part of an **isomorphic test suite**. Python and TypeScript test implementations maintain identical structure, test names, test descriptions, and test counts.

**See**: [../../Documentation/TESTING_Architecture.md](../../Documentation/TESTING_Architecture.md) for complete testing philosophy and [../../Documentation/Isomorphic_Development.md](../../Documentation/Isomorphic_Development.md) for isomorphic principles.

## Isomorphic Testing Principles

1. **Identical Test Counts**: Python and TypeScript must have exactly the same number of tests
2. **Identical Test Names**: Test descriptions match exactly across languages
3. **Identical Structure**: File organization and test grouping mirror TypeScript exactly
4. **Zero Skipped Tests**: NEVER use `@pytest.mark.skip`—use no-op tests that pass instead
5. **Document Differences**: Use "Isomorphic:" comments to explain language-specific test behavior

### Mapping to TypeScript Tests

| Python File | TypeScript File | Structure |
|-------------|----------------|-----------|
| `test_interview.py` | `interview.test.ts` | `describe_interview()` ↔ `describe('Interview')` |
| `test_builder.py` | `builder.test.ts` | `describe_builder()` ↔ `describe('Builder')` |
| `test_interviewer.py` | `interviewer.test.ts` | `describe_interviewer()` ↔ `describe('Interviewer')` |

**Goal**: New developers see literally identical test output in both languages, building confidence in Chatfield's genuine two-language commitment.

## Test Files

```
tests/
├── test_interview.py         # Core Interview class tests
├── test_interviewer.py       # Interviewer orchestration tests
├── test_interviewer_conversation.py  # Conversation flow tests
├── test_builder.py           # Builder API tests
├── test_field_proxy.py       # FieldProxy tests
├── test_custom_transformations.py  # Transformation system tests
├── test_conversations.py     # End-to-end conversation tests
└── CLAUDE.md                 # This file
```

### Key Test Files

- **test_interview.py**: Core Interview class, field discovery, property access, state management
- **test_interviewer.py**: Interviewer orchestration, LangGraph integration, tool binding
- **test_interviewer_conversation.py**: Conversation flow, message handling, state transitions
- **test_builder.py**: Fluent builder API, method chaining, field configuration
- **test_field_proxy.py**: FieldProxy string behavior, transformation properties, attribute access
- **test_custom_transformations.py**: as_int(), as_float(), as_bool(), as_lang(), cardinality methods
- **test_conversations.py**: Integration tests with real conversation scenarios

## Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_interview.py

# Run specific test by name
python -m pytest -k "test_name"

# Run tests matching pattern
python -m pytest -k "field"

# Run with verbose output
python -m pytest -v

# Run with coverage report
python -m pytest --cov=chatfield --cov-report=html

# Run excluding slow/API tests
python -m pytest -m "not slow and not requires_api_key"
```

**See**: [../../Documentation/Commands.md](../../Documentation/Commands.md) for complete command reference.

## Test Structure

Tests use pytest-describe for BDD-style organization matching TypeScript:

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
- **Describe blocks**: `describe_*` functions group related tests (mirrors TypeScript's `describe()`)
- **Test functions**: `it_*` functions describe specific behaviors (mirrors TypeScript's `it()`)
- **Docstrings**: Provide clear descriptions matching TypeScript test names

## Test Organization

1. **Unit Tests**: Individual component testing (builder API, field discovery)
2. **Integration Tests**: Component interaction testing with mock LLMs
3. **Live API Tests**: Real OpenAI API tests (marked with `@pytest.mark.requires_api_key`)

### Mocking Strategy

```python
# Common mock patterns:

# 1. Mock LLM Backend
class MockLLM:
    def invoke(self, messages):
        return AIMessage(content="mocked response")

# 2. Mock Interviewer with predetermined responses
mock_responses = {
    'field_name': 'predetermined value'
}
```

**See**: [../../Documentation/TESTING_Architecture.md](../../Documentation/TESTING_Architecture.md) for detailed testing approach.

## Test Markers

```bash
# Skip tests requiring API key
python -m pytest -m "not requires_api_key"

# Run only fast unit tests
python -m pytest -m "not slow"

# Run integration tests only
python -m pytest -m "integration"
```

## Adding New Tests

When creating new tests, follow the isomorphic testing approach:

1. **Check TypeScript first**: Look for the corresponding TypeScript test in `../../TypeScript/tests/`
2. **Match structure exactly**: Place test in the same file structure as TypeScript
3. **Follow BDD structure**: Use `describe_*` and `it_*` functions that mirror TypeScript's describe/it
4. **Identical descriptions**: Use test descriptions that match TypeScript exactly
5. **Include docstrings**: Docstrings should match TypeScript test descriptions
6. **Isomorphic comments**: If test behavior differs, add "Isomorphic:" comments in both files
7. **No skipping**: Use no-op tests that pass instead of `@pytest.mark.skip`
8. **Verify counts**: Ensure test counts remain identical between Python and TypeScript

### Example of Harmonized Test

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

## Coverage Goals

- Unit test coverage > 80%
- Integration test coverage for all major workflows
- Edge cases and error conditions tested
- Performance regression tests for critical paths

## Common Issues

- **ImportError**: Ensure chatfield package is installed: `pip install -e ..`
- **Missing API Key**: Set OPENAI_API_KEY or mark test with `@pytest.mark.requires_api_key`
- **Flaky Tests**: Use mocks instead of real API calls for determinism
- **Slow Tests**: Mark with `@pytest.mark.slow` and optimize or mock
- **State Pollution**: Use fixtures and proper test isolation

## Additional Resources

- **Testing Philosophy**: [../../Documentation/TESTING_Architecture.md](../../Documentation/TESTING_Architecture.md)
- **Isomorphic Development**: [../../Documentation/Isomorphic_Development.md](../../Documentation/Isomorphic_Development.md)
- **Python Implementation**: [../CLAUDE.md](../CLAUDE.md)
- **TypeScript Tests**: [../../TypeScript/tests/CLAUDE.md](../../TypeScript/tests/CLAUDE.md) for comparison
