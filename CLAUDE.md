# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## About This File

This is an **Agent Documentation** file - part of a structured system of UPPERCASE `.md` files designed specifically for AI coding agents. These files provide comprehensive context about the codebase, architecture, and development practices.

**See**: [CLAUDE/AGENT_DOCUMENTATION.md](CLAUDE/AGENT_DOCUMENTATION.md) for complete information about the Agent Documentation system, naming conventions, and maintenance guidelines.

## Project Overview

Chatfield is a dual-implementation library that transforms data collection from rigid forms into natural conversations powered by LLMs. It provides both Python (v1.0.0a2) and TypeScript/JavaScript (v1.0.0a2) implementations with feature parity as a goal.

**Core Concept**: Replace traditional form fields with conversational dialogues that intelligently gather, validate, and transform structured data through natural language interactions.

**Key Features**:
- LLM-powered conversational data collection
- Smart validation and transformation of responses
- LangGraph-based conversation orchestration
- Fluent builder pattern API
- Full TypeScript type safety
- React and CopilotKit integrations

## Critical: Isomorphic Development

**Both Python and TypeScript implementations are equal first-class citizens.** Code structure, naming, logic, and test suites are nearly identical across languages. This is fundamental to Chatfield.

**See**: [Documentation/Isomorphic_Development.md](Documentation/Isomorphic_Development.md) for complete principles and the "Isomorphic:" comment pattern.

## Quick Start

### Python
```bash
cd Python
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest  # Run tests
```

### TypeScript
```bash
cd TypeScript
npm install
npm run build
npm test  # Run tests
```

**See**: [Documentation/Getting_Started_Python.md](Documentation/Getting_Started_Python.md) and [Documentation/Getting_Started_TypeScript.md](Documentation/Getting_Started_TypeScript.md)

## Development Commands

**See**: [Documentation/Commands.md](Documentation/Commands.md) for complete command reference including:
- Setup & installation
- Testing (pytest for Python, Jest for TypeScript)
- Code quality (formatting, linting, type checking)
- Build & distribution
- Running examples

## Project Structure

```
Chatfield/
├── Documentation/    # All project documentation
├── Python/          # Python implementation (v1.0.0a2)
│   ├── chatfield/   # Core package
│   ├── tests/       # pytest test suite
│   └── examples/    # Usage examples
└── TypeScript/      # TypeScript implementation (v1.0.0a2)
    ├── chatfield/   # Core package
    ├── tests/       # Jest test suite
    └── examples/    # Usage examples
```

**See**: [Documentation/Project_Structure.md](Documentation/Project_Structure.md) for detailed file organization and naming conventions.

## Core Architecture

### Key Concepts
1. **Interview**: Main class that defines fields to collect via builder API
2. **Field Definitions**: Builder calls that define data fields
3. **Field Specifications**: Validation rules (must, reject, hint)
4. **Field Transformations**: Type casts (as_int, as_bool, etc.) computed by LLM
5. **Interviewer**: Orchestrates conversation flow using LangGraph
6. **FieldProxy**: String subclass providing dot-access to transformations
7. **State Management**: LangGraph manages conversation state

### LangGraph State Machine
```
initialize → think → listen → tools → teardown
              ↑        ↓
              └────────┘
```

**See**: [Documentation/Architecture.md](Documentation/Architecture.md) for detailed architecture, data flow, and internal structures.

## Builder API

```python
# Python
interview = (chatfield()
    .field("age")
        .desc("Your age")
        .must("be specific")
        .as_int()
    .build())

# After collection
interview.age              # "25" (string)
interview.age.as_int       # 25 (integer)
```

```typescript
// TypeScript
const interview = chatfield()
  .field('age')
    .desc('Your age')
    .must('be specific')
    .as_int()
  .build()
```

**See**: [Documentation/Builder_Api.md](Documentation/Builder_Api.md) for complete API reference, all validation methods, transformations, and cardinality options.

## API Configuration

