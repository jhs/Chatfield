# CLAUDE.md

This file provides guidance to Claude Code when working with the integration modules in this directory.

## Overview

This directory contains integration modules that connect the Chatfield TypeScript/JavaScript library with popular frameworks and tools, particularly React and CopilotKit. The integrations provide hooks, components, and utilities for seamless UI integration of conversational data collection.

## Project Structure

```
TypeScript/src/integrations/
├── react.ts      # React hooks and components for Chatfield
└── CLAUDE.md     # This documentation file
```

## Key Files

### react.ts
- **Purpose**: React integration for Chatfield conversations
- **Status**: Currently being refactored to use new Interviewer class
- **Features**: Hooks for conversation state, UI components, progress tracking
- **Dependencies**: React (optional - gracefully handles missing React)

## Architecture Overview

### React Integration Components

1. **useConversation Hook**
   - Main hook for managing conversation state
   - Handles message flow, field collection, validation
   - Provides actions for user interaction
   - Tracks progress and completion

2. **ConversationState Interface**
   ```typescript
   interface ConversationState {
     messages: ConversationMessage[]
     collectedData: CollectedData
     currentField: FieldMeta | null
     isComplete: boolean
     isLoading: boolean
     isWaitingForUser: boolean
     validationError: string | null
     totalFields: number
     completedFields: number
     progress: number // 0-100
   }
   ```

3. **ConversationActions Interface**
   ```typescript
   interface ConversationActions {
     sendMessage: (message: string) => Promise<void>
     retry: () => Promise<void>
     reset: () => void
     skipField: () => void
   }
   ```

## Current Status and Refactoring Notes

### Temporary State
The React integration is currently in a transitional state:
- The original `Conversation` class has been removed
- Integration is being refactored to use the new `Interviewer` class
- Current implementation includes stubs and warnings
- Full functionality will be restored after refactoring

### Migration Path
```typescript
// Old approach (removed)
const conversation = new Conversation(gatherer)

// New approach (to be implemented)
const interviewer = new Interviewer(gatherer)
```

## Development Commands

### Testing React Integration

```bash
# Run React integration tests
npm test integration/react

# Run with React Testing Library
npm test -- --testEnvironment=jsdom integration/react

# Build and verify React imports
npm run build
```

### Development Setup

```bash
# Install React (if not already installed)
npm install react react-dom

# Install React types
npm install -D @types/react @types/react-dom

# Install testing utilities
npm install -D @testing-library/react @testing-library/react-hooks
```

## Usage Patterns

### Basic Hook Usage

```typescript
import { useConversation } from 'chatfield/integrations/react'

function MyComponent() {
  const [state, actions] = useConversation(gatherer, {
    onComplete: (instance) => {
      console.log('Completed:', instance)
    },
    onError: (error) => {
      console.error('Error:', error)
    }
  })

  return (
    <div>
      <div>Progress: {state.progress}%</div>
      <button onClick={() => actions.sendMessage('Hello')}>
        Send
      </button>
    </div>
  )
}
```

### With CopilotKit Integration

```typescript
import { CopilotSidebar } from '@copilotkit/react-ui'
import { ChatfieldConversation } from 'chatfield/integrations/react'

function App() {
  return (
    <CopilotSidebar>
      <ChatfieldConversation 
        gatherer={MyForm}
        onComplete={handleComplete}
      />
    </CopilotSidebar>
  )
}
```

### Custom UI Components

```typescript
// Message display component
function ConversationMessages({ state }) {
  return (
    <div className="messages">
      {state.messages.map((msg, i) => (
        <div key={i} className={msg.role}>
          {msg.content}
        </div>
      ))}
    </div>
  )
}

// Input component
function ConversationInput({ actions, state }) {
  const [input, setInput] = useState('')
  
  const handleSubmit = (e) => {
    e.preventDefault()
    actions.sendMessage(input)
    setInput('')
  }
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        disabled={!state.isWaitingForUser}
      />
    </form>
  )
}
```

