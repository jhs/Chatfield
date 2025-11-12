# LiteLLM Proxy Setup for Chatfield Browser Development

This guide explains how to set up and use the LiteLLM proxy for secure browser-based development with Chatfield.

## Overview

The LiteLLM proxy enables secure browser-based Chatfield applications by:
- **Keeping API keys server-side** (not exposed in browser)
- **Providing rate limiting** for cost control
- **Enabling usage tracking** and audit trails
- **Supporting multiple LLM providers** (OpenAI, Anthropic, etc.)
- **Simplifying CORS** for local development

## Architecture

```
Browser (Chatfield App)
    ↓ HTTP
LiteLLM Proxy (localhost:4000)
    ↓ HTTPS
OpenAI API / Other Providers
```

## Prerequisites

### 1. Python Environment (for running proxy)

```bash
cd Python
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"     # Includes litellm
```

### 2. OpenAI API Key

Set your OpenAI API key as an environment variable:

```bash
# Linux/Mac
export OPENAI_API_KEY=your-api-key-here

# Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key-here"

# Or use a .env file
echo "OPENAI_API_KEY=your-api-key" > Python/.env
```

### 3. TypeScript Build

Build the browser bundles:

```bash
cd TypeScript
npm install
npm run build
```

## Running the Proxy

### Method 1: Using Python (Recommended)

From the TypeScript directory:

```bash
npm run proxy
```

Or from the Python directory:

```bash
make proxy
# or
python litellm_proxy.py
```

The proxy will start on `http://localhost:4000` by default.

### Method 2: Using Docker Compose (Optional)

If you prefer Docker:

```yaml
# docker-compose.yml (example)
version: '3.8'
services:
  litellm:
    image: ghcr.io/berriai/litellm:latest
    ports:
      - "4000:4000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./Python/litellm_config.yaml:/app/config.yaml
    command: --config /app/config.yaml
```

## Configuration

The proxy is configured via `Python/litellm_config.yaml`:

```yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: gpt-4o
      api_key: os.environ/OPENAI_API_KEY

litellm_settings:
  set_verbose: true
  max_tokens: 4000
  allowed_origins:
    - "http://localhost:8080"
    - "http://127.0.0.1:8080"
```

### Key Configuration Options

- **`model_list`**: Define available models and their providers
- **`allowed_origins`**: CORS whitelist for browser access
- **`max_tokens`**: Default token limit to control costs
- **`set_verbose`**: Enable detailed logging for debugging

## Using the Proxy in Code

### TypeScript/JavaScript

```typescript
import { chatfield, Interviewer } from '@chatfield/core';

const interview = chatfield()
  .field('name')
    .desc('Your name')
  .build();

// Option 1: Pass proxy URL directly
const interviewer = new Interviewer(interview, {
  proxyUrl: 'http://localhost:4000'
});

// Option 2: Use environment variable
// Set LITELLM_PROXY_URL in your environment
const interviewer2 = new Interviewer(interview);
```

### Browser HTML

```html
<script type="module">
  import { chatfield, Interviewer } from '/dist/esm/index.js';

  const interview = chatfield()
    .field('email')
    .desc('Your email')
    .build();

  const interviewer = new Interviewer(interview, {
    proxyUrl: 'http://localhost:4000'
  });

  const response = await interviewer.go();
</script>
```

## Running Browser Examples

1. **Start the proxy** (in one terminal):
   ```bash
   cd TypeScript
   npm run proxy
   ```

2. **Serve the examples** (in another terminal):
   ```bash
   cd TypeScript
   npm run serve:examples
   ```

3. **Open in browser**:
   - Basic Example: http://localhost:8080/examples/browser/basic-usage.html
   - Job Interview: http://localhost:8080/examples/browser/job-interview.html

## Troubleshooting

### Proxy won't start

**Error**: `litellm command not found`

**Solution**: Install LiteLLM in Python environment:
```bash
cd Python
pip install -e ".[dev]"
```

### API Key not recognized

**Error**: `OpenAI API key not found`

**Solution**: Set the OPENAI_API_KEY environment variable:
```bash
export OPENAI_API_KEY=your-key
```

### CORS errors in browser

**Error**: `Access-Control-Allow-Origin` blocked

**Solution**: Add your origin to `allowed_origins` in `litellm_config.yaml`:
```yaml
litellm_settings:
  allowed_origins: ["http://localhost:8080"]
```

### Connection refused

**Error**: `Failed to fetch` or `Connection refused`

**Solution**:
1. Verify proxy is running: `curl http://localhost:4000/health`
2. Check proxy URL matches in code: `proxyUrl: 'http://localhost:4000'`
3. Ensure no firewall blocking port 4000

### Rate limit errors

**Error**: `Rate limit exceeded`

**Solution**: Configure rate limits in `litellm_config.yaml` or use a different model:
```yaml
model_list:
  - model_name: gpt-4o-mini  # Cheaper model
    litellm_params:
      model: gpt-4o-mini
      api_key: os.environ/OPENAI_API_KEY
```

## Advanced Configuration

### Virtual Keys (Production)

For production, use virtual keys with rate limits:

```yaml
general_settings:
  master_key: "your-secret-master-key"
  database_url: "sqlite:///litellm_proxy.db"
```

Generate virtual keys:
```bash
curl -X POST http://localhost:4000/key/generate \
  -H "Authorization: Bearer your-secret-master-key" \
  -H "Content-Type: application/json" \
  -d '{
    "max_budget": 10.0,
    "models": ["gpt-4o", "gpt-4o-mini"]
  }'
```

### Multiple Providers

Configure multiple LLM providers:

```yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: gpt-4o
      api_key: os.environ/OPENAI_API_KEY

  - model_name: claude-3
    litellm_params:
      model: claude-3-opus-20240229
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: gemini-pro
    litellm_params:
      model: gemini/gemini-pro
      api_key: os.environ/GEMINI_API_KEY
```

### PostgreSQL Backend

For persistence and audit trails:

```yaml
general_settings:
  database_url: "postgresql://user:pass@localhost:5432/litellm"
```

With Docker Compose:
```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: litellm
      POSTGRES_USER: litellm
      POSTGRES_PASSWORD: password

  litellm:
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://litellm:password@postgres:5432/litellm
```

## Security Best Practices

1. **Never expose API keys in browser code**
   - Always use the proxy for browser apps
   - Keep keys in server-side environment variables

2. **Use virtual keys for production**
   - Generate limited-scope keys
   - Set budget limits per key
   - Rotate keys regularly

3. **Enable rate limiting**
   - Protect against runaway costs
   - Limit requests per user/IP

4. **Use HTTPS in production**
   - Never use HTTP for production traffic
   - Use a reverse proxy (nginx, Caddy) with SSL

5. **Monitor usage**
   - Track API costs in proxy logs
   - Set up alerts for unusual patterns
   - Review audit trails regularly

## Development Workflow

Typical development workflow with the proxy:

```bash
# Terminal 1: Start proxy
cd Python
make proxy

# Terminal 2: Serve examples
cd TypeScript
npm run serve:examples

# Terminal 3: Development (optional)
cd TypeScript
npm run dev  # Watch mode for builds
```

## Resources

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [LiteLLM Proxy Docs](https://docs.litellm.ai/docs/simple_proxy)
- [Chatfield GitHub Issues](https://github.com/yourusername/chatfield/issues)

## Support

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review proxy logs for error messages
3. Open an issue with:
   - Proxy configuration
   - Error messages
   - Steps to reproduce