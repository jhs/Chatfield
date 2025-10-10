# CLAUDE.md

This file provides guidance to Claude Code when working with the TypeScript/JavaScript implementation of Chatfield.

## CRITICAL: Synchronization Requirements

**The TypeScript implementation MUST stay synchronized with the Python implementation.** This means:
- **Filenames**: Match Python's naming (e.g., `interview.py` → `interview.ts`)
- **Test Files**: Python uses `test_*.py`, TypeScript uses `*.test.ts` (e.g., `test_builder.py` → `builder.test.ts`)
- **Class/Function Names**: Keep identical names (e.g., `Interview`, `Interviewer`, `FieldProxy`)
- **Method Names**: Preserve Python method names (e.g., `_name()`, `_pretty()`, `as_int`)
- **Code Logic**: Implement the same algorithms and flows as Python
- **Test Structure**: Mirror Python test files and test names exactly
- **Test Descriptions**: Use identical test descriptions for corresponding tests
- **Only deviate when necessary** for language-specific requirements (e.g., TypeScript types, async/await patterns)

## Overview

Chatfield JS/TS is the TypeScript/JavaScript implementation (v0.1.0) of conversational data collection powered by LLMs. Package name: `@chatfield/core`. This implementation maintains feature parity with the Python version (v0.2.0).

## Project Structure

```
TypeScript/
├── chatfield/                   # TypeScript source code
│   ├── index.ts                 # Main exports and public API
│   ├── interview.ts             # Base Interview class (mirrors Python)
│   ├── interviewer.ts           # LangGraph-based conversation orchestration
│   ├── builder.ts               # Builder pattern API (primary interface)
│   ├── builder-types.ts         # TypeScript type definitions for builder
│   ├── field-proxy.ts           # FieldProxy string subclass for transformations
│   ├── types.ts                 # Core type definitions
│   └── integrations/            # Framework integrations
│       ├── react.ts             # React hooks (useConversation)
│       ├── react-components.tsx # UI components
│       └── copilotkit.tsx       # CopilotKit integration
├── tests/                       # Test suite (*.test.ts naming, mirrors Python)
│   ├── interview.test.ts        # Interview class tests
│   ├── interviewer.test.ts      # Interviewer orchestration tests
│   ├── interviewer_conversation.test.ts # Conversation flow tests
│   ├── builder.test.ts          # Builder API tests
│   ├── field_proxy.test.ts      # FieldProxy tests
│   ├── custom_transformations.test.ts # Transformation tests
│   ├── conversations.test.ts    # End-to-end conversation tests
│   ├── integration/             # Integration test scenarios
│   │   └── react.ts            # React hooks integration tests
│   └── CLAUDE.md                # Test suite documentation
├── examples/                    # Usage examples
│   ├── basic-usage.ts           # Simple builder pattern example
│   ├── job-interview.ts         # Job application (mirrors Python)
│   ├── restaurant-order.ts      # Restaurant ordering
│   ├── schema-based.ts          # Schema-driven approach
│   └── type-safe-demo.ts        # TypeScript type inference demo
├── dist/                        # Compiled output (generated)
├── package.json                 # Node package configuration
├── tsconfig.json                # TypeScript compiler configuration
├── jest.config.js               # Jest testing configuration
└── minimal.ts                   # Minimal test script for OpenAI API
```

## Development Commands

```bash
# Setup
npm install              # Install dependencies
npm run build           # Initial build

# Build & Development
npm run build           # Compile TypeScript to dist/
npm run dev             # Watch mode compilation
npm run clean           # Remove dist/ directory

# Testing
npm test                                    # Run all tests
npm run test:watch                          # Watch mode testing
npm test -- interview.test.ts               # Run specific test file
npm test -- --testNamePattern="field validation"  # Run tests matching pattern
npm test -- --coverage                      # Run with coverage report

# Code Quality  
npm run lint            # ESLint checks

# Running Examples
npm run min                                 # Test OpenAI connection with minimal.ts
npx tsx examples/basic-usage.ts             # Run basic example
npx tsx examples/job-interview.ts           # Run job interview example
node dist/examples/basic-usage.js           # Run compiled example
```

## Architecture Overview

