# CLAUDE.md

This file provides guidance to Claude Code when working with the TypeScript/JavaScript test suite in this directory.

## Overview

This directory contains the comprehensive test suite for the Chatfield TypeScript/JavaScript library, mirroring the Python implementation's test structure for feature parity. Tests cover the builder API, Interview class, Interviewer orchestration, transformations, and conversation flows using Jest as the testing framework. The test structure uses nested describe/it blocks that correspond exactly to Python's pytest-describe organization.

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
  - `describe('useGatherer')` → `it('provides gatherer interface')`
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
    "src/**/*.ts",
    "!src/**/*.d.ts"
  ]
}
```

## Architecture Notes

### Test Harmonization with Python

Each TypeScript test file corresponds to a Python test file with matching test descriptions:

| TypeScript File | Python File | Description Pattern |
|----------------|-------------|--------------------|
| interview.test.ts | test_interview.py | Identical describe/it structure |
| interviewer.test.ts | test_interviewer.py | Same test names and organization |
| builder.test.ts | test_builder.py | Matching feature coverage |
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
  const result = await interviewer.run()
  expect(result).toBeDefined()
})

// With error handling
test('should handle errors', async () => {
  await expect(interviewer.run()).rejects.toThrow('Expected error')
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
    useConversation(gatherer)
  )
  
  act(() => {
    result.current[1].sendMessage('Hello')
  })
  
  expect(result.current[0].messages).toHaveLength(1)
})
```

## Known Considerations

1. **Test Harmonization**: Test descriptions must match Python exactly
2. **Naming Convention**: Use `it()` instead of `test()` to match Python's `it_*` pattern
3. **Test Isolation**: Each test must be independent
4. **Mock Cleanup**: Jest automatically clears mocks between tests
5. **TypeScript Types**: Ensure proper typing for mocks
6. **Async Handling**: Use async/await properly in tests
7. **Timer Mocks**: Use `jest.useFakeTimers()` for time-dependent tests
8. **Module Mocks**: Place in `__mocks__` directory or use `jest.mock()`
9. **Coverage Gaps**: Focus on critical paths first
10. **Flaky Tests**: Use deterministic mocks instead of real APIs

## Adding New Tests

When creating new tests:

1. **Check Python equivalent**: Look for corresponding Python test first
2. **Match test description**: Use exact same test description as Python
3. Follow naming convention (`*.test.ts` for files)
4. Use `describe()` and `it()` to match Python's structure
5. Place in appropriate file based on component
6. Group related tests in nested `describe` blocks
7. Add setup/teardown in `beforeEach`/`afterEach`
8. Mock external dependencies
9. Test both success and failure cases
10. Add comments for complex test logic
11. Update this CLAUDE.md file if adding new test files

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