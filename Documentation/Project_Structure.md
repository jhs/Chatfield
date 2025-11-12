# Project Structure

## Repository Layout

```
Chatfield/
├── Documentation/               # Project-wide documentation
│   ├── Isomorphic_Development.md  # Isomorphic development principles
│   ├── Commands.md                # Development commands reference
│   ├── Api_Configuration.md       # API and environment setup
│   ├── Builder_Api.md             # Builder pattern API reference
│   ├── Project_Structure.md       # This file
│   ├── Architecture.md            # System architecture details
│   ├── Testing_Architecture.md    # Testing approach and structure
│   ├── Design_Decisions.md        # Key design decisions
│   ├── Cookbook.md                # Common patterns and recipes
│   ├── Prompt_System.md           # LLM prompt engineering
│   ├── Getting_Started_Python.md  # Python quickstart
│   ├── Getting_Started_TypeScript.md # TypeScript quickstart
│   └── README.md                  # Documentation index
│
├── Python/                      # Python implementation (v1.0.0a2)
│   ├── chatfield/               # Core Python package
│   │   ├── __init__.py          # Main exports and public API
│   │   ├── interview.py         # Base Interview class with field discovery
│   │   ├── interviewer.py       # LangGraph-based conversation orchestration
│   │   ├── field_proxy.py       # FieldProxy string subclass for transformations
│   │   ├── builder.py           # Fluent builder API
│   │   ├── serialization.py     # Interview state serialization
│   │   ├── presets.py           # Common preset configurations
│   │   └── visualization.py     # Graph visualization utilities
│   ├── tests/                   # Test suite (test_*.py naming, pytest-describe structure)
│   │   ├── test_interview.py    # Interview class tests
│   │   ├── test_interviewer.py  # Interviewer orchestration tests
│   │   ├── test_interviewer_conversation.py # Conversation flow tests
│   │   ├── test_builder.py      # Builder API tests
│   │   ├── test_field_proxy.py  # FieldProxy tests
│   │   ├── test_custom_transformations.py # Transformation system tests
│   │   ├── test_conversations.py # End-to-end conversation tests
│   │   └── CLAUDE.md            # Test suite documentation
│   ├── examples/                # Python usage examples
│   │   ├── job_interview.py     # Job application interview example
│   │   ├── restaurant_order.py  # Restaurant ordering conversation
│   │   ├── tech_request.py      # Technical support request form
│   │   └── favorite_number.py   # Simple number collection with validation
│   ├── Makefile                 # Python development shortcuts
│   ├── pyproject.toml           # Python package configuration
│   └── CLAUDE.md                # Python-specific implementation guide
│
└── TypeScript/                  # TypeScript/JavaScript implementation (v1.0.0a2)
    ├── chatfield/               # TypeScript source code
    │   ├── index.ts             # Main exports and public API
    │   ├── interview.ts         # Base Interview class (mirrors Python)
    │   ├── interviewer.ts       # LangGraph conversation orchestration
    │   ├── field-proxy.ts       # FieldProxy for transformations
    │   ├── builder.ts           # Primary fluent builder API
    │   ├── builder-types.ts     # TypeScript type definitions for builder
    │   ├── types.ts             # Core type definitions
    │   └── integrations/        # Framework integrations
    │       ├── react.ts         # React hooks
    │       ├── react-components.tsx # UI components
    │       └── copilotkit.tsx   # CopilotKit integration
    ├── tests/                   # Jest test suite (*.test.ts naming, mirrors Python)
    │   ├── interview.test.ts    # Interview class tests (mirrors test_interview.py)
    │   ├── interviewer.test.ts  # Interviewer orchestration tests
    │   ├── interviewer_conversation.test.ts # Conversation flow tests
    │   ├── builder.test.ts      # Builder API tests
    │   ├── field_proxy.test.ts  # FieldProxy implementation tests
    │   ├── custom_transformations.test.ts # Transformation system tests
    │   ├── conversations.test.ts # End-to-end conversation tests
    │   ├── integration/         # Integration test scenarios
    │   │   └── react.ts        # React hooks integration tests
    │   └── CLAUDE.md            # Test suite documentation
    ├── examples/                # TypeScript/JavaScript examples
    │   ├── basic-usage.ts       # Simple builder pattern example
    │   ├── job-interview.ts     # Job application (mirrors Python)
    │   ├── restaurant-order.ts  # Restaurant ordering
    │   ├── schema-based.ts      # Schema-driven approach
    │   └── type-safe-demo.ts    # TypeScript type inference demo
    ├── package.json             # Node package configuration
    ├── tsconfig.json            # TypeScript compiler configuration
    ├── jest.config.js           # Jest testing configuration
    ├── minimal.ts               # Minimal OpenAI API test script
    └── CLAUDE.md                # TypeScript-specific implementation guide
```

