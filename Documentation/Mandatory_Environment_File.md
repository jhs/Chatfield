# Environment Setup

Chatfield requires API keys to function. Create a `.env.secret` file in the project root directory to configure your environment.

Here is a sample file you can use to get started. You must paste your values for all **mandatory** keys.

```bash
# =========
# MANDATORY
# =========

# OpenAI API Key - Required for Chatfield's LLM backend
# Get your key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-...your-key-here...

# ==================================
# OPTIONAL FOR CHATFIELD DEVELOPMENT
# ==================================

# Anthropic API Key - Only needed for using Anthropic models in evaluations
# Get your key from: https://console.anthropic.com/settings/keys
# ANT_API_KEY=sk-ant-...your-key-here...

# LangSmith API Key - Only needed for tracing and debugging on smith.langchain.com
# Get your key from: https://smith.langchain.com/settings
# LANGSMITH_API_KEY=lsv2_pt_...your-key-here...

# OpenRouter API Key - Only needed for evaluations with alternative models
# Get your key from: https://openrouter.ai/keys
# OPENROUTER_API_KEY=sk-or-...your-key-here...
```