## Important Patterns

### Optional React Dependency

The integration handles missing React gracefully:

```typescript
let useState: any, useEffect: any, useCallback: any
try {
  const react = require('react')
  useState = react.useState
  useEffect = react.useEffect
  // ...
} catch {
  // React not available - hooks will throw runtime errors
}
```

### State Management

The hook manages complex state transitions:

1. **Initialization**: Set up conversation, prepare first field
2. **User Input**: Accept message, validate, update state
3. **Field Progression**: Move to next field after validation
4. **Completion**: Handle final state, trigger callbacks
5. **Error Handling**: Manage validation errors, retries

### Progress Tracking

Progress is calculated based on field completion:

```typescript
const progress = (completedFields / totalFields) * 100
```

## Known Considerations

1. **React Version**: Requires React 16.8+ for hooks support
2. **Refactoring Status**: Currently being migrated to use Interviewer
3. **Optional Dependency**: React is not a required dependency
4. **Type Safety**: Full TypeScript support with proper types
5. **Server-Side Rendering**: Not currently SSR-compatible
6. **State Persistence**: State is not persisted between sessions
7. **Concurrent Mode**: Not tested with React 18 concurrent features
8. **Error Boundaries**: Recommend wrapping in error boundary

## Testing Approach

### Unit Tests
```typescript
import { renderHook, act } from '@testing-library/react-hooks'

test('useConversation initializes correctly', () => {
  const { result } = renderHook(() => 
    useConversation(gatherer)
  )
  
  expect(result.current[0].isComplete).toBe(false)
  expect(result.current[0].messages).toEqual([])
})
```

### Integration Tests
```typescript
import { render, fireEvent, waitFor } from '@testing-library/react'

test('full conversation flow', async () => {
  const { getByRole, getByText } = render(
    <ConversationComponent gatherer={gatherer} />
  )
  
  // Interact with the component
  fireEvent.click(getByRole('button'))
  
  await waitFor(() => {
    expect(getByText('Thank you')).toBeInTheDocument()
  })
})
```

## Future Enhancements

### Planned Features
1. **Interviewer Integration**: Complete refactoring to use Interviewer class
2. **Streaming Support**: Real-time message streaming from LLM
3. **Voice Input**: Integration with Web Speech API
4. **File Uploads**: Support for file attachments in conversations
5. **Multi-language**: i18n support for UI elements
6. **Accessibility**: Full ARIA support and keyboard navigation
7. **Themes**: Customizable UI themes and styles
8. **Analytics**: Conversation analytics and metrics

### API Improvements
```typescript
// Future API possibilities
const [state, actions] = useConversation(gatherer, {
  backend: customBackend,
  persistence: localStorage,
  streaming: true,
  voice: true,
  theme: 'dark',
  locale: 'en-US'
})
```

## Common Issues and Solutions

- **React not found**: Install React or handle gracefully in non-React apps
- **Hook rules violation**: Ensure hooks are called at top level
- **Stale closures**: Use callback refs for event handlers
- **Memory leaks**: Clean up effects properly
- **Type errors**: Ensure proper TypeScript configuration
- **SSR issues**: Wrap in dynamic import for Next.js

## Migration Guide

### From Old Conversation Class
```typescript
// Old (removed)
const conversation = new Conversation(gatherer)
await conversation.start()

// New (to be implemented)
const interviewer = new Interviewer(gatherer)
await interviewer.run()
```

### Hook Migration
The hook API will remain largely the same after refactoring:
```typescript
// API remains stable
const [state, actions] = useConversation(gatherer)
```

## Contributing

When updating this integration:

1. Maintain backward compatibility where possible
2. Update tests for new features
3. Document breaking changes clearly
4. Consider React version compatibility
5. Test with and without React installed
6. Update TypeScript types
7. Add examples for new features
8. Update this CLAUDE.md file