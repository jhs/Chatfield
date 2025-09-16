# Chatfield TypeScript/JavaScript

TypeScript/JavaScript implementation of conversational data collection.

## Development Setup

```bash
# Install dependencies
npm install

# Build the project
npm run build

# Watch mode for development
npm run dev
```

## Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run specific test file
npm test -- interview.test.ts

# Run tests matching pattern
npm test -- --testNamePattern="field validation"

# Run with coverage
npm test -- --coverage
# Coverage report will be in coverage/lcov-report/index.html
```

## Build Commands

```bash
# Build TypeScript to JavaScript
npm run build

# Watch mode (rebuilds on changes)
npm run dev

# Clean build directory
npm run clean

# Run minimal test script
npm run min
```

## Code Quality

```bash
# Run ESLint
npm run lint

# Fix ESLint issues automatically
npm run lint -- --fix

# Type check without building
npx tsc --noEmit
```

## Running Examples

```bash
# Using tsx (TypeScript execute)
npx tsx examples/basic-usage.ts
npx tsx examples/job-interview.ts

# Using compiled JavaScript
node dist/examples/basic-usage.js
node dist/examples/job-interview.js
```

## Project Structure

```
TypeScript/
├── src/                    # TypeScript source
│   ├── index.ts           # Main exports
│   ├── interview.ts       # Interview class
│   ├── interviewer.ts     # Conversation orchestration
│   ├── builder.ts         # Builder API
│   ├── builder-types.ts   # Type definitions
│   ├── field-proxy.ts     # FieldProxy implementation
│   ├── types.ts           # Core types
│   └── integrations/      # Framework integrations
├── tests/                  # Test suite
│   ├── *.test.ts          # Test files
│   └── integration/       # Integration tests
├── examples/              # Example scripts
├── dist/                  # Compiled JavaScript (generated)
├── package.json           # Package configuration
├── tsconfig.json          # TypeScript configuration
├── jest.config.js         # Jest test configuration
└── minimal.ts             # Minimal test script
```

## Package Scripts

Available npm scripts in package.json:

- `npm run build` - Compile TypeScript to JavaScript
- `npm run dev` - Watch mode compilation
- `npm run clean` - Remove dist directory
- `npm test` - Run Jest tests
- `npm run test:watch` - Run tests in watch mode
- `npm run lint` - Run ESLint
- `npm run min` - Run minimal test script

## Environment Variables

Set in `.env` file or export:

```bash
OPENAI_API_KEY=your-api-key
LANGCHAIN_TRACING_V2=true  # Optional: Enable LangSmith tracing
```

## Node Version

Requires Node.js 20.0.0 or higher.

## TypeScript Configuration

The project uses strict TypeScript settings:
- Target: ES2020
- Module: CommonJS
- Strict mode enabled
- All strict checks enabled
- Source maps generated

## Dependencies

Core dependencies are managed in `package.json`. Key packages:
- @langchain/core (0.3.72+)
- @langchain/langgraph (1.0.0a3+)
- @langchain/openai (0.6.9+)
- openai (4.70.0+)
- zod (3.25.76+)

Development dependencies include:
- typescript
- jest
- ts-jest
- @types/node
- eslint