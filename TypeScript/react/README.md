# @chatfield/react

React hooks for Chatfield conversational data collection.

## Overview

`@chatfield/react` provides the `useChatfield` hook for integrating Chatfield interviews into React applications. Transform traditional forms into natural conversations powered by LLMs.

## Installation

```bash
npm install @chatfield/core @chatfield/react
```

**Peer Dependencies:**
- `react` ^18.0.0 || ^19.0.0

## Quick Start

```typescript
import React from 'react'
import { useChatfield } from '@chatfield/react'
import { chatfield } from '@chatfield/core'

// Define interview
const interview = chatfield()
  .field('name')
    .desc('Your name')
  .field('email')
    .desc('Your email address')
  .field('age')
    .desc('Your age')
    .as_int()
  .build()

// Use in React component
function MyForm() {
  const [state, actions] = useChatfield(interview, {
    onField: (fieldName, value) => {
      console.log(`Collected ${fieldName}:`, value)
    },
    onError: (error) => {
      console.error('Error:', error)
    }
  })

  if (state.interview._done) {
    return (
      <div>
        <h2>Complete!</h2>
        <p>Name: {state.interview.name}</p>
        <p>Age: {state.interview.age.as_int}</p>
      </div>
    )
  }

  return (
    <div>
      {state.messages.map((msg, i) => (
        <div key={i} className={msg.role}>
          {msg.content}
        </div>
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

## API Reference

### `useChatfield(interview, options?)`

Main hook for managing Chatfield conversations.

**Parameters:**

- `interview: Interview` - Chatfield interview instance from `chatfield().build()`
- `options?: UseChatfieldOptions` - Optional configuration

**Returns:** `[state, actions]`

### State

```typescript
interface ChatfieldState {
  // Conversation messages (user and assistant only)
  messages: Array<{ role: 'user' | 'assistant', content: string }>

  // True when ready for user input (post-interrupt)
  isReadyForInput: boolean

  // Direct access to Interview instance
  interview: Interview
}
```

**Usage:**

- **`state.messages`** - Display conversation history
- **`state.isReadyForInput`** - Disable input when false
- **`state.interview._done`** - Check if interview complete
- **`state.interview.fieldName`** - Access collected field values

### Actions

```typescript
interface ChatfieldActions {
  // Send user message and process conversation turn
  send: (message: string) => Promise<void>
}
```

### Options

```typescript
interface UseChatfieldOptions {
  // Called when regular field collected (not Confidential/Conclude)
  onField?: (fieldName: string, fieldProxy: FieldProxy) => void

  // Called when Confidential or Conclude field collected
  onConfidential?: (fieldName: string, fieldProxy: FieldProxy) => void

  // Error handler
  onError?: (error: Error) => void

  // Interviewer configuration
  interviewerOptions?: {
    threadId?: string
    baseUrl?: string      // LiteLLM proxy URL (recommended)
    apiKey?: string
    llmId?: string
    temperature?: number | null
    endpointSecurity?: 'strict' | 'warn' | 'disabled'
  }
}
```

### Field Callbacks

**`onField`** fires when a regular field transitions from `null` to collected:

```typescript
useChatfield(interview, {
  onField: (fieldName, fieldProxy) => {
    // Access transformations
    console.log('Raw value:', fieldProxy.toString())
    console.log('As int:', fieldProxy.as_int)
    console.log('As bool:', fieldProxy.as_bool)

    // Track analytics
    analytics.track('field_collected', { fieldName })
  }
})
```

**`onConfidential`** fires for Confidential and Conclude fields:

```typescript
useChatfield(interview, {
  onConfidential: (fieldName, fieldProxy) => {
    // Handle sensitive data
    console.log(`Confidential field collected: ${fieldName}`)
  }
})
```

**Important:** Callbacks fire once per field when it transitions from uncollected to collected.

## Security

**Never expose API keys in browser code!**

✅ **Recommended:** Use LiteLLM proxy

```typescript
const [state, actions] = useChatfield(interview, {
  interviewerOptions: {
    baseUrl: 'http://localhost:4000', // Your LiteLLM proxy
    apiKey: 'proxy-key'
  }
})
```

See [LiteLLM Proxy Setup](../../Documentation/PROXY_SETUP.md) for configuration.

❌ **Not Recommended:** Direct API key (development only)

```typescript
// Only for local development, never in production!
const [state, actions] = useChatfield(interview, {
  interviewerOptions: {
    apiKey: process.env.REACT_APP_OPENAI_KEY,
    endpointSecurity: 'warn'
  }
})
```

## Examples

See [examples/react/](../../examples/react/) for complete examples:

- **simple-form.tsx** - Basic contact form
- More examples coming soon

## Framework Integration

### Vite

Works out of the box:

```bash
npm create vite@latest my-app -- --template react-ts
npm install @chatfield/core @chatfield/react
```

### Next.js

See [Issue #66](https://github.com/jhs/Chatfield/issues/66) for comprehensive Next.js guide.

Basic usage:

```typescript
// app/components/ChatfieldForm.tsx
'use client'

