# TypeScript Implementation - CLAUDE.md

This file provides guidance for working with the TypeScript/JavaScript implementation of Chatfield.

## Overview

Chatfield TypeScript (v0.1.0) is the TypeScript/JavaScript implementation of conversational data collection powered by LLMs. Package name: `@chatfield/core`. This implementation maintains feature parity with the Python version (v0.2.0).

**IMPORTANT**: This is the TypeScript implementation of an **isomorphic library**. The Python and TypeScript implementations are equal first-class citizens, maintaining near-identical code structure, naming, logic, and test suites.

**See**: [../Documentation/Isomorphic_Development.md](../Documentation/Isomorphic_Development.md) for isomorphic development principles.

## Quick Start

```bash
cd TypeScript
npm install
npm run build
npm test  # Run tests
```

**See**: [../Documentation/Getting_Started_TypeScript.md](../Documentation/Getting_Started_TypeScript.md) for detailed setup.

## Development Commands

```bash
# Build & Development
npm run build           # Compile TypeScript to dist/
npm run dev             # Watch mode compilation
npm run clean           # Remove dist/ directory

# Testing
npm test                # Run all tests
npm run test:watch      # Watch mode testing
npm test -- interview.test.ts  # Run specific file

# Code Quality
npm run lint            # ESLint checks

# Examples
npx tsx examples/basic-usage.ts
```

**See**: [../Documentation/Commands.md](../Documentation/Commands.md) for complete command reference.

## Project Structure

```
TypeScript/
├── chatfield/               # TypeScript source code
│   ├── index.ts             # Main exports and public API
│   ├── interview.ts         # Base Interview class (mirrors Python)
│   ├── interviewer.ts       # LangGraph orchestration
│   ├── field-proxy.ts       # FieldProxy for transformations
│   ├── builder.ts           # Primary fluent builder API
│   ├── builder-types.ts     # TypeScript type definitions
│   ├── types.ts             # Core type definitions
│   └── integrations/        # Framework integrations
│       ├── react.ts         # React hooks
│       ├── react-components.tsx # UI components
│       └── copilotkit.tsx   # CopilotKit integration
├── tests/                   # Jest test suite
└── examples/                # Usage examples
```

**See**: [../Documentation/Project_Structure.md](../Documentation/Project_Structure.md) for complete structure.

## Core Architecture

### Key Components

1. **Interview** (`interview.ts`): Base class with field definitions and _chatfield structure (mirrors Python)
2. **Interviewer** (`interviewer.ts`): LangGraph-based conversation orchestration
3. **Builder** (`builder.ts`): Primary fluent builder API with full TypeScript type inference
4. **FieldProxy** (`field-proxy.ts`): String-like class for field values with transformation access

### Data Flow

1. **Definition Phase**: Builder creates Interview with metadata
2. **Conversation Phase**: LangGraph orchestrates state machine (initialize → think → listen → tools → teardown)
3. **Collection Phase**: LLM validates and transforms responses
4. **Access Phase**: FieldProxy provides values with transformations

**See**: [../Documentation/Architecture.md](../Documentation/Architecture.md) for detailed architecture.

## Builder API

```typescript
import { chatfield } from '@chatfield/core'

const interview = chatfield()
  .type('Contact Form')
  .field('age')
    .desc('Your age')
    .must('be specific')
    .as_int()
  .build()

// After collection
interview.age        // number (transformed)
```

**See**: [../Documentation/Builder_Api.md](../Documentation/Builder_Api.md) for complete API reference.

## API Configuration

```typescript
import { Interviewer, chatfield } from '@chatfield/core'

const interview = chatfield().field('name').build()

// Option 1: Use environment variable (default)
const interviewer = new Interviewer(interview)

// Option 2: Explicit API key
const interviewer = new Interviewer(interview, {
  apiKey: 'your-api-key'
})

// Option 3: Custom base URL (e.g., LiteLLM proxy)
const interviewer = new Interviewer(interview, {
  apiKey: 'your-api-key',
  baseUrl: 'https://my-litellm-proxy.com/v1'
})
```

**See**: [../Documentation/Api_Configuration.md](../Documentation/Api_Configuration.md) for detailed configuration options and security modes.

## Testing

Tests use Jest with structure mirroring Python's pytest tests:

```bash
npm test                     # Run all tests
npm run test:watch          # Watch mode
npm test -- --coverage      # Coverage report
npm test interview.test.ts  # Specific file
```

**Critical**: TypeScript tests maintain **isomorphic structure** with Python—identical test counts, descriptions, and organization.

