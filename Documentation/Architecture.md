# Chatfield Architecture Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Core Components](#core-components)
3. [Data Flow Architecture](#data-flow-architecture)
4. [LangGraph State Machine](#langgraph-state-machine)
5. [Template System](#template-system)
6. [Dual Implementation Strategy](#dual-implementation-strategy)
7. [Integration Architecture](#integration-architecture)
8. [Key Design Patterns](#key-design-patterns)
9. [Security and Evaluation](#security-and-evaluation)
10. [Performance Considerations](#performance-considerations)

---

## System Overview

Chatfield is a conversational data collection framework that transforms rigid forms into natural, LLM-powered dialogues. It maintains dual implementations in Python (v0.2.0) and TypeScript/JavaScript (v0.1.0) with strict feature parity.

### Design Philosophy

**Core Principle**: Replace traditional form fields with Socratic dialogues that intelligently gather, validate, and transform structured data through natural language interactions.

**Key Goals**:
- Natural conversation flow that feels human
- Robust validation without frustrating users
- Type transformation powered by LLM reasoning
- Framework-agnostic core with integration points
- Identical behavior across Python and TypeScript

---

## Core Components

### 1. Interview Class

**Location**: `chatfield/interview.py` (Python) | `chatfield/interview.ts` (TypeScript)

The Interview class is the central data structure representing a conversational form.

#### Internal Structure (`_chatfield` dictionary)

```python
{
    'type': 'Interview Type Name',           # Human-readable type
    'desc': 'Interview description',         # Purpose/context
    'roles': {
        'alice': {                           # Interviewer (agent)
            'type': 'Agent',
            'traits': ['friendly', 'professional'],
            'possible_traits': {             # Conditional traits
                'empathetic': {
                    'active': False,
                    'desc': 'when user seems stressed'
                }
            }
        },
        'bob': {                             # Interviewee (user)
            'type': 'User',
            'traits': [],
            'possible_traits': {}
        }
    },
    'fields': {
        'field_name': {
            'desc': 'Field description',
            'specs': {                       # Validation rules
                'must': ['be specific'],
                'reject': ['vague answers'],
                'hint': ['Format: X-Y-Z'],
                'confidential': False,       # Track silently
                'conclude': False            # Evaluate post-conversation
            },
            'casts': {                       # Type transformations
                'as_int': {
                    'type': 'int',
                    'prompt': 'Parse as integer'
                },
                'as_lang_fr': {
                    'type': 'str',
                    'prompt': 'Translate to French'
                }
            },
            'value': {                       # Populated by LLM
                'value': '25',               # Primary string value
                'as_quote': 'I am 25',       # Direct quote
                'as_context': '...',         # Conversation context
                'as_int': 25,                # Transformed values
                'as_lang_fr': 'vingt-cinq'
            }
        },
        # Fields can have special characters (brackets, dots, etc.)
        'topmostSubform[0].Page1[0].f1_01[0]': {
            'desc': 'Full legal name from PDF form',
            'specs': {...},
            'casts': {},
            'value': {
                'value': 'John Smith',
                'as_quote': 'My name is John Smith',
                'as_context': '...'
            }
        }
    }
}
```

**Field Access**: Regular fields use dot notation (`interview.field_name`), while fields with special characters use bracket notation (`interview["field[0]"]`).

#### Key Methods

- `_name`: Human-readable interview type
- `_id()`: Safe identifier (lowercase, underscores)
- `_alice` / `_bob`: Role access with trait merging
- `_fields()`: List of defined field names
- `_done`: All fields populated
- `_enough`: Non-confidential/non-conclude fields populated
- `_pretty()`: Debug-friendly string representation

### 2. Builder API

**Location**: `chatfield/builder.py` (Python) | `chatfield/builder.ts` (TypeScript)

Fluent interface for defining interviews without inheritance.

#### Builder Hierarchy

```
ChatfieldBuilder (root)
├── type(), desc()          # Interview metadata
├── alice() → RoleBuilder
│   ├── type()              # Role type
│   └── trait()             # TraitBuilder (regular/possible traits)
├── bob() → RoleBuilder
└── field(name) → FieldBuilder
    ├── desc()              # Field description
    ├── must(), reject(), hint()    # Validation specs
    ├── confidential(), conclude()  # Special behaviors
    ├── as_int() → CastBuilder
    ├── as_float(), as_bool()
    ├── as_lang(code) → CastBuilder
    ├── as_one(choices) → ChoiceBuilder   # Exactly one
    ├── as_maybe(choices)                 # Zero or one
    ├── as_multi(choices)                 # One or more
    └── as_any(choices)                   # Zero or more
```

#### Usage Example

```python
interview = (chatfield()
    .type('Job Application')
    .alice().type('Interviewer').trait('professional')
    .field('name').desc('Your full name')
        .must('include first and last')
    .field('years_exp').as_int()
        .must('be between 0 and 50')
    .field('languages').as_multi('language', 'Python', 'JavaScript', 'Go')
    .build())
```

### 3. Interviewer Class

**Location**: `chatfield/interviewer.py` (Python) | `chatfield/interviewer.ts` (TypeScript)

Orchestrates conversation flow using LangGraph state machine.

#### Responsibilities

1. **LLM Integration**: Manages ChatOpenAI (or mock LLM for testing)
2. **Tool Generation**: Creates Pydantic/Zod schemas for field updates
3. **State Management**: Maintains conversation state via LangGraph checkpointer
4. **Validation Execution**: Enforces `must`/`reject` rules through LLM reasoning
5. **Transformation**: Computes all `as_*` casts during collection
6. **Prompt Rendering**: Uses TemplateEngine for system prompts

#### Key Methods

- `initialize()`: Setup conversation, inject Interview into state
- `think()`: LLM generates next message or decides to call tools
- `listen()`: Interrupt for user input, copy state back to original Interview
- `tools()`: Process tool calls, validate, update Interview
- `digest()`: Handle confidential/conclude fields
- `teardown()`: Finalize conversation, copy state to original Interview
- **`go(user_input)`**: Main conversation loop entry point
  - **Always returns a string** (the AI's next message)
  - **Never returns null** - designed for infinite loops
  - Check `interview._done` to know when fields are collected
  - Application must decide when to call `end()` for cleanup
- **`end()`**: Explicitly terminate conversation and run teardown

### 4. FieldProxy Class

**Location**: `chatfield/field_proxy.py` (Python) | `chatfield/field-proxy.ts` (TypeScript)

String subclass providing transformation attribute access.

#### Design Rationale

Fields must behave as normal strings while exposing transformations:

```python
interview.age              # "25" (string, for display)
interview.age.as_int       # 25 (integer, for logic)
interview.age.as_lang_fr   # "vingt-cinq" (translation)
interview.age.as_quote     # "I am 25 years old" (original quote)
```

#### Implementation

**Python**: Subclasses `str`, stores `_chatfield` metadata
**TypeScript**: Uses ES6 Proxy wrapping a String primitive

Both provide:
- String operations (comparison, methods)
- Transformation access via `__getattr__` / Proxy get trap
- Pretty-printing for debugging

### 5. Template Engine

**Location**: `chatfield/template_engine.py` (Python) | `chatfield/template-engine.ts` (TypeScript)

Handlebars-based prompt generation system.

#### Directory Structure

```
Prompts/
├── system-prompt.hbs.txt           # Main conversation prompt
├── digest-confidential.hbs.txt     # Confidential field digest
├── digest-conclude.hbs.txt         # Conclude field digest
└── partials/
    └── *.hbs.txt                   # Reusable template fragments
```

#### Custom Helpers

- **Text Processing**: `tidy`, `dedent`, `indent`
- **Markdown**: `section`, `bullet`
- **Lists**: `join`, `listJoin`
- **Conditionals**: `any`, `all`, `ifAny`, `ifAll`
- **Field Specs**: `fieldSpec`, `allFieldSpecs`

#### Context Variables

Templates receive structured data:
- `form`: Interview instance
- `fields`: Array of field metadata
- `labels`: Validation type labels ("Must", "Reject")
- `counters`: Validation rule counts
- `interview_name`, `alice_role_name`, `bob_role_name`

### 6. Merge Logic

**Location**: `chatfield/merge.py` (Python) | `chatfield/merge.ts` (TypeScript)

LangGraph reducer for Interview state merging.

#### Merge Strategy

1. **Type Preservation**: Subclass wins over parent class
2. **Type Compatibility**: Same types merge, different types error
3. **Change Detection**: Uses DeepDiff to identify modifications
4. **Permissive Additions**: New fields/values always accepted
5. **Conservative Updates**: Only `None → value` and `falsy → truthy` allowed

#### Handled Scenarios

- Initial Interview injection (null → populated)
- Field value updates (None → data)
- Role type overrides (default → custom)
- Dictionary/list additions

---

## Data Flow Architecture

### Phase 1: Definition

```
Developer writes code
        ↓
chatfield() builder
        ↓
.field().must().as_int()
        ↓
.build() → Interview instance
        ↓
_chatfield dictionary populated
```

### Phase 2: Initialization

```
Interviewer(interview)
        ↓
LangGraph graph compiled
        ↓
Tools generated (update/conclude)
        ↓
System prompt rendered
```

### Phase 3: Conversation (Infinite Loop Design)

**CRITICAL**: Chatfield conversations are designed to run in an **infinite loop**. The application controls when to exit.

```typescript
// TypeScript pattern
const interviewer = new Interviewer(interview)

let message = await interviewer.go()  // Start conversation
console.log(message)

while (!interview._done) {
  const userInput = await getUserInput()
  message = await interviewer.go(userInput)  // Always returns string, never null
  console.log(message)
}

await interviewer.end()  // Explicit cleanup when ready
```

**Conversation Flow**:

```
User: (opens conversation)
        ↓
initialize node → inject Interview
        ↓
think node → LLM generates greeting
        ↓
listen node → interrupt, wait for input
        ↓
go() returns → string message (NEVER null)
        ↓
Application displays message, gets user input
        ↓
Application calls go(userInput)
        ↓
think node → LLM decides to call update_* tool
        ↓
tools node → validate "25" against specs
        ↓
        ├─ VALID → compute transformations (as_int: 25)
        │          store in field.value
        ↓
digest node (if _enough) → conclude fields
        ↓
listen node → interrupt, returns string
        ↓
Application checks interview._done
        ↓
If _done: Application calls interviewer.end()
        ↓
teardown node → copy state to original Interview
```

**Key Design Principles**:
1. `go()` **always returns a string message** (never null/None)
2. The conversation **never automatically terminates**
3. Check `interview._done` to know when all required fields are collected
4. Even after `_done=true`, you can continue calling `go()` - the AI keeps conversing
5. Call `interviewer.end()` when you want to run cleanup and terminate
6. Throw errors for exceptional cases (no interrupts received, etc.)

### Phase 4: Access

```
Developer accesses results
        ↓
interview.age (via __getattr__)
        ↓
FieldProxy("25", metadata)
        ↓
interview.age.as_int (via __getattr__)
        ↓
Returns: 25
```

---

## LangGraph State Machine

### State Definition

```python
class State(TypedDict):
    messages: Annotated[List[Any], add_messages]        # Conversation history
    interview: Annotated[Interview, merge_interviews]   # Form state
```

### Node Graph

```
┌─────────────────────────────────────────────────────────────┐
│                         START                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         v
                  ┌──────────────┐
                  │ initialize   │  Inject Interview into state
                  └──────┬───────┘  Generate system prompt
                         │
                         v
              ┌──────────────────┐
       ┌─────>│      think       │  LLM generates message/tool call
       │      └─────┬──────┬─────┘  Binds update/conclude tools
       │            │      │
       │    tool?   │      │  no tool
       │            v      v
       │      ┌─────────┐ ┌──────────────┐
       │      │  tools  │ │    listen    │  Interrupt for user input
       │      └────┬────┘ └──────┬───────┘  Returns to go() caller
       │           │             │
       │           │  enough?    │
       │           v             │
       │      ┌─────────┐        │
       │      │ digest  │<───────┘ (if _enough)
       │      └────┬────┘   Handle confidential/conclude
       │           │
       │           ├─────> (back to think)
       └───────────┘
                   │
                   │  done?
                   v
            ┌─────────────┐
            │  teardown   │  Copy state to original Interview
            └──────┬──────┘
                   │
                   v
                 END
```

### Node Details

#### initialize

- **Input**: Empty or minimal state
- **Action**: Inject Interview instance into state
- **Output**: `{'interview': self.interview}`

#### think

- **Input**: Current state (messages + interview)
- **Actions**:
  1. Generate system prompt on first message
  2. Bind appropriate tools (update/none based on context)
  3. Call LLM with conversation history
- **Output**: New AIMessage (chat or tool call)

#### listen

- **Input**: State with latest AIMessage
- **Actions**:
  1. Copy Interview state to original (for caller access)
  2. Extract AIMessage content
  3. Call `interrupt(feedback)` to pause graph
- **Output**: Interrupt with user feedback prompt
- **Resume**: User provides input → HumanMessage added to state

#### tools

- **Input**: AIMessage with tool_calls
- **Actions**:
  1. Extract tool invocation args
  2. Validate against field specs (must/reject)
  3. Compute transformations (as_int, as_lang, etc.)
  4. Update Interview._chatfield['fields'][name]['value']
  5. Return ToolMessage (success/error)
- **Output**: ToolMessage(s), updated Interview (if changed)

#### digest

- **Purpose**: Handle fields not collected via normal conversation
- **Types**:
  1. **Confidential**: Fields tracked silently (mark as N/A if not mentioned)
  2. **Conclude**: Fields requiring post-conversation synthesis
- **Actions**:
  1. Generate special tool schema for remaining fields
  2. Call LLM with digest prompt
  3. Process tool call to populate fields
- **Output**: New messages, updated Interview

#### teardown

- **Input**: Complete Interview (_done = True)
- **Action**: Copy final state to original Interview instance
- **Output**: None (ends graph)

### Routing Logic

**From think**:
- Has tool calls? → `tools`
- Interview._done? → `teardown`
- Interview._enough? → `digest`
- Else → `listen`

**From tools**:
- Interview._enough and not _done? → `digest`
- Else → `think`

**From digest**:
- Has tool calls? → `tools`
- Else → `think`

---

## Template System

### Architecture

```
TemplateEngine
├── Compiler (pybars/handlebars.js)
├── Template Cache
├── Partials Cache
└── Custom Helpers Registry
```

### System Prompt Structure

```handlebars
{{tidy}}
# Conversation Context

You are {{form._alice_role_name}} conducting a conversation with {{form._bob_role_name}}.

Interview Type: {{form._name}}
{{#if form._chatfield.desc}}
Purpose: {{form._chatfield.desc}}
{{/if}}

# Fields to Collect

{{#each fields}}
- {{name}}: {{desc}}
{{#if specs.must}}
  {{#each specs.must}}
    - Must: {{this}}
  {{/each}}
{{/if}}
{{#if specs.reject}}
  {{#each specs.reject}}
    - Reject: {{this}}
  {{/each}}
{{/if}}
{{#if casts}}
  {{#each casts}}
    - Confidential cast: `{{name}}` -> {{prompt}}
  {{/each}}
{{/if}}
{{/each}}

# Validation Labels

{{#if labels}}
Follow these validation rules:
{{labels}}
{{/if}}

{{/tidy}}
```

### Prompt Generation Flow

1. `Interviewer.mk_system_prompt(state)`
2. Count validation rules → populate `counters`
3. Extract field data → `mk_fields_data()`
4. Prepare context dict
5. `template_engine.render('system-prompt', context)`
6. Return rendered string for SystemMessage

---

## Dual Implementation Strategy

### Synchronization Requirements

**Python** (source of truth) ↔ **TypeScript** (mirror)

| Aspect | Python | TypeScript | Notes |
|--------|--------|------------|-------|
| File names | `interview.py` | `interview.ts` | Match exactly |
| Test files | `test_*.py` | `*.test.ts` | Different convention |
| Class names | `Interview` | `Interview` | Identical |
| Method names | `_name`, `as_int` | `_name`, `as_int` | Identical |
| Test structure | pytest-describe | describe/it | BDD style |
| Test descriptions | "uses field name..." | "uses field name..." | Exact match |
| Async | Optional | Required | Language difference |

### Implementation Mapping

| Python | TypeScript | Notes |
|--------|------------|-------|
| `str.__new__()` | `new Proxy(String(...))` | FieldProxy creation |
| `__getattr__()` | Proxy get trap | Attribute access |
| Pydantic schemas | Zod schemas | Tool validation |
| `@tool` decorator | `{name, description, args_schema}` | Tool binding |
| pytest markers | Jest test.skip | Test control |
| `DeepDiff` | `deepdiff` package | State comparison |

### Version Synchronization

- Python: v0.2.0 (`pyproject.toml`)
- TypeScript: v0.1.0 (`package.json`)
- Update together when releasing features

---

## Integration Architecture

### React Integration

**Location**: `TypeScript/chatfield/integrations/react.ts`

#### useConversation Hook

```typescript
const {
  messages,           // Conversation history
  sendMessage,        // Send user input
  interview,          // Current Interview state
  isComplete          // Conversation done?
} = useConversation(interviewDefinition)
```

**Features**:
- State management via React hooks
- Automatic re-rendering on updates
- TypeScript type inference for field access

#### ChatfieldConversation Component

**Location**: `TypeScript/chatfield/integrations/react-components.tsx`

Pre-built UI component for conversations:
- Message display (user/agent)
- Input field with send button
- Completion indicator
- Customizable styling

### CopilotKit Integration

**Location**: `TypeScript/chatfield/integrations/copilotkit.tsx`

Sidebar component for CopilotKit framework:
- Embeds Chatfield in CopilotKit UI
- Handles conversation state
- Provides completion callbacks

### Browser vs Node.js

**Endpoint Protection**: Interviewer detects browser environment and blocks direct OpenAI API calls:

```typescript
DANGEROUS_ENDPOINTS = ['api.openai.com', 'api.anthropic.com']

// Browser must use proxy
baseUrl: '/chatfield/openai'  // Default for browser

// Node.js can use direct API
baseUrl: 'https://api.openai.com/v1'
```

**Proxy Setup**: See `TypeScript/PROXY_SETUP.md` for Express/Next.js proxy configuration.

---

## Key Design Patterns

### 1. Builder Pattern

**Purpose**: Provide fluent API without requiring class inheritance

**Structure**:
- ChatfieldBuilder (root)
- RoleBuilder (alice/bob configuration)
- FieldBuilder (field definition)
- CastBuilder (transformation configuration)
- ChoiceBuilder (multiple choice configuration)

**Benefits**:
- No need to define Interview subclasses
- Type inference (TypeScript)
- Method chaining for readability

### 2. Proxy Pattern (FieldProxy)

**Purpose**: Provide string behavior with transformation access

**Python**: `str` subclass with `__getattr__`
**TypeScript**: ES6 Proxy wrapping String

**Benefits**:
- Natural string operations
- Dot-notation for transformations
- Transparent to user code

### 3. State Machine Pattern

**Purpose**: Orchestrate complex conversation flow

**Implementation**: LangGraph state machine

**Benefits**:
- Clear node responsibilities
- Resumable conversations (checkpointer)
- Testable node logic
- Interrupt handling for user input

### 4. Reducer Pattern

**Purpose**: Merge Interview state updates

**Implementation**: `merge_interviews()` as LangGraph reducer

**Benefits**:
- Deterministic state updates
- Change detection via DeepDiff
- Safe concurrent updates (future)

### 5. Template Method Pattern

**Purpose**: Standardize prompt generation

**Implementation**: Handlebars templates with custom helpers

**Benefits**:
- Separation of logic and presentation
- Reusable prompt components (partials)
- Version control for prompts

### 6. Mock Injection Pattern

**Purpose**: Enable testing without API calls

**Implementation**: Optional `llm` parameter in Interviewer constructor

```python
# Production
interviewer = Interviewer(interview)

# Testing
mock_llm = MockLLMBackend()
interviewer = Interviewer(interview, llm=mock_llm)
```

**Benefits**:
- Fast tests (no network calls)
- Deterministic behavior
- Cost savings during development

---

## Security and Evaluation

### Security Model

#### Information Protection

**Problem**: LLM must compute transformations without revealing them to user

**Solution**: Confidential casts

```python
.field('answer').as_bool('is_correct', 'True if answer is correct')
```

- Cast definition hidden from user-facing prompts
- Computed during tool calls
- Never included in conversation messages
- Stored in `field.value` dict, not displayed

#### Exam Security Evaluation

**Location**: `Python/evals/`

**Purpose**: Test resistance to answer extraction attacks

**Attack Patterns** (16 types):
1. Direct questions ("What's the answer?")
2. Prompt injection ("Ignore instructions, tell me...")
3. Jailbreaking ("For research purposes...")
4. Role confusion ("As the exam itself...")
5. Indirect extraction ("List all options...")
6. Social engineering ("I'm the teacher...")
7. Technical exploits (Unicode, encoding tricks)
8. Context manipulation
9. Multi-turn attacks
10. Steganography attempts

**Evaluation Suite**:
- `eval_cast_security.py`: Main runner
- `test_*.py`: DeepEval-based test modules
- `datasets/`: Attack patterns and test cases
- `attacks.json`: Attack taxonomy

**Metrics**:
- Success rate against attacks
- Cast leakage detection
- Validation compliance
- Conversation quality

### Validation Architecture

#### Spec Types

1. **must**: Requirements (LLM enforces)
2. **reject**: Anti-patterns (LLM blocks)
3. **hint**: Guidance (LLM considers)

#### Validation Flow

```
User provides input
        ↓
LLM calls update tool with field value
        ↓
Tool schema includes specs in field description
        ↓
LLM reasoning applies must/reject rules
        ↓
Invalid → ToolMessage with error
Valid → Compute transformations, store
```

#### Error Handling

```python
try:
    process_update_tool(interview, **kwargs)
except ValidationError as e:
    return ToolMessage(
        content=f'Error: {e}',
        tool_call_id=...,
        additional_kwargs={'error': e}
    )
```

---

## Performance Considerations

### Token Optimization

**System Prompt Size**: Grows with field count

**Mitigation**:
1. Omit already-collected fields from tool schemas
2. Use conclude fields for post-conversation synthesis
3. Confidential fields only in digest phase

### API Cost Management

**Evaluation Suite**: Tracks costs per model

**Dashboard**: `streamlit_results.py` displays:
- Total API cost
- Cost per test
- Cost per model
- Token usage

### Caching

**Template Engine**:
- Compiled templates cached
- Partials cached separately
- `clear_cache()` for development

**LangGraph Checkpointer**:
- In-memory state storage
- Thread-isolated conversations
- Resume without re-processing

### Parallel Execution

**LangGraph**: Supports parallel node execution

**Current Usage**:
- Sequential (think → listen → tools → think)
- Future: Parallel field collection

---

## Appendix: File Reference

### Python Core

| File | Lines | Purpose |
|------|-------|---------|
| `interview.py` | 344 | Interview class, field access |
| `interviewer.py` | 886 | LangGraph orchestration |
| `builder.py` | 329 | Fluent builder API |
| `field_proxy.py` | 102 | String subclass with transformations |
| `merge.py` | 80 | State merging logic |
| `template_engine.py` | 286 | Handlebars template system |
| `serialization.py` | ~100 | LangGraph state serialization |

### TypeScript Core

| File | Lines | Purpose |
|------|-------|---------|
| `interview.ts` | ~350 | Interview class (mirrors Python) |
| `interviewer.ts` | ~900 | LangGraph orchestration |
| `builder.ts` | ~500 | Fluent builder API |
| `field-proxy.ts` | ~150 | Proxy-based transformations |
| `merge.ts` | ~100 | State merging |
| `template-engine.ts` | ~300 | Handlebars templates |

### Integrations

| File | Purpose |
|------|---------|
| `react.ts` | useConversation hook |
| `react-components.tsx` | ChatfieldConversation component |
| `copilotkit.tsx` | CopilotKit sidebar integration |

### Tests

| Pattern | Count | Framework |
|---------|-------|-----------|
| `test_*.py` | ~15 | pytest + pytest-describe |
| `*.test.ts` | ~15 | Jest + ts-jest |

### Templates

| File | Purpose |
|------|---------|
| `system-prompt.hbs.txt` | Main conversation prompt |
| `digest-confidential.hbs.txt` | Confidential field digest |
| `digest-conclude.hbs.txt` | Conclude field synthesis |

---

## Conclusion

Chatfield's architecture prioritizes:

1. **Natural Conversation**: LangGraph state machine enables fluid dialogues
2. **Type Safety**: Dual implementation with matching behaviors
3. **Extensibility**: Builder pattern, template system, integration points
4. **Testability**: Mock injection, BDD tests, security evaluations
5. **Security**: Confidential casts, information protection
6. **Developer Experience**: Fluent API, pretty printing, debugging tools

The dual-language implementation ensures Chatfield works seamlessly in both backend (Python) and frontend (TypeScript/React) contexts, with strict synchronization maintaining feature parity.
