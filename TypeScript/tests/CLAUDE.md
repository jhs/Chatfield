# TypeScript Test Suite - CLAUDE.md

This file provides guidance for working with the TypeScript/JavaScript test suite.

## Overview

This directory contains the comprehensive test suite for Chatfield TypeScript, using Jest with structure mirroring Python's pytest implementation. Tests cover the builder API, Interview class, Interviewer orchestration, transformations, and conversation flows.

**CRITICAL**: These tests are part of an **isomorphic test suite**. TypeScript and Python test implementations maintain identical structure, test names, test descriptions, and test counts.

**See**: [../../Documentation/TESTING_ARCHITECTURE.md](../../Documentation/TESTING_ARCHITECTURE.md) for complete testing philosophy and [../../Documentation/ISOMORPHIC_DEVELOPMENT.md](../../Documentation/ISOMORPHIC_DEVELOPMENT.md) for isomorphic principles.

## Isomorphic Testing Principles

1. **Identical Test Counts**: TypeScript and Python must have exactly the same number of tests
2. **Identical Test Names**: Test descriptions match exactly across languages
3. **Identical Structure**: File organization and test grouping mirror Python exactly
4. **Zero Skipped Tests**: NEVER use `it.skip()` or `test.skip()`—use no-op tests that pass instead
5. **Document Differences**: Use "Isomorphic:" comments to explain language-specific test behavior

### Mapping to Python Tests

| TypeScript File | Python File | Structure |
|----------------|-------------|-----------|
| `interview.test.ts` | `test_interview.py` | `describe('Interview')` ↔ `describe_interview()` |
| `builder.test.ts` | `test_builder.py` | `describe('Builder')` ↔ `describe_builder()` |
| `interviewer.test.ts` | `test_interviewer.py` | `describe('Interviewer')` ↔ `describe_interviewer()` |

**Goal**: New developers see literally identical test output in both languages, building confidence in Chatfield's genuine two-language commitment.

## Test Files

```
tests/
├── interview.test.ts         # Core Interview class tests
├── interviewer.test.ts       # Interviewer orchestration tests
├── interviewer_conversation.test.ts  # Conversation flow tests
├── builder.test.ts           # Builder API tests
├── field_proxy.test.ts       # FieldProxy tests
├── custom_transformations.test.ts  # Transformation system tests
├── conversations.test.ts     # End-to-end conversation tests
├── integration/
│   └── react.ts             # React hooks integration tests
└── CLAUDE.md                 # This file
```

### Key Test Files

- **interview.test.ts**: Core Interview class, field access, state management
- **interviewer.test.ts**: Interviewer orchestration, LLM binding, tool configuration
- **interviewer_conversation.test.ts**: Multi-turn conversation dynamics, message handling
- **builder.test.ts**: Fluent builder API, method chaining, field configuration
- **field_proxy.test.ts**: FieldProxy string-like behavior, transformation access
- **custom_transformations.test.ts**: Type transformations, language transformations, cardinality
- **conversations.test.ts**: End-to-end scenarios, complex validations
- **integration/react.ts**: React hooks and components (TypeScript-specific)

## Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run specific test file
npm test interview.test.ts

# Run tests matching pattern
npm test -- --testNamePattern="field validation"

# Run with coverage
npm test -- --coverage

# Run integration tests only
npm test -- integration/

# Debug tests
node --inspect-brk node_modules/.bin/jest --runInBand

# Run tests with verbose output
npm test -- --verbose
```

**See**: [../../Documentation/COMMANDS.md](../../Documentation/COMMANDS.md) for complete command reference.

## Test Structure

Tests use Jest with structure mirroring Python's pytest-describe:

```typescript
describe('ComponentName', () => {
  // Matches Python's describe_component_name

  describe('feature area', () => {
    // Matches Python's describe_feature_area

    beforeEach(() => {
      // Setup
    })

    afterEach(() => {
      // Cleanup
    })

    it('does something specific', () => {
      // Matches Python's it_does_something_specific
      // Arrange
      const interview = createTestInterview()

      // Act
      const result = interview.someMethod()

      // Assert
      expect(result).toBe(expected)
    })
  })
})
```

### Naming Convention Mapping

| Python | TypeScript | Example |
|--------|------------|---------|
| `describe_interview` | `describe('Interview')` | Top-level component |
| `describe_field_discovery` | `describe('field discovery')` | Feature area |
| `it_uses_field_name_when_no_description` | `it('uses field name when no description')` | Specific test |

## Test Organization

1. **Unit Tests**: Test individual components (mock all external dependencies)
2. **Integration Tests**: Test component interactions (may use real Interview/Interviewer, mock external services)
3. **End-to-End Tests**: Complete workflow tests (full conversation flows, may use real API if marked)

### Mocking Strategy

```typescript
// Mock LLM Backend
class MockLLMBackend {
  temperature = 0.0
  modelName = 'openai:gpt-4o'
  tools: any[] = []
  boundTools: any[] = []