## Key Files to Understand

### Python Core Files
- `chatfield/interview.py`: Base Interview class, field discovery, _chatfield structure
- `chatfield/interviewer.py`: LangGraph orchestration, tool generation, state management
- `chatfield/builder.py`: Fluent builder API
- `chatfield/field_proxy.py`: String subclass for transformation access
- `chatfield/serialization.py`: State serialization for LangGraph

### TypeScript Core Files
- `chatfield/interview.ts`: Base Interview class (mirrors Python implementation)
- `chatfield/interviewer.ts`: LangGraph TypeScript orchestration
- `chatfield/builder.ts`: Primary fluent builder API
- `chatfield/field-proxy.ts`: FieldProxy implementation for transformations
- `chatfield/types.ts`: Core TypeScript type definitions

## Naming Conventions

### File Naming
- **Python**: `snake_case.py` (e.g., `field_proxy.py`)
- **TypeScript**: `kebab-case.ts` (e.g., `field-proxy.ts`)
- **Tests Python**: `test_*.py` (e.g., `test_interview.py`)
- **Tests TypeScript**: `*.test.ts` (e.g., `interview.test.ts`)

### Code Naming
- **Python**: `snake_case` for functions/methods
- **TypeScript**: `camelCase` for functions/methods
- **Both**: `PascalCase` for classes
- **Both**: `_leading_underscore` for private/internal

## Documentation Organization

### Agent Documentation System

This project uses a structured **Agent Documentation** system - UPPERCASE `.md` files designed for AI coding agents. The system follows a two-tier hierarchy:

**Tier 1: Overview Files (CLAUDE.md)**
- Located at key directory levels (root, Python/, TypeScript/, tests/, examples/)
- Provide high-level overviews with references to detailed documentation
- Keep content concise (<200 lines)

**Tier 2: Detailed Files (Documentation/ directory)**
- `Documentation/` directory contains all detailed documentation (centralized)
- Agent-focused files use UPPERCASE naming (e.g., `AGENT_DOCUMENTATION.md`)
- Human-focused files use Normal_Case naming (e.g., `Architecture.md`)
- Can be comprehensive and extensive

**See**: [AGENT_DOCUMENTATION.md](AGENT_DOCUMENTATION.md) for complete details on the Agent Documentation system, naming conventions, and maintenance guidelines.

### Documentation/ Directory (Project-Wide Reference)

The `Documentation/` directory contains **all detailed documentation** for both AI agents and humans:
- **Agent-focused (UPPERCASE)**: `AGENT_DOCUMENTATION.md`, `JS_CONVERSION_PLAN.md`, `PROXY_SETUP.md`, `ROLLUP_BUILD_OPTIONS.md`, `CONVERTING_WITH_SCREENSHOTS.md`, `CLAUDE_SKILLS_BEST_PRACTICES.md`
- **Core concepts**: `Isomorphic_Development.md`, `Architecture.md`
- **Getting started**: `Getting_Started_Python.md`, `Getting_Started_TypeScript.md`
- **Reference**: `Builder_Api.md`, `Api_Configuration.md`, `Commands.md`, `Project_Structure.md`
- **Testing**: `TESTING_Architecture.md`
- **Advanced**: `Design_Decisions.md`, `Cookbook.md`, `Prompt_System.md`

**Note**: `Documentation/` serves as the central repository for all project documentation. Use UPPERCASE for agent-focused files and Normal_Case for human-focused files.

## File Correspondence

The isomorphic nature means files directly correspond:

| Python | TypeScript | Purpose |
|--------|-----------|---------|
| `interview.py` | `interview.ts` | Base Interview class |
| `interviewer.py` | `interviewer.ts` | LangGraph orchestration |
| `builder.py` | `builder.ts` | Fluent builder API |
| `field_proxy.py` | `field-proxy.ts` | FieldProxy implementation |
| `test_interview.py` | `interview.test.ts` | Interview tests |
| `test_builder.py` | `builder.test.ts` | Builder tests |

See `Documentation/Isomorphic_Development.md` for details on maintaining this correspondence.