import { useChatfield } from '@chatfield/react'
import { interview } from '../interviews/contact'

export function ChatfieldForm() {
  const [state, actions] = useChatfield(interview, {
    interviewerOptions: {
      baseUrl: process.env.NEXT_PUBLIC_LITELLM_PROXY
    }
  })
  // ... component implementation
}
```

### Create React App

```bash
npx create-react-app my-app --template typescript
npm install @chatfield/core @chatfield/react
```

## Advanced Usage

### Accessing Interview State

```typescript
const [state, actions] = useChatfield(interview)

// Check completion
if (state.interview._done) {
  console.log('Complete!')
}

// Access fields
const name = state.interview.name  // FieldProxy or null
const age = state.interview.age?.as_int  // number or undefined

// Check individual field status
if (state.interview.email) {
  console.log('Email collected:', state.interview.email)
}
```

### Multiple Interviews

```typescript
// Use separate hook instances for multiple interviews
const [contactState, contactActions] = useChatfield(contactInterview)
const [surveyState, surveyActions] = useChatfield(surveyInterview)
```

### Custom Message Display

```typescript
const [state, actions] = useChatfield(interview)

return (
  <div>
    {state.messages.map((msg, index) => (
      <div
        key={index}
        style={{
          textAlign: msg.role === 'user' ? 'right' : 'left',
          color: msg.role === 'user' ? 'blue' : 'black'
        }}
      >
        <strong>{msg.role}:</strong> {msg.content}
      </div>
    ))}
  </div>
)
```

## TypeScript Support

Full TypeScript support with type inference:

```typescript
import type { ChatfieldState, ChatfieldActions } from '@chatfield/react'

const [state, actions]: [ChatfieldState, ChatfieldActions] = useChatfield(interview)

// state.messages is typed as Array<{role: 'user' | 'assistant', content: string}>
// state.isReadyForInput is boolean
// state.interview is Interview
// actions.send is (message: string) => Promise<void>
```

## Error Handling

```typescript
const [state, actions] = useChatfield(interview, {
  onError: (error) => {
    // Handle different error types
    if (error.message.includes('API key')) {
      console.error('Authentication error:', error)
    } else if (error.message.includes('network')) {
      console.error('Network error:', error)
    } else {
      console.error('Unknown error:', error)
    }

    // Show user-friendly message
    alert('Something went wrong. Please try again.')
  }
})
```

## Performance Considerations

- The hook creates a single `Interviewer` instance per component
- Messages are stored in React state (not persisted)
- Field callbacks use memoization to fire only once per field
- Interview state updates trigger re-renders

## Limitations

- No built-in persistence (localStorage, etc.) - implement in parent component if needed
- No streaming support yet (see [Issue #63](https://github.com/jhs/Chatfield/issues/63))
- No time-travel/branching yet (see [Issue #3](https://github.com/jhs/Chatfield/issues/3))

## Contributing

See main [Chatfield repository](https://github.com/jhs/Chatfield) for contribution guidelines.

## License

MIT

## Links

- [Chatfield Core](https://www.npmjs.com/package/@chatfield/core)
- [Documentation](https://github.com/jhs/Chatfield/tree/main/Documentation)
- [Examples](https://github.com/jhs/Chatfield/tree/main/TypeScript/examples/react)
- [Issues](https://github.com/jhs/Chatfield/issues)