  async invoke(messages: any[]) {
    return { content: 'Mock response' }
  }

  bind(args: any) {
    if (args.tools) {
      this.boundTools = args.tools
    }
    return this
  }

  bindTools(tools: any[]) {
    this.tools = tools
    this.boundTools = tools
    return this
  }

  withStructuredOutput(schema: any) {
    return this
  }
}

// Pass mock LLM directly to Interviewer constructor
const mockLlm = new MockLLMBackend()
const interviewer = new Interviewer(interview, { llm: mockLlm })
```

**See**: [../../Documentation/TESTING_ARCHITECTURE.md](../../Documentation/TESTING_ARCHITECTURE.md) for detailed testing approach.

## Jest Configuration

```json
{
  "preset": "ts-jest",
  "testEnvironment": "node",
  "testMatch": ["**/*.test.ts"],
  "collectCoverageFrom": [
    "chatfield/**/*.ts",
    "!chatfield/**/*.d.ts"
  ]
}
```

## Adding New Tests

When creating new tests, follow the isomorphic testing approach:

1. **Check Python first**: Look for the corresponding Python test in `../../Python/tests/`
2. **Match structure exactly**: Place test in the same file structure as Python
3. **Identical descriptions**: Use test descriptions that match Python exactly
4. **Follow naming convention**: Use `*.test.ts` for files (mirrors Python's `test_*.py`)
5. **BDD structure**: Use `describe()` and `it()` to mirror Python's `describe_*` and `it_*`
6. **Isomorphic comments**: If test behavior differs, add "Isomorphic:" comments in both files
7. **No skipping**: Use no-op tests that pass instead of `it.skip()` or `test.skip()`
8. **Verify counts**: Ensure test counts remain identical between TypeScript and Python

### Example of Harmonized Test

```typescript
// TypeScript (interview.test.ts)
describe('Interview', () => {
  describe('field discovery', () => {
    it('uses field name when no description', () => {
      // Test implementation
    })
  })
})

// Python (test_interview.py)
def describe_interview():
    def describe_field_discovery():
        def it_uses_field_name_when_no_description():
            """Uses field name as description when none provided."""
            # Test implementation
```

## Coverage Goals

- Line coverage: > 80%
- Branch coverage: > 75%
- Function coverage: > 80%
- Statement coverage: > 80%

## Async Testing

```typescript
// Async test pattern
test('should handle async operations', async () => {
  const interviewer = new Interviewer(interview)
  const result = await interviewer.go()
  expect(result).toBeDefined()
})

// With error handling
test('should handle errors', async () => {
  await expect(interviewer.go()).rejects.toThrow('Expected error')
})
```

## Common Issues

- **Module not found**: Ensure correct import paths and build
- **Type errors**: Check TypeScript configuration and types
- **Async timeout**: Increase timeout with `jest.setTimeout(10000)`
- **Mock not working**: Verify mock is before import
- **Coverage gaps**: Add tests for uncovered branches
- **Snapshot failures**: Update with `npm test -- -u`

## Debugging Tests

```bash
# Debug with VS Code
# Add breakpoint and use "Debug Jest Tests" launch config

# Debug with Chrome DevTools
node --inspect-brk node_modules/.bin/jest --runInBand

# Debug specific test
npm test -- --runInBand interview.test.ts
```

## Additional Resources

- **Testing Philosophy**: [../../Documentation/TESTING_ARCHITECTURE.md](../../Documentation/TESTING_ARCHITECTURE.md)
- **Isomorphic Development**: [../../Documentation/ISOMORPHIC_DEVELOPMENT.md](../../Documentation/ISOMORPHIC_DEVELOPMENT.md)
- **TypeScript Implementation**: [../CLAUDE.md](../CLAUDE.md)
- **Python Tests**: [../../Python/tests/CLAUDE.md](../../Python/tests/CLAUDE.md) for comparison
