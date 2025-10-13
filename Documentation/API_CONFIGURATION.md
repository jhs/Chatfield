# API Configuration

## Environment Configuration

Both implementations require OpenAI API key:

```bash
# Option 1: Environment variable
export OPENAI_API_KEY=your-api-key

# Option 2: .env file in project root
echo "OPENAI_API_KEY=your-api-key" > .env

# Option 3: Pass to Interviewer constructor
interviewer = Interviewer(interview, api_key="your-api-key")
```

## Python API Initialization

The `Interviewer` constructor supports flexible API configuration for different deployment scenarios:

```python
from chatfield import Interviewer, chatfield

interview = chatfield().field("name").build()

# Option 1: Use environment variable (default)
interviewer = Interviewer(interview)

# Option 2: Explicit API key
interviewer = Interviewer(interview, api_key='your-api-key')

# Option 3: Custom base URL (e.g., LiteLLM proxy)
interviewer = Interviewer(
    interview,
    api_key='your-api-key',
    base_url='https://my-litellm-proxy.com/v1'
)

# Option 4: Both custom base URL and API key
interviewer = Interviewer(
    interview,
    base_url='https://my-proxy.com/openai',
    api_key='proxy-api-key'
)
```

**Constructor Parameters:**
- `interview` (Interview): The interview instance to orchestrate
- `thread_id` (Optional[str]): Custom thread ID for conversation tracking
- `llm` (Optional): Custom LLM instance (overrides all other LLM config)
- `llm_id` (Optional[str]): LLM model identifier (default: 'openai:gpt-4o')
- `temperature` (Optional[float]): Temperature for LLM generation (default: 0.0)
- `base_url` (Optional[str]): Custom API endpoint (e.g., for LiteLLM proxies)
- `api_key` (Optional[str]): API key (falls back to OPENAI_API_KEY env var)
- `endpoint_security` (Optional[EndpointSecurityMode]): Security mode for endpoint validation ('strict', 'warn', or 'disabled', default: 'disabled')

## TypeScript API Initialization

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

## Use Cases

- **Production**: Use `baseUrl` to point to a LiteLLM proxy that handles authentication
- **Development**: Use environment variables for simplicity
- **Testing**: Pass explicit `apiKey` and `baseUrl` for test environments
- **Multi-tenant**: Different API keys per Interviewer instance

## Endpoint Security Modes

The `endpoint_security`/`endpointSecurity` parameter controls how the Interviewer validates API endpoints to prevent accidental exposure of API keys.

### Python Endpoint Security

```python
from chatfield import Interviewer, chatfield

interview = chatfield().field("name").build()

# Option 1: Disabled mode (default for server-side Python)
# Allows official endpoints like api.openai.com
interviewer = Interviewer(
    interview,
    api_key='your-api-key',
    base_url='https://api.openai.com/v1',
    endpoint_security='disabled'  # or omit, as this is the default
)

# Option 2: Strict mode
# Blocks official endpoints, requires proxy
interviewer = Interviewer(
    interview,
    api_key='your-api-key',
    base_url='https://my-proxy.com/v1',
    endpoint_security='strict'  # Raises ValueError for api.openai.com, api.anthropic.com
)

# Option 3: Warn mode
# Warns about official endpoints but allows them
interviewer = Interviewer(
    interview,
    api_key='your-api-key',
    base_url='https://api.openai.com/v1',
    endpoint_security='warn'  # Logs warning but continues
)
```

### TypeScript Endpoint Security

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

### Security Mode Behavior

- **`'strict'`**: Throws Error when official endpoints are detected (api.openai.com, api.anthropic.com). Forces use of a backend proxy. Default for browser in TypeScript, must be explicitly enabled in Python.
- **`'warn'`**: Logs warnings to console when official endpoints are detected, but allows the connection. Useful for development with awareness of potential issues.
- **`'disabled'`**: Detection logic runs and logs debug messages, but allows all endpoints including official ones. Use for server-side applications where API keys are protected. Default for Python and Node.js/server in TypeScript.

**Dangerous Endpoints Detected:**
- `api.openai.com`
- `api.anthropic.com`

**Environment-Based Defaults:**
- **Python**: Defaults to `'disabled'` (server-side only)
- **TypeScript Browser**: Defaults to `'strict'` mode. Cannot be set to `'disabled'`.
- **TypeScript Node.js/Server**: Defaults to `'disabled'` mode.

**Note:** TypeScript automatically detects browser vs. server environments and applies appropriate defaults. Python runs server-side only and defaults to `'disabled'`.
