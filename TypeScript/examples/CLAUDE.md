# CLAUDE.md

This file provides guidance to Claude Code when working with the TypeScript/JavaScript examples in this directory.

## Overview

This directory contains demonstration examples of the Chatfield TypeScript/JavaScript library, showcasing the builder API and various use cases. Each example demonstrates specific capabilities of the conversational data collection framework in a TypeScript/Node.js environment.

## Project Structure

```
TypeScript/examples/
├── basic-usage.ts       # Simple examples with builder API
├── schema-based.ts      # Zod schema integration example
├── type-safe-demo.ts    # TypeScript type safety features
├── job-interview.ts     # Professional HR use case
├── restaurant-order.ts  # Interactive ordering system
└── CLAUDE.md           # This documentation file
```

## Key Files

### basic-usage.ts
- **Purpose**: Introduction to the builder API
- **Features**: Simple contact form and business plan examples
- **Patterns**: Fluent method chaining, field validation
- **Key Concepts**: `.must()`, `.reject()`, `.hint()` methods


### schema-based.ts
- **Purpose**: Shows Zod schema integration
- **Features**: Type-safe validation, schema inference, runtime validation
- **Integration**: Combines Zod schemas with Chatfield conversations
- **Benefits**: Leverages existing Zod schemas for data collection

### type-safe-demo.ts
- **Purpose**: Showcases TypeScript type safety features
- **Features**: Generic types, type inference, compile-time checking
- **Advanced**: Demonstrates type-safe field access and transformations
- **Developer Experience**: Shows IDE autocomplete and type hints

### job-interview.ts
- **Purpose**: Professional recruitment scenario
- **Features**: Complex validation, multi-field dependencies
- **Patterns**: Professional tone configuration, detailed requirements
- **Use Case**: HR applications and professional data collection

### restaurant-order.ts
- **Purpose**: E-commerce ordering system
- **Features**: Dynamic menus, contextual validation, order flow
- **Patterns**: Stateful conversations, item recommendations
- **Use Case**: Food delivery and e-commerce applications

## Development Commands

### Running Examples

```bash
# Using npm scripts (defined in package.json)
npm run example:basic
npm run example:schema

# Direct execution with tsx
npx tsx examples/basic-usage.ts
npx tsx examples/schema-based.ts
npx tsx examples/type-safe-demo.ts
npx tsx examples/job-interview.ts
npx tsx examples/restaurant-order.ts

# With environment variables
OPENAI_API_KEY=sk-... npx tsx examples/basic-usage.ts

# With Node.js (after compilation)
npm run build
node dist/examples/basic-usage.js
```

### Environment Setup

```bash
# Navigate to TypeScript directory
cd TypeScript

# Install dependencies
npm install

# Build the library
npm run build

# Set up environment variables
export OPENAI_API_KEY=your-api-key-here

# Or use a .env file
echo "OPENAI_API_KEY=your-api-key" > .env
```

## Architecture Notes

### Import Patterns

Examples use different import styles based on use case:

```typescript
// Builder API imports
import { chatfield } from '../chatfield'

// Backend imports
import { OpenAIBackend, MockLLMBackend } from '../chatfield'

```

### API Styles

1. **Builder Pattern** (Recommended):
```typescript
const Form = chatfield()
  .field('name', 'Your name')
  .must('include first and last')
  .build()
```

### Running Conversations

Standard pattern for all examples:

```typescript
const form = chatfield()
  .field('name', 'Your name')
  .build()

// Initialize backend
const backend = new OpenAIBackend({
  apiKey: process.env.OPENAI_API_KEY
})

// Create and run interviewer
const interviewer = new Interviewer(form, { backend })
const result = await interviewer.go()

// Access collected data
console.log(result.name)
```

## Testing Approach

- Examples serve as integration tests for the library
- Each example tests specific API styles or features
- Should be runnable independently
- Include error handling for missing API keys
- Provide clear console output showing results

## Important Patterns

### TypeScript Configuration

Examples require specific TypeScript settings:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "strict": true
  }
}
```

### Error Handling

All examples should handle common errors:

```typescript
if (!process.env.OPENAI_API_KEY) {
  console.error('Please set OPENAI_API_KEY environment variable')
  process.exit(1)
}

try {
  const result = await interviewer.go()
} catch (error) {
  console.error('Interview failed:', error)
}
```

### Mock Backend Usage

For testing without API calls:

```typescript
const backend = new MockLLMBackend({
  responses: {
    name: 'John Doe',
    email: 'john@example.com'
  }
})
```

## Known Considerations

1. **TypeScript Version**: Examples require TypeScript 4.5+ for best experience
2. **Node.js Version**: Requires Node.js 16+ for ES modules support
3. **API Key Management**: Never commit API keys to version control
5. **Bundle Size**: Consider tree-shaking for production builds
6. **React Integration**: See `src/integrations/react.ts` for React examples
7. **Async/Await**: All examples use async/await patterns
8. **Type Safety**: Leverage TypeScript's type system fully

## Adding New Examples

When creating new examples:

1. Follow naming convention (kebab-case.ts)
2. Include comprehensive header comments explaining purpose
3. Import from '../chatfield' for development convenience
4. Handle missing API keys gracefully
5. Provide clear console output showing progress
6. Test with both real and mock backends
7. Add npm script to package.json if frequently used
8. Demonstrate specific features clearly
9. Update this CLAUDE.md file with the new example

## Common Issues and Solutions

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

### With React (see chatfield/integrations/react.ts)
```typescript
const [state, actions] = useConversation(Form)
```

### With CopilotKit
```typescript
// TODO write this
```