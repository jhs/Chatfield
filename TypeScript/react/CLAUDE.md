# TypeScript React Integration - CLAUDE.md

This file provides guidance for working with the Chatfield React integration.

## Overview

`@chatfield/react` provides React hooks and utilities for integrating Chatfield conversational data collection into React applications. The package is designed to be headless (no UI components), focusing on business logic and state management.

**Package Name**: `@chatfield/react`
**Version**: 0.1.0
**Location**: `TypeScript/react/`

## Quick Start

```bash
cd TypeScript/react
npm install
npm run build
```

## Core API

### useChatfield Hook

The primary API for React integration. Provides state management and conversation orchestration for Chatfield interviews.

```typescript
import { useChatfield } from '@chatfield/react'
import { chatfield } from '@chatfield/core/lean'

const interview = chatfield()
  .field('name', 'Your name')
  .build()

function MyComponent() {
  const [state, actions] = useChatfield(interview, {
    onField: (fieldName, fieldProxy) => {
      console.log(`Collected: ${fieldName}`, fieldProxy)
    },
    onError: (error) => {
      console.error('Error:', error)
    }
  })

  if (state.interview._done) {
    return <div>Complete! Name: {state.interview.name}</div>
  }

  return (
    <div>
      {state.messages.map((msg, i) => (
        <div key={i}>{msg.content}</div>
      ))}
      <input
        disabled={!state.isReadyForInput}
        onKeyPress={(e) => {
          if (e.key === 'Enter') {
            actions.send(e.target.value)
            e.target.value = ''
          }
        }}
      />
    </div>
  )
}
```

## Architecture

### State Management

- **messages**: Array of conversation messages `{ role: 'user' | 'assistant', content: string }`
- **isReadyForInput**: Boolean indicating if ready for user input (replaces separate isWaiting/isThinking)
- **interview**: Current interview instance with collected field values

### Actions

- **send(message: string)**: Send user message and get AI response

### Callbacks

- **onField**: Called when non-confidential field is collected
- **onConfidential**: Called when confidential/conclude field is collected
- **onError**: Called on errors

## Field Callback Memoization

The hook tracks which fields have fired callbacks using `useRef<Set<string>>` to ensure each field callback fires exactly once when the field transitions from null/undefined to a FieldProxy value.

```typescript
const firedFieldsRef = useRef<Set<string>>(new Set())

// In effect:
for (const [fieldName, chatfield] of Object.entries(fields)) {
  if (firedFieldsRef.current.has(fieldName)) continue

  const fieldValue = interviewState[fieldName]
  if (fieldValue !== null && fieldValue !== undefined) {
    firedFieldsRef.current.add(fieldName)

    if (chatfield.specs?.confidential || chatfield.specs?.conclude) {
      onConfidential?.(fieldName, fieldValue)
    } else {
      onField?.(fieldName, fieldValue)
    }
  }
}
```

## Development

### Building

```bash
npm run build    # Compile TypeScript
npm run dev      # Watch mode
npm run clean    # Remove dist/
```

### TypeScript Configuration

- **Module**: ESNext for modern bundler compatibility
- **Module Resolution**: bundler (supports package exports)
- **JSX**: React
- **Target**: ES2020
- **Path Mapping**: `@chatfield/core/lean` maps to `../chatfield/index.ts` for direct TypeScript source imports

**Critical**: No `rootDir` specified to allow importing from parent `chatfield/` directory.

## Integration with Frameworks

### Next.js

```typescript
'use client'
import { useChatfield } from '@chatfield/react'
// ... use in client components
```

### Vite

```typescript
import { useChatfield } from '@chatfield/react'
// ... works out of the box
```

### Create React App

```typescript
import { useChatfield } from '@chatfield/react'
// ... works out of the box
```

## Examples

**See**: `TypeScript/examples/react/` for complete examples:
- `simple-form.tsx`: Basic contact form with field callbacks
- `demo.html`: Browser-based demo with React CDN

## Design Principles

1. **Headless**: No UI components, just business logic
2. **Minimal API**: Only essential state and actions
3. **Conversational Focus**: Designed for voice-first, moving away from GUI
4. **Type Safe**: Full TypeScript support
5. **Framework Agnostic**: Works with Next.js, Vite, CRA, etc.

## API Surface

### UseChatfieldOptions

```typescript
interface UseChatfieldOptions {
  onField?: (fieldName: string, fieldProxy: FieldProxy) => void
  onConfidential?: (fieldName: string, fieldProxy: FieldProxy) => void
  onError?: (error: Error) => void
  interviewerOptions?: {
    apiKey?: string
    baseUrl?: string
    endpointSecurity?: 'strict' | 'warn' | 'disabled'
    // ... other Interviewer options
  }
}
```

### ChatfieldState

```typescript
interface ChatfieldState {
  messages: Array<{ role: 'user' | 'assistant', content: string }>
  isReadyForInput: boolean
  interview: Interview
}
```

### ChatfieldActions

```typescript
interface ChatfieldActions {
  send: (message: string) => Promise<void>
}
```

## Dependencies

- **@chatfield/core**: Core Chatfield library (file:../)
- **react**: Peer dependency (^18.0.0 || ^19.0.0)

## Key Considerations

1. **Single Interviewer Instance**: Created once on mount, stored in `useRef`
2. **Field Memoization**: Each field callback fires exactly once
3. **Confidential Fields**: Separate callback for sensitive data
4. **Completion Detection**: Check `state.interview._done` for completion
5. **Error Handling**: Always provide `onError` callback

## Security

**See**: `README.md` for comprehensive security best practices including:
- API key management (never expose in browser)
- LiteLLM proxy configuration
- Endpoint security modes
- Production deployment recommendations

## Additional Resources

- **README**: `TypeScript/react/README.md` for comprehensive documentation
- **Examples**: `TypeScript/examples/react/` for working code
- **Core Docs**: `TypeScript/CLAUDE.md` for Chatfield core
- **API Configuration**: `Documentation/Api_Configuration.md` for security and deployment