### Core Components

1. **Interview Class** (`chatfield/interview.ts`)
   - Mirrors Python's Interview base class exactly
   - Manages field definitions in `_chatfield` structure
   - Provides field access through getters
   - Tracks completion state with `_done` property
   - Supports serialization for LangGraph state

2. **Interviewer Class** (`chatfield/interviewer.ts`)
   - LangGraph-based conversation orchestration
   - Uses @langchain/langgraph for state management
   - Generates Zod-based tools for field collection
   - Handles validation and transformations
   - Maintains thread isolation with unique IDs
   - Accepts optional `llm` parameter for testing (mirrors Python)

3. **Builder API** (`chatfield/builder.ts`)
   - Primary interface for defining interviews
   - Fluent method chaining pattern
   - Full TypeScript type inference
   - Generates Interview instances with metadata

4. **FieldProxy** (`chatfield/field-proxy.ts`)
   - String-like class for field values
   - Provides transformation access (`.as_int`, `.as_lang_fr`, etc.)
   - Mirrors Python's FieldProxy behavior


### Key Dependencies

- **@langchain/core** (0.3.72+): Core LangChain abstractions
- **@langchain/langgraph** (0.4.6+): State machine orchestration
- **@langchain/openai** (0.6.9+): OpenAI LLM integration
- **openai** (4.70.0+): Direct OpenAI API client
- **zod** (3.25.76+): Runtime type validation for tools
- **uuid** (11.1.0+): Unique ID generation

## Testing Approach

### Test Harmonization
Tests are structured to match Python's pytest-describe organization:

```typescript
describe('Interview', () => {
  describe('field discovery', () => {
    it('uses field name when no description', () => {
      // Test matches Python's: it_uses_field_name_when_no_description
    })
  })
})
```

### Test Structure
- Each `.test.ts` file corresponds to a Python `test_*.py` file
- Test descriptions match Python exactly for feature parity
- Mock LLM backends for deterministic testing
- Integration tests in `tests/integration/`

### Running Tests
```bash
npm test                     # Run all tests
npm run test:watch          # Watch mode
npm test -- --coverage      # Coverage report
npm test interview.test.ts  # Specific file
```

## Important Patterns

### Builder Pattern Usage
```typescript
const interview = chatfield()
  .type('JobApplication')
  .field('position')
    .desc('Desired position')
    .must('include company name')
    .as_string()
  .field('experience')
    .desc('Years of experience')
    .as_int()
    .must('be realistic')
  .build()
```

### Field Access
```typescript
// After collection
interview.position       // string value
interview.experience     // number (transformed)

// With FieldProxy
const field = interview.getField('position')
field.asQuote           // Original quote
field.asContext         // Conversational context
```

### Mock LLM for Testing
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
```

## Key Differences from Python

1. **Async by default**: All operations use async/await
2. **Type safety**: Full TypeScript type inference and checking
3. **Builder primary**: Builder pattern is primary API
4. **React focus**: Built-in React hooks and components
5. **Field definition**: Fields defined via builder pattern
6. **Zod validation**: Uses Zod for runtime type validation in tools
7. **Import style**: Absolute imports from `chatfield/` directory

## API Key Configuration

Requires OpenAI API key:
```bash
export OPENAI_API_KEY=your-api-key
```
Or use `.env` file in project directory.

### API Initialization Options

The `Interviewer` constructor supports flexible API configuration for different deployment scenarios:

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

// Option 4: Both custom base URL and API key
const interviewer = new Interviewer(interview, {
  baseUrl: 'https://my-proxy.com/openai',
  apiKey: 'proxy-api-key'
})
```

**Constructor Options:**
- `threadId` (string, optional): Custom thread ID for conversation tracking
- `llm` (any, optional): Custom LLM instance (overrides all other LLM config)
- `llmId` (string, optional): LLM model identifier (default: 'openai:gpt-4o')
- `temperature` (number, optional): Temperature for LLM generation (default: 0.0)
- `baseUrl` (string, optional): Custom API endpoint (e.g., for LiteLLM proxies)
- `apiKey` (string, optional): API key (falls back to OPENAI_API_KEY env var)
- `endpointSecurity` (EndpointSecurityMode, optional): Security mode for endpoint validation ('strict', 'warn', or 'disabled')

