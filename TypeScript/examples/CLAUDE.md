# TypeScript Examples - CLAUDE.md

This file provides guidance for working with the TypeScript/JavaScript examples.

## Overview

This directory contains demonstration examples showcasing Chatfield TypeScript features, builder API, and various use cases. Each example demonstrates specific capabilities in a TypeScript/Node.js environment.

## Examples

```
examples/
├── basic-usage.ts                # Simple examples with builder API
├── schema-based.ts               # Zod schema integration
├── type-safe-demo.ts             # TypeScript type safety features
├── job-interview.ts              # Professional HR use case
├── restaurant-order.ts           # Interactive ordering system
├── polish-passport-wizard.ts     # Government service wizard
└── CLAUDE.md                     # This file
```

### Key Examples

- **basic-usage.ts**: Introduction to builder API with simple contact form and business plan examples. Demonstrates `.must()`, `.reject()`, `.hint()` methods.
- **schema-based.ts**: Zod schema integration showing type-safe validation, schema inference, and runtime validation combined with conversational collection.
- **type-safe-demo.ts**: TypeScript type safety features including generic types, type inference, compile-time checking, and type-safe field access.
- **job-interview.ts**: Professional recruitment scenario with complex validation, multi-field dependencies, and professional tone configuration.
- **restaurant-order.ts**: E-commerce ordering system with dynamic menus, contextual validation, and stateful conversations.
- **polish-passport-wizard.ts**: Government service wizard for Polish child passport applications with multi-step conditional logic, choice constraints, and educational hints for non-native speakers.

## Running Examples

```bash
cd TypeScript

# Using tsx (direct execution)
npx tsx examples/basic-usage.ts
npx tsx examples/schema-based.ts
npx tsx examples/job-interview.ts

# With environment variables
OPENAI_API_KEY=sk-... npx tsx examples/basic-usage.ts

# After compilation
npm run build
node dist/examples/basic-usage.js
```

**See**: [../../Documentation/Commands.md](../../Documentation/Commands.md) for complete command reference.

## Setup

```bash
cd TypeScript
npm install                               # Install dependencies
npm run build                             # Build library
export OPENAI_API_KEY=your-api-key-here   # Set API key
# Or create .env.secret file with: OPENAI_API_KEY=your-api-key
```

## Common Patterns

All examples use similar structure:

```typescript
import { chatfield, Interviewer } from '@chatfield/core'

// Build interview
const interview = chatfield()
  .type('InterviewType')
  .field('fieldName')
    .desc('Field description')
  .must('validation rule')
  .build()

// Run interview
const interviewer = new Interviewer(interview)
const result = await interviewer.go()

// Access collected data
console.log(result.fieldName)
```

## Key Considerations

1. **TypeScript Version**: Requires TypeScript 4.5+ for best experience
2. **Node.js Version**: Requires Node.js 16+ for ES modules support
3. **API Key Management**: Never commit API keys to version control
4. **Async/Await**: All examples use async/await patterns
5. **Type Safety**: Leverage TypeScript's type system fully

## Adding New Examples

When creating new examples:

1. Follow naming convention (kebab-case.ts)
2. Include comprehensive header comments explaining purpose
3. Import from '../chatfield' for development
4. Handle missing API keys gracefully
5. Provide clear console output showing progress
6. Test with both real and mock backends
7. Add npm script to package.json if frequently used
8. Update this CLAUDE.md file

## Mock Backend for Testing

For testing without API calls:

```typescript
class MockLLMBackend {
  async invoke(messages: any[]) {
    return { content: 'Mock response' }
  }
  bindTools(tools: any[]) {
    return this
  }
}

const interviewer = new Interviewer(interview, { llm: new MockLLMBackend() })
```

## Common Issues

- **Module not found**: Run `npm install` and `npm run build` first
- **API Key Error**: Set OPENAI_API_KEY environment variable
- **TypeScript Errors**: Ensure tsconfig.json has correct settings
- **Runtime Errors**: Check Node.js version (16+ required)
- **Import Errors**: Use correct import paths ('../chatfield' during development)

## Integration Examples

### With Express Server
```typescript
app.post('/interview', async (req, res) => {
  const interviewer = new Interviewer(Form)
  const result = await interviewer.go()
  res.json(result)
})
```

### With React
```typescript
// See chatfield/integrations/react.ts
const [state, actions] = useConversation(Form)
```

## Additional Resources

- **TypeScript Implementation**: [../CLAUDE.md](../CLAUDE.md)
- **Builder API**: [../../Documentation/Builder_Api.md](../../Documentation/Builder_Api.md)
- **API Configuration**: [../../Documentation/Api_Configuration.md](../../Documentation/Api_Configuration.md)
- **Python Examples**: [../../Python/examples/CLAUDE.md](../../Python/examples/CLAUDE.md) for comparison
