# React Examples

This directory contains React examples demonstrating the `@chatfield/react` package.

## Examples

### `simple-form.tsx`
A basic contact form demonstrating:
- `useChatfield` hook usage
- Message display
- User input handling
- Field collection callbacks
- Completion detection

## Running the Examples

These examples are **reference implementations** showing how to use `@chatfield/react` in your own React application.

### Option 1: Use in Your Existing React App

1. **Install dependencies:**
   ```bash
   npm install @chatfield/core @chatfield/react
   ```

2. **Set up LiteLLM proxy** (recommended for development):
   ```bash
   # See TypeScript/CLAUDE/PROXY_SETUP.md
   docker-compose up
   ```

3. **Copy example code** from `simple-form.tsx` into your app

4. **Configure Interviewer** with proxy URL:
   ```typescript
   const [state, actions] = useChatfield(interview, {
     interviewerOptions: {
       baseUrl: 'http://localhost:4000',
       apiKey: 'your-api-key'
     }
   })
   ```

### Option 2: Quick Start with Vite

```bash
# Create new Vite app
npm create vite@latest my-chatfield-app -- --template react-ts
cd my-chatfield-app

# Install dependencies
npm install @chatfield/core @chatfield/react

# Copy example
cp ../examples/react/simple-form.tsx src/App.tsx

# Run
npm run dev
```

### Option 3: Use with Next.js

See issue #66 for comprehensive Next.js integration guide (coming soon).

## Key Concepts

### Hook API

```typescript
const [state, actions] = useChatfield(interview, options)
```

**State:**
- `state.messages` - Array of `{role, content}` messages
- `state.isReadyForInput` - Boolean indicating if ready for user input
- `state.interview` - Direct access to Interview instance

**Actions:**
- `actions.send(message)` - Send user message and process conversation

**Options:**
- `onField` - Callback when regular field is collected
- `onConfidential` - Callback when Confidential/Conclude field is collected
- `onError` - Error handler
- `interviewerOptions` - Configuration passed to Interviewer

### Checking Completion

```typescript
if (state.interview._done) {
  // Interview complete - access collected fields
  console.log(state.interview.name)
  console.log(state.interview.age.as_int)
}
```

### Field Callbacks

```typescript
useChatfield(interview, {
  onField: (fieldName, fieldProxy) => {
    console.log(`Collected ${fieldName}`)
    // Access transformations
    if (fieldName === 'age') {
      console.log('Age as int:', fieldProxy.as_int)
    }
  }
})
```

## Security Note

**Never expose API keys in browser code!** Always use a backend proxy (like LiteLLM) to handle authentication securely.

## More Information

- **Package Documentation:** `../packages/react/README.md`
- **Core Documentation:** `../CLAUDE.md`
- **Next.js Integration:** Issue #66