**Use Cases:**
- **Production**: Use `baseUrl` to point to a LiteLLM proxy that handles authentication
- **Development**: Use environment variables for simplicity
- **Testing**: Pass explicit `apiKey` and `baseUrl` for test environments
- **Multi-tenant**: Different API keys per Interviewer instance

### Endpoint Security Modes

The `endpointSecurity` parameter controls how the Interviewer validates API endpoints to prevent accidental exposure of API keys:

```typescript
import { Interviewer, chatfield } from '@chatfield/core'

const interview = chatfield().field('name').build()

// Option 1: Strict mode (default for browser environment)
// Blocks official endpoints, requires proxy
const interviewer = new Interviewer(interview, {
  apiKey: 'your-api-key',
  baseUrl: 'https://my-proxy.com/v1',
  endpointSecurity: 'strict'  // Throws error for api.openai.com, api.anthropic.com
})

// Option 2: Warn mode
// Warns about official endpoints but allows them
const interviewer = new Interviewer(interview, {
  apiKey: 'your-api-key',
  baseUrl: 'https://api.openai.com/v1',
  endpointSecurity: 'warn'  // Logs warning but continues
})

// Option 3: Disabled mode (default for Node.js/server environment)
// Allows official endpoints like api.openai.com
const interviewer = new Interviewer(interview, {
  apiKey: 'your-api-key',
  baseUrl: 'https://api.openai.com/v1',
  endpointSecurity: 'disabled'  // or omit, as this is the default for Node
})
```

**Security Mode Behavior:**
- **`'strict'`** (default for browser): Throws Error when official endpoints are detected (api.openai.com, api.anthropic.com). Forces use of a backend proxy. Automatically enabled in browser environments.
- **`'warn'`**: Logs warnings to console when official endpoints are detected, but allows the connection. Useful for development with awareness of potential issues.
- **`'disabled'`** (default for Node.js): Detection logic runs and logs debug messages, but allows all endpoints including official ones. Use for server-side applications where API keys are protected. **Cannot be used in browser environments** - attempting to disable security in a browser will throw an error.

**Dangerous Endpoints Detected:**
- `api.openai.com`
- `api.anthropic.com`

**Environment-Based Defaults:**
- **Browser**: Defaults to `'strict'` mode. Cannot be set to `'disabled'`.
- **Node.js/Server**: Defaults to `'disabled'` mode.

**Note:** The TypeScript implementation automatically detects browser vs. server environments and applies appropriate defaults. Python runs server-side only and defaults to `'disabled'`.

## Known Considerations

1. **Test synchronization**: Test names and descriptions must match Python
2. **LangGraph version**: Uses @langchain/langgraph 0.4.6+ (Python uses 0.6.4+)
3. **Import paths**: Use absolute imports from `chatfield/`
4. **Async patterns**: All LLM operations are async
5. **Type inference**: Leverage TypeScript's type system fully
6. **React integration**: Primary UI integration path
7. **Tool generation**: Uses Zod schemas instead of Pydantic
8. **State merging**: Custom merge logic for Interview instances
9. **LangSmith debugging**: Trace URLs generated for debugging

## Synchronization with Python

When implementing new features:
1. **ALWAYS check the Python implementation first** in `Python/`
2. Match file names, class names, and method names exactly
3. Use identical test descriptions for corresponding tests
4. Implement the same algorithms and validation logic
5. Only deviate for TypeScript-specific requirements (types, async/await)

## Contributing Guidelines

1. **Maintain parity**: Keep synchronized with Python implementation
2. **Test coverage**: Write tests matching Python test descriptions
3. **Type safety**: Ensure full TypeScript type coverage
4. **Documentation**: Update CLAUDE.md when adding features
5. **Examples**: Provide TypeScript examples for new features
6. **Code style**: Follow ESLint configuration
7. **Version sync**: Update version in package.json with pyproject.toml

## Build Configuration

- TypeScript compiles to `dist/` directory
- Target: ES2020, CommonJS modules
- Strict mode enabled with all checks
- Decorator support enabled
- Source maps generated for debugging