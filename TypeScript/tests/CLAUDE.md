# CLAUDE.md

This file provides guidance to Claude Code when working with the TypeScript/JavaScript test suite in this directory.

## Overview

This directory contains the comprehensive test suite for the Chatfield TypeScript/JavaScript library, mirroring the Python implementation's test structure for feature parity. Tests cover the builder API, Interview class, Interviewer orchestration, transformations, and conversation flows using Jest as the testing framework. The test structure uses nested describe/it blocks that correspond exactly to Python's pytest-describe organization.

**IMPORTANT**: These tests are part of an **isomorphic test suite**. The TypeScript and Python test implementations maintain identical structure, test names, test descriptions, and test counts. This is fundamental to Chatfield's isomorphic development philosophy.

## Isomorphic Testing Philosophy

### Core Principles

1. **Identical Test Counts**: TypeScript and Python must have exactly the same number of tests
2. **Identical Test Names**: Test descriptions match exactly (e.g., `it('uses field name when no description')` ↔ `it_uses_field_name_when_no_description`)
3. **Identical Structure**: File organization and test grouping mirror Python exactly
4. **Zero Skipped Tests**: NEVER use `it.skip()` or `test.skip()`—use no-op tests that pass instead
5. **Document Differences**: Use "Isomorphic:" comments to explain language-specific test behavior

### Why Isomorphic Tests Matter

- **Developer Confidence**: Seeing identical test counts in both languages builds trust
- **Feature Parity**: Ensures both implementations truly have the same capabilities
- **Easy Verification**: New developers can quickly verify consistency
- **No Second-Class Citizens**: Both languages are equal first-class implementations

### Mapping to Python Tests

| TypeScript File | Python File | Structure |
|----------------|-------------|-----------|
| `interview.test.ts` | `test_interview.py` | `describe('Interview')` ↔ `describe_interview()` |
| `builder.test.ts` | `test_builder.py` | `describe('Builder')` ↔ `describe_builder()` |
| `interviewer.test.ts` | `test_interviewer.py` | `describe('Interviewer')` ↔ `describe_interviewer()` |

### Example: Isomorphic Test Structure

```typescript
// TypeScript
describe('Interview', () => {
  describe('field discovery', () => {
    it('uses field name when no description', () => {
      // Test implementation
    })
  })
})
```

```python
# Python
def describe_interview():
    def describe_field_discovery():
        def it_uses_field_name_when_no_description():
            """Uses field name as description when none provided."""
            # Test implementation
```

## Project Structure

```
TypeScript/tests/
├── interview.test.ts                # Core Interview class tests
├── interviewer.test.ts              # Interviewer orchestration tests  
├── interviewer_conversation.test.ts # Conversation flow and state tests
├── builder.test.ts                  # Builder API and method chaining tests
├── custom_transformations.test.ts   # Transformation system tests
├── conversations.test.ts            # Full conversation integration tests
├── integration/
│   └── react.ts                     # React hooks integration tests
└── CLAUDE.md                        # This documentation file
```

## Key Files

### interview.test.ts
- **Purpose**: Tests the core Interview class functionality (mirrors test_interview.py)
- **Coverage**: Field access, state management, completion detection
- **Structure**: `describe('Interview')` with nested describe blocks
- **Test Examples**:
  - `describe('field discovery')` → `it('uses field name when no description')`
  - `describe('field access')` → `it('returns none for uncollected fields')`
  - `describe('completion state')` → `it('starts with done as false')`
- **Focus**: Interview instance behavior without LLM interaction

### interviewer.test.ts
- **Purpose**: Tests the Interviewer class orchestration (mirrors test_interviewer.py)
- **Coverage**: Initialization, LLM binding, tool configuration
- **Structure**: Nested describe blocks matching Python's structure
- **Test Examples**:
  - `describe('initialization')` → `it('creates interviewer with default model')`
  - `describe('tool generation')` → `it('generates tools for all fields')`
- **Mock Strategy**: Uses `MockLLMBackend` for deterministic testing

### interviewer_conversation.test.ts
- **Purpose**: Tests multi-turn conversation dynamics (mirrors test_interviewer_conversation.py)
- **Coverage**: Message handling, state management, field progression
- **Structure**: Matches Python's BDD-style organization
- **Test Examples**:
  - `describe('conversation flow')` → `it('handles multi turn conversations')`
  - `describe('field progression')` → `it('collects fields in order')`
- **Focus**: Conversation state machine and transitions