**See**:
- [tests/CLAUDE.md](tests/CLAUDE.md) for TypeScript test suite details
- [../Documentation/TESTING_Architecture.md](../Documentation/TESTING_Architecture.md) for testing philosophy

## Isomorphic Development in TypeScript

### Key Principles

1. **Check Python First**: Before implementing features, check `../Python/` for the corresponding implementation
2. **Match Structure**: File names, class names, method names should match Python (accounting for language conventions)
3. **Use "Isomorphic:" Comments**: When TypeScript code must differ from Python, include identical "Isomorphic:" comments in both files
4. **Identical Tests**: Test descriptions, counts, and structure must match Python's pytest tests
5. **Zero Skipped Tests**: Use no-op tests that pass instead of `it.skip()` or `test.skip()`

### TypeScript-Specific Conventions

- **Naming**: Use `camelCase` for methods (vs Python's `snake_case`)
- **Async**: TypeScript implementation is async by default (Python is primarily synchronous)
- **Types**: Full TypeScript type inference and checking throughout
- **Imports**: Use absolute imports from `chatfield/` directory
- **Testing**: Use Jest describe/it to mirror Python's pytest-describe structure

### Example: Isomorphic Comment Pattern

```typescript
// Isomorphic: Python uses snake_case for method names, TypeScript uses camelCase.
// Both implementations have identical logic and behavior.
getFieldValue(fieldName: string): string | null {
  return this._chatfield.fields[fieldName]?.value ?? null
}
```

**See**: [../Documentation/Isomorphic_Development.md](../Documentation/Isomorphic_Development.md) for complete details.

## Key Dependencies

- **@langchain/core** (0.3.72+): Core LangChain abstractions
- **@langchain/langgraph** (0.4.6+): State machine orchestration
- **@langchain/openai** (0.6.9+): OpenAI LLM integration
- **openai** (4.70.0+): Direct OpenAI API client
- **zod** (3.25.76+): Runtime type validation for tools
- **uuid** (11.1.0+): Unique ID generation

## Key Differences from Python

1. **Async by default**: All operations use async/await
2. **Type safety**: Full TypeScript type inference and checking
3. **Builder primary**: Builder pattern is primary API
4. **React focus**: Built-in React hooks and components
5. **Field definition**: Fields defined via builder pattern
6. **Zod validation**: Uses Zod for runtime type validation in tools
7. **Import style**: Absolute imports from `chatfield/` directory

## Environment

- **Node Version**: 20.0.0+ recommended
- **TypeScript**: 5.0.0+ with strict mode
- **Module Resolution**: CommonJS for compatibility
- **Build Target**: ES2020
- **Compilation**: TypeScript compiles to `dist/` directory

## Key Considerations

1. **Isomorphic Implementation**: This TypeScript code mirrors Python—check both implementations when making changes
2. **Test Isomorphism**: Test names, counts, and descriptions must match Python implementation exactly
3. **Naming Conventions**: Use camelCase (TypeScript) vs snake_case (Python), documented with "Isomorphic:" comments
4. **Async Patterns**: All LLM operations are async (Python is primarily sync)
5. **Type Inference**: Leverage TypeScript's type system fully
6. **React Integration**: Primary UI integration path

## Mock LLM for Testing

```typescript
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

**See**: [tests/CLAUDE.md](tests/CLAUDE.md) for testing patterns.

## Build Configuration

- TypeScript compiles to `dist/` directory
- Target: ES2020, CommonJS modules
- Strict mode enabled with all checks
- Decorator support enabled
- Source maps generated for debugging

## Advanced Topics

For detailed technical documentation on TypeScript-specific implementation details:

- **JS Conversion Plan**: [CLAUDE/JS_CONVERSION_PLAN.md](CLAUDE/JS_CONVERSION_PLAN.md) - Comprehensive plan for reimplementing TypeScript to match Python's chatfield architecture
- **Proxy Setup**: [CLAUDE/PROXY_SETUP.md](CLAUDE/PROXY_SETUP.md) - LiteLLM proxy configuration for secure browser-based development
- **Build Options**: [CLAUDE/ROLLUP_BUILD_OPTIONS.md](CLAUDE/ROLLUP_BUILD_OPTIONS.md) - Rollup build configuration and environment variable reference

## Additional Resources

- **Main Documentation**: [../CLAUDE.md](../CLAUDE.md) for project overview
- **Architecture**: [../Documentation/Architecture.md](../Documentation/Architecture.md)
- **Cookbook**: [../Documentation/Cookbook.md](../Documentation/Cookbook.md) for common patterns
- **Design Decisions**: [../Documentation/Design_Decisions.md](../Documentation/Design_Decisions.md)