Both implementations support:
- Environment variable: `OPENAI_API_KEY`
- Direct API key: `Interviewer(interview, api_key='...')`
- Custom base URL: `base_url='https://my-proxy.com/v1'` (for LiteLLM proxies)
- Endpoint security: `endpoint_security='strict'/'warn'/'disabled'`

**See**: [Documentation/Api_Configuration.md](Documentation/Api_Configuration.md) for detailed configuration options, security modes, and deployment scenarios.

## Testing

Both implementations maintain **isomorphic test suites** with:
- Identical test counts (zero skipped tests)
- Identical test descriptions
- BDD-style organization (pytest-describe in Python, Jest describe/it in TypeScript)
- **NEVER skip tests** - use no-op tests that pass

**See**:
- [Documentation/TESTING_Architecture.md](Documentation/TESTING_Architecture.md) for testing philosophy and structure
- [Python/tests/CLAUDE.md](Python/tests/CLAUDE.md) for Python test suite details
- [TypeScript/tests/CLAUDE.md](TypeScript/tests/CLAUDE.md) for TypeScript test suite details

## Implementation-Specific Documentation

- **Python**: See [Python/CLAUDE.md](Python/CLAUDE.md) for Python-specific details
- **TypeScript**: See [TypeScript/CLAUDE.md](TypeScript/CLAUDE.md) for TypeScript-specific details

## Additional Resources

- **Agent Documentation Guide**: [CLAUDE/AGENT_DOCUMENTATION.md](CLAUDE/AGENT_DOCUMENTATION.md) - How this project's agent documentation system works
- **Developer Guide**: [Developers.md](Developers.md) - Comprehensive guide for setting up development environment, running tests, and contributing
- **Design Decisions**: [Documentation/Design_Decisions.md](Documentation/Design_Decisions.md)
- **Cookbook**: [Documentation/Cookbook.md](Documentation/Cookbook.md) for common patterns
- **Prompt System**: [Documentation/Prompt_System.md](Documentation/Prompt_System.md) for LLM prompt engineering
- **Documentation Index**: [Documentation/README.md](Documentation/README.md)

## Version Management Policy

**All version numbers must be kept in sync across the entire project:**

- `Python/pyproject.toml` - Python package version
- `TypeScript/package.json` - TypeScript/JavaScript package version
- `.claude/skills/filling-pdf-forms/SKILL.md` - Skill metadata version

**Current synchronized version: 1.0.0a2**

When incrementing versions, update all three locations simultaneously in a single commit. This ensures consistency across the Python library, TypeScript library, and related skills/tooling.

## Contributing Guidelines

1. **Isomorphic first**: Maintain both implementations as equal first-class citizens
2. **Synchronize implementations**: Keep code structures, names, and logic identical
3. **Document deviations**: Use "Isomorphic:" comments for language-specific differences
4. **Test coverage**: Write identical tests with same descriptions in both languages
5. **Zero skipped tests**: Use no-op tests instead of skipping
6. **Parallel development**: Implement features in both languages simultaneously
7. **Version sync**: Always update version numbers in Python/pyproject.toml, TypeScript/package.json, and .claude/skills/filling-pdf-forms/SKILL.md together in a single commit

**See**: [Documentation/Isomorphic_Development.md](Documentation/Isomorphic_Development.md) for complete contributing guidelines.

## Key Considerations

1. **Python uses `python` command**: Always use `python`, not `python3`
2. **Test harmonization**: Both implementations use BDD-style test organization
3. **LangGraph versions**: Python uses langgraph 1.0.0a3+, TypeScript uses @langchain/langgraph 1.0.0a3+
4. **Async patterns**: TypeScript uses async/await throughout, Python is primarily synchronous
5. **Transformation computation**: All transformations computed by LLM during collection

## Dependencies

### Python Core
- langchain (0.3.27+), langgraph (1.0.0a3+), langchain-openai (0.3.29+)
- pydantic (2.11.7+), openai (1.99.6+)

### TypeScript Core
- @langchain/core (0.3.72+), @langchain/langgraph (1.0.0a3+), @langchain/openai (0.6.9+)
- openai (4.70.0+), zod, reflect-metadata