### builder.test.ts
- **Purpose**: Tests the fluent builder API (mirrors test_builder.py)
- **Coverage**: Method chaining, field configuration, validation rules
- **Structure**: `describe('Builder')` with feature-specific describe blocks
- **Test Examples**:
  - `describe('chaining')` → `it('supports method chaining')`
  - `describe('field configuration')` → `it('applies must rules')`
  - `describe('transformations')` → `it('adds type transformations')`
- **Validation**: Ensures builder creates correct Interview instances

### field_proxy.test.ts
- **Purpose**: Tests the FieldProxy implementation (mirrors test_field_proxy.py)
- **Coverage**: String-like behavior, transformation access
- **Structure**: `describe('FieldProxy')` with behavior-specific tests
- **Test Examples**:
  - `describe('string behavior')` → `it('acts as normal string')`
  - `describe('transformations')` → `it('provides transformation access')`
  - `describe('attribute access')` → `it('returns transformation values')`
- **Focus**: Dynamic property access and string subclass behavior

### custom_transformations.test.ts
- **Purpose**: Tests transformation system (mirrors test_custom_transformations.py)
- **Coverage**: Type transformations, language transformations, cardinality
- **Structure**: `describe('Transformations')` with type-specific blocks
- **Test Examples**:
  - `describe('numeric transformations')` → `it('transforms to int')`
  - `describe('language transformations')` → `it('translates to french')`
  - `describe('cardinality')` → `it('chooses one option')`
- **Focus**: Transformation registration and application

### conversations.test.ts
- **Purpose**: Integration tests with complete conversation flows (mirrors test_conversations.py)
- **Coverage**: End-to-end scenarios, complex validations
- **Structure**: `describe('Conversations')` with scenario-based tests
- **Test Examples**:
  - `describe('full conversations')` → `it('completes job interview')`
  - `describe('edge cases')` → `it('handles invalid responses')`
  - `describe('validation')` → `it('enforces must rules')`
- **Note**: May include tests with real API calls (properly marked)

### integration/react.ts
- **Purpose**: Tests React hooks and components (TypeScript-specific)
- **Coverage**: `useConversation` hook, state management, UI updates
- **Structure**: Standard React testing patterns with describe/it
- **Test Examples**:
  - `describe('useConversation')` → `it('manages conversation state')`
- **Requirements**: React Testing Library, DOM environment
- **Focus**: React integration and component behavior

## Development Commands

### Running Tests

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

### Jest Configuration

The test suite uses Jest with the following configuration:

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

## Architecture Notes

### Isomorphic Test Mapping to Python

Each TypeScript test file is isomorphic to a Python test file with matching test descriptions and counts:

| TypeScript File | Python File | Isomorphic Structure |
|----------------|-------------|---------------------|
| interview.test.ts | test_interview.py | Identical describe/it ↔ describe_/it_ structure |
| interviewer.test.ts | test_interviewer.py | Same test names and organization |
| builder.test.ts | test_builder.py | Matching feature coverage and test counts |
| field_proxy.test.ts | test_field_proxy.py | Same behavior tests |
| custom_transformations.test.ts | test_custom_transformations.py | Identical transformation tests |
| conversations.test.ts | test_conversations.py | Same scenario tests |

### Test Organization

1. **Unit Tests**: Test individual components
   - Mock all external dependencies
   - Fast execution (< 100ms per test)
   - Focus on single responsibility

2. **Integration Tests**: Test component interactions
   - May use real Interview/Interviewer instances
   - Mock only external services (LLM APIs)
   - Medium execution time

3. **End-to-End Tests**: Complete workflow tests
   - Full conversation flows
   - May use real API (marked appropriately)
   - Slower execution

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
    // Support bind method for LangChain compatibility
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

// Mock responses for testing
const mockResponses = {
  name: 'John Doe',
  email: 'john@example.com'
}
```

### Test Patterns

```typescript
// Harmonized test structure matching Python's pytest-describe
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
|--------|------------|---------||
| `describe_interview` | `describe('Interview')` | Top-level component |
| `describe_field_discovery` | `describe('field discovery')` | Feature area |
| `it_uses_field_name_when_no_description` | `it('uses field name when no description')` | Specific test |

## Testing Approach

### Test Coverage Requirements

- Line coverage: > 80%
- Branch coverage: > 75%
- Function coverage: > 80%
- Statement coverage: > 80%

### Test Categories

1. **Smoke Tests**: Basic functionality
   ```typescript
   test('should create interview instance', () => {
     const interview = chatfield().build()
     expect(interview).toBeDefined()
   })
   ```

