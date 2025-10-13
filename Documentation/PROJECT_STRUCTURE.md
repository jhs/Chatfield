# Project Structure

## Repository Layout

```
Chatfield/
├── Documentation/               # Project-wide documentation
│   ├── ISOMORPHIC_DEVELOPMENT.md  # Isomorphic development principles
│   ├── COMMANDS.md                # Development commands reference
│   ├── API_CONFIGURATION.md       # API and environment setup
│   ├── BUILDER_API.md             # Builder pattern API reference
│   ├── PROJECT_STRUCTURE.md       # This file
│   ├── ARCHITECTURE.md            # System architecture details
│   ├── TESTING_ARCHITECTURE.md    # Testing approach and structure
│   ├── DESIGN_DECISIONS.md        # Key design decisions
│   ├── COOKBOOK.md                # Common patterns and recipes
│   ├── PROMPT_SYSTEM.md           # LLM prompt engineering
│   ├── Getting_Started_Python.md  # Python quickstart
│   ├── Getting_Started_TypeScript.md # TypeScript quickstart
│   └── README.md                  # Documentation index
│
├── Python/                      # Python implementation (v0.2.0)
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
└── TypeScript/                  # TypeScript/JavaScript implementation (v0.1.0)
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

All documentation lives in `Documentation/`:
- **Core concepts**: `ISOMORPHIC_DEVELOPMENT.md`, `ARCHITECTURE.md`
- **Getting started**: `Getting_Started_Python.md`, `Getting_Started_TypeScript.md`
- **Reference**: `BUILDER_API.md`, `API_CONFIGURATION.md`, `COMMANDS.md`
- **Testing**: `TESTING_ARCHITECTURE.md`
- **Advanced**: `DESIGN_DECISIONS.md`, `COOKBOOK.md`, `PROMPT_SYSTEM.md`

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

See `Documentation/ISOMORPHIC_DEVELOPMENT.md` for details on maintaining this correspondence.