2. **Validation Tests**: Field validation logic
   ```typescript
   test('should validate required fields', () => {
     const interview = chatfield()
       .field('name').must('not be empty')
       .build()
     // Test validation
   })
   ```

3. **State Tests**: State management
   ```typescript
   test('should track completion state', () => {
     expect(interview._done).toBe(false)
     // Set fields
     expect(interview._done).toBe(true)
   })
   ```

### Async Testing

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

## Important Patterns

### Test Fixtures

```typescript
// Common test data
const createTestInterview = () => {
  return chatfield()
    .type('TestInterview')
    .field('name').desc('Your name')
    .field('email').desc('Your email')
    .build()
}

// Mock data
const TEST_RESPONSES = {
  name: 'Test User',
  email: 'test@example.com'
}
```

### Snapshot Testing

```typescript
test('should match snapshot', () => {
  const interview = createTestInterview()
  expect(interview._chatfield).toMatchSnapshot()
})
```

### Testing React Hooks

```typescript
import { renderHook, act } from '@testing-library/react-hooks'

test('useConversation hook', () => {
  const { result } = renderHook(() => 
    useConversation(interview)
  )
  
  act(() => {
    result.current[1].sendMessage('Hello')
  })
  
  expect(result.current[0].messages).toHaveLength(1)
})
```

## Known Considerations

1. **Isomorphic Tests**: Test names, descriptions, and counts must match Python exactly
2. **Zero Skipped Tests**: NEVER skip tests—use no-op tests that pass to maintain identical test counts
3. **Naming Convention**: Use `it()` instead of `test()` to match Python's `it_*` pattern
4. **Test Isolation**: Each test must be independent
5. **Mock Cleanup**: Jest automatically clears mocks between tests
6. **TypeScript Types**: Ensure proper typing for mocks
7. **Async Handling**: Use async/await properly in tests (Python tests are primarily sync)
8. **Timer Mocks**: Use `jest.useFakeTimers()` for time-dependent tests
9. **Module Mocks**: Place in `__mocks__` directory or use `jest.mock()`
10. **Coverage Gaps**: Focus on critical paths first
11. **Flaky Tests**: Use deterministic mocks instead of real APIs
12. **Isomorphic Comments**: Use "Isomorphic:" comments to document language-specific test differences

## Adding New Tests

When creating new tests, follow the isomorphic testing approach:

1. **Check Python first**: Look for the corresponding Python test in `../../Python/tests/`
2. **Match structure exactly**: Place test in the same file structure as Python
3. **Identical descriptions**: Use test descriptions that match Python exactly
4. **Follow naming convention**: Use `*.test.ts` for files (mirrors Python's `test_*.py`)
5. **BDD structure**: Use `describe()` and `it()` to mirror Python's `describe_*` and `it_*`
6. **Isomorphic comments**: If test behavior differs, add "Isomorphic:" comments in both files
7. **No skipping**: Use no-op tests that pass instead of `it.skip()` or `test.skip()`
8. **Place appropriately**: Place in appropriate file based on component
9. **Group tests**: Group related tests in nested `describe` blocks
10. **Setup/teardown**: Add setup/teardown in `beforeEach`/`afterEach`
11. **Mock dependencies**: Mock external dependencies
12. **Test comprehensively**: Test both success and failure cases
13. **Add comments**: Add comments for complex test logic
14. **Update documentation**: Update this CLAUDE.md file if adding new test files
15. **Verify counts**: Ensure test counts remain identical between TypeScript and Python

### Example of Harmonized Test:
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

## Common Issues and Solutions

- **Module not found**: Ensure correct import paths and build
- **Type errors**: Check TypeScript configuration and types
- **Async timeout**: Increase timeout with `jest.setTimeout(10000)`
- **Mock not working**: Verify mock is before import
- **Coverage gaps**: Add tests for uncovered branches
- **Snapshot failures**: Update with `npm test -- -u`

## CI/CD Integration

```yaml
# GitHub Actions example
- name: Run tests
  run: |
    npm install
    npm run build
    npm test -- --coverage --ci
```

## Performance Testing

For performance-sensitive code:

```typescript
test('should complete within time limit', () => {
  const start = performance.now()
  // Operation to test
  const end = performance.now()
  expect(end - start).toBeLessThan(100) // ms
})
```

## Debugging Tests

```bash
# Debug with VS Code
# Add breakpoint and use "Debug Jest Tests" launch config

# Debug with Chrome DevTools
node --inspect-brk node_modules/.bin/jest --runInBand

# Debug specific test
npm test -- --runInBand interview.test.ts
```