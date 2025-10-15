# Chatfield Prompt System Architecture

## Overview

Chatfield uses a sophisticated template-based prompt generation system built on Handlebars. This document details the prompt architecture, template structure, and how prompts adapt to different interview configurations.

## Table of Contents

1. [Template Engine Architecture](#template-engine-architecture)
2. [Prompt Templates](#prompt-templates)
3. [System Prompt Structure](#system-prompt-structure)
4. [Digest Prompts](#digest-prompts)
5. [Custom Helpers](#custom-helpers)
6. [Prompt Generation Flow](#prompt-generation-flow)
7. [Context Variables](#context-variables)
8. [Best Practices](#best-practices)

---

## Template Engine Architecture

### Location

- **Python**: `chatfield/template_engine.py`
- **TypeScript**: `chatfield/template-engine.ts`
- **Templates**: `Prompts/*.hbs.txt`
- **Partials**: `Prompts/partials/*.hbs.txt`

### Core Components

```
TemplateEngine
├── Compiler (pybars/handlebars.js)
├── Template Cache: Map<string, CompiledTemplate>
├── Partials Cache: Map<string, CompiledTemplate>
└── Helpers Registry: Map<string, Function>
```

### Initialization

```python
class TemplateEngine:
    def __init__(self, templates_dir: Optional[Path] = None):
        # Default to /Prompts at project root
        self.templates_dir = templates_dir or Path(__file__).parent.parent.parent / "Prompts"
        self.compiler = pybars.Compiler()
        self._template_cache = {}
        self._partials_cache = {}

        self._register_helpers()
        self._load_partials()
```

### Template Loading

1. **On-demand**: Templates loaded when first requested
2. **Caching**: Compiled templates cached for performance
3. **Partials**: All partials loaded at initialization
4. **Development**: Call `clear_cache()` to reload templates

---

## Prompt Templates

### Template Files

```
Prompts/
├── system-prompt.hbs.txt          # Main conversation prompt
├── digest-confidential.hbs.txt    # Confidential field handling
├── digest-conclude.hbs.txt        # Post-conversation synthesis
└── partials/
    ├── field-list.hbs.txt         # Reusable field rendering
    ├── validation-rules.hbs.txt   # Reusable validation display
    └── role-info.hbs.txt          # Reusable role description
```

### Template Naming Convention

- **Extension**: `.hbs.txt` (prevents IDEs from auto-formatting)
- **Naming**: Kebab-case (e.g., `system-prompt`, `digest-conclude`)
- **Partials**: No special prefix, just in `partials/` directory

### Usage

```python
# Render a template
rendered = template_engine.render('system-prompt', context)

# Context is a dictionary of variables
context = {
    'form': interview,
    'fields': fields_data,
    'labels': '"Must" and "Reject"',
    'counters': {'must': 5, 'reject': 2, 'hint': 1}
}
```

---

## System Prompt Structure

### Purpose

The system prompt instructs the LLM on:
1. Role and personality (alice/bob)
2. Interview type and purpose
3. Fields to collect with descriptions
4. Validation rules (must/reject/hint)
5. Confidential transformations (casts)
6. Conversation guidelines

### Template Anatomy

```handlebars
{{!-- system-prompt.hbs.txt --}}
{{tidy}}

# Role and Context

You are **{{form._alice_role_name}}** ({{form._alice_oneliner}}) conducting a conversation with **{{form._bob_role_name}}** ({{form._bob_oneliner}}).

**Interview Type**: {{form._name}}
{{#if form._chatfield.desc}}
**Purpose**: {{form._chatfield.desc}}
{{/if}}

# Fields to Collect

The following information must be gathered from the {{form._bob_role_name}} through natural conversation:

{{#each fields}}
## {{name}}

{{#if desc}}
**Description**: {{desc}}
{{/if}}

{{#if specs.must}}
**Must**:
{{#each specs.must}}
- {{this}}
{{/each}}
{{/if}}

{{#if specs.reject}}
**Reject**:
{{#each specs.reject}}
- {{this}}
{{/each}}
{{/if}}

{{#if specs.hint}}
**Hints**:
{{#each specs.hint}}
- {{this}}
{{/each}}
{{/if}}

{{#if specs.confidential}}
⚠️ **Confidential**: Do not ask about this directly. Only record if the {{../form._bob_role_name}} volunteers this information.
{{/if}}

{{#if casts}}
**Transformations** (confidential, do NOT mention):
{{#each casts}}
- `{{name}}`: {{prompt}}
{{/each}}
{{/if}}

{{/each}}

# Guidelines

1. **Natural Conversation**: Engage naturally, don't interrogate
2. **One Topic at a Time**: Don't ask about multiple fields simultaneously
3. **Validation**: Ensure responses meet all "Must" requirements
4. **Rejection**: Politely redirect if response matches "Reject" patterns
5. **Confidential Fields**: Track silently if volunteered, never ask directly
6. **Transformations**: Compute internally, never reveal to user

{{#if labels}}
# Validation Labels

This interview uses {{labels}} validation rules. Strictly enforce all requirements.
{{/if}}

{{/tidy}}
```

### Generated Example

For a job application interview:

```markdown
# Role and Context

You are **Hiring Manager** (Interviewer, professional and friendly) conducting a conversation with **Job Candidate** (User).

**Interview Type**: Job Application
**Purpose**: Collect information about job candidates

# Fields to Collect

The following information must be gathered from the Job Candidate through natural conversation:

## position

**Description**: What position are you applying for?

**Must**:
- include the specific role and department
- mention the company name

**Reject**:
- vague or generic answers

## years_experience

**Description**: Years of relevant experience

**Transformations** (confidential, do NOT mention):
- `as_int`: Parse as integer

**Must**:
- be a realistic number between 0 and 50

## languages

**Description**: Programming languages you know

**Transformations** (confidential, do NOT mention):
- `as_multi_language`: Choose one or more from: Python, JavaScript, Go, Rust

# Guidelines

1. **Natural Conversation**: Engage naturally, don't interrogate
2. **One Topic at a Time**: Don't ask about multiple fields simultaneously
3. **Validation**: Ensure responses meet all "Must" requirements
4. **Rejection**: Politely redirect if response matches "Reject" patterns
5. **Confidential Fields**: Track silently if volunteered, never ask directly
6. **Transformations**: Compute internally, never reveal to user

# Validation Labels

This interview uses "Must" and "Reject" validation rules. Strictly enforce all requirements.
```

---

## Digest Prompts

### Confidential Digest

**File**: `digest-confidential.hbs.txt`

**Purpose**: Handle confidential fields that weren't mentioned in conversation

**When**: After `_enough` is true but before `_done`

**Behavior**: Mark unmentioned confidential fields as N/A or synthesize from context

```handlebars
{{tidy}}

# Confidential Field Digest

The conversation is progressing well. Some confidential fields have not been explicitly discussed yet.

**Your Task**: For each field below, determine if the {{bob_role_name}} has implicitly provided or hinted at this information during the conversation. If so, extract it. If not, mark it as "N/A" or provide a reasonable default.

## Confidential Fields

{{#each fields}}
- **{{name}}**: {{desc}}
{{/each}}

**Important**:
- Do NOT ask the {{bob_role_name}} about these fields
- Only extract if information was volunteered
- Mark as "N/A" if not discussed
- Use conversation context to infer if appropriate

{{/tidy}}
```

### Conclude Digest

**File**: `digest-conclude.hbs.txt`

**Purpose**: Synthesize conclude fields from full conversation

**When**: After all normal fields collected

**Behavior**: LLM reviews entire conversation and computes summary fields

```handlebars
{{tidy}}

# Conversation Synthesis

The conversation is complete. Now synthesize the following conclude fields based on the entire conversation:

## Fields to Synthesize

{{#each fields}}
### {{name}}

**Description**: {{desc}}

**Guidance**: Review the full conversation with the {{../bob_role_name}} and determine this value through analysis, synthesis, or recall.

{{/each}}

**Important**:
- Base your answers on the complete conversation
- These are analytical/summary fields, not direct user responses
- Provide thoughtful, accurate assessments

{{/tidy}}
```

---

## Custom Helpers

### Text Processing Helpers

#### `tidy`

**Purpose**: Clean up template output while preserving structure

**Behavior**:
1. Dedent (remove common leading whitespace)
2. Strip leading/trailing newlines
3. Join non-blank lines (un-word-wrap)
4. Preserve paragraph breaks (double newlines)
5. Re-indent to specified level

**Usage**:

```handlebars
{{tidy at=1 pre=0 suf=0}}
    This text will be dedented,
    joined into single lines per paragraph,
    and then re-indented to level 1.

    This second paragraph is preserved.
{{/tidy}}
```

**Parameters**:
- `at`: Indentation level (4 spaces per level)
- `pre`: Leading spaces
- `suf`: Trailing spaces

#### `dedent` (disabled in current version)

Removes common leading indentation from text blocks.

#### `indent` (disabled in current version)

Adds consistent indentation to text blocks.

### Markdown Helpers

#### `section`

**Purpose**: Generate markdown headers

**Usage**:

```handlebars
{{section "Field List" 2}}
```

**Output**: `## Field List`

**Parameters**:
- `title`: Section title
- `level`: Header level (1-6)

#### `bullet`

**Purpose**: Generate bullet points with optional indentation

**Usage**:

```handlebars
{{bullet "First item" 0}}
{{bullet "Nested item" 1}}
```

**Output**:
```
- First item
  - Nested item
```

### List Helpers

#### `join` (disabled in current version)

Joins list items with a separator.

#### `listJoin` (disabled in current version)

Joins list items with proper English grammar:
- `["A"]` → "A"
- `["A", "B"]` → "A and B"
- `["A", "B", "C"]` → "A, B and C"

### Conditional Helpers

#### `any`

**Purpose**: Return true if any argument is truthy

**Usage**:

```handlebars
{{#if (any counters.must counters.reject)}}
  Validation rules present
{{/if}}
```

#### `all`

**Purpose**: Return true if all arguments are truthy

**Usage**:

```handlebars
{{#if (all form._done user_confirmed)}}
  Interview complete
{{/if}}
```

#### `ifAny` / `ifAll` (disabled in current version)

Block helpers for conditional rendering based on multiple conditions.

### Field Specification Helpers

#### `fieldSpec` (disabled in current version)

Formats a specific spec type (must/reject/hint) for a field.

#### `allFieldSpecs` (disabled in current version)

Formats all specs for a field with proper labels.

### Debug Helper

#### `debug`

**Purpose**: Print value to console during development

**Usage**:

```handlebars
{{debug counters "Counters"}}
```

**Output** (to console):
```
Debug [Counters]: {
  "must": 5,
  "reject": 2,
  "hint": 1
}
```

---

## Prompt Generation Flow

### System Prompt Generation

```python
def mk_system_prompt(self, state: State) -> str:
    interview = self._get_state_interview(state)

    # Count validation rules
    counters = {'hint': 0, 'must': 0, 'reject': 0}
    fields_data = self.mk_fields_data(interview, counters=counters)

    # Determine validation labels
    labels = None
    has_validation = counters['must'] > 0 or counters['reject'] > 0
    if has_validation:
        if counters['must'] > 0 and counters['reject'] == 0:
            labels = '"Must"'
        elif counters['must'] == 0 and counters['reject'] > 0:
            labels = '"Reject"'
        elif counters['must'] > 0 and counters['reject'] > 0:
            labels = '"Must" and "Reject"'

    # Prepare context
    context = {
        'form': interview,
        'labels': labels,
        'counters': counters,
        'fields': fields_data,
    }

    # Render template
    prompt = self.template_engine.render('system-prompt', context)
    return prompt
```

### Field Data Extraction

```python
def mk_fields_data(self, interview: Interview, mode='normal', field_names=None, counters=None) -> list:
    """Generate structured field data for templates."""
    fields = []

    field_keys = field_names or interview._chatfield['fields'].keys()
    for field_name in field_keys:
        chatfield = interview._chatfield['fields'][field_name]

        # Filter by mode
        if mode == 'normal' and chatfield['specs']['conclude']:
            continue
        if mode == 'conclude' and not chatfield['specs']['conclude']:
            continue

        # Count validation rules
        if counters is not None:
            for spec_name in ('hint', 'must', 'reject'):
                predicates = chatfield['specs'].get(spec_name, [])
                if predicates and isinstance(predicates, list):
                    counters[spec_name] += len(predicates)

        # Extract cast info
        casts = [
            {'name': k, 'prompt': v["prompt"]}
            for k, v in chatfield['casts'].items()
        ]

        fields.append({
            'name': field_name,
            'desc': chatfield.get('desc', ''),
            'casts': casts,
            'specs': chatfield.get('specs', {})
        })

    return fields
```

---

## Context Variables

### Available in Templates

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `form` | Interview | Full Interview instance | `{{form._name}}` |
| `form._name` | string | Interview type | "Job Application" |
| `form._chatfield.desc` | string | Interview description | "Collect candidate info" |
| `form._alice_role_name` | string | Alice role type | "Hiring Manager" |
| `form._bob_role_name` | string | Bob role type | "Job Candidate" |
| `form._alice_oneliner` | string | Alice with traits | "Interviewer (professional)" |
| `form._bob_oneliner` | string | Bob with traits | "User" |
| `fields` | Array | Field metadata objects | See below |
| `labels` | string | Validation labels | '"Must" and "Reject"' |
| `counters` | Object | Validation counts | `{must: 5, reject: 2, hint: 1}` |

### Field Object Structure

```javascript
{
  name: "position",
  desc: "What position are you applying for?",
  specs: {
    must: ["include role and department"],
    reject: ["vague answers"],
    hint: [],
    confidential: false,
    conclude: false
  },
  casts: [
    {
      name: "as_int",
      prompt: "Parse as integer"
    }
  ]
}
```

---

## Best Practices

### 1. Template Organization

**DO**:
- Use partials for reusable components
- Keep templates focused (one purpose per file)
- Use descriptive names (e.g., `digest-confidential` not `digest1`)

**DON'T**:
- Mix concerns in templates
- Hardcode values that should be context variables
- Over-nest conditionals (extract to partials)

### 2. Whitespace Management

**DO**:
- Use `{{tidy}}` helper to clean up output
- Preserve paragraph breaks with double newlines
- Use consistent indentation within templates

**DON'T**:
- Leave trailing spaces
- Mix tabs and spaces
- Assume template whitespace doesn't matter

### 3. Context Design

**DO**:
- Pass structured data (objects/arrays)
- Include helper properties (e.g., `_oneliner`)
- Provide fallback values

**DON'T**:
- Pass raw strings when objects are more flexible
- Assume properties exist (use `{{#if}}`)
- Mutate context in helpers

### 4. Helper Development

**DO**:
- Return strings (not objects) from helpers
- Handle edge cases (empty arrays, null values)
- Provide clear parameter names

**DON'T**:
- Perform side effects in helpers (except `debug`)
- Assume input types (validate)
- Create deeply nested helper calls

### 5. Validation Presentation

**DO**:
- Clearly label validation types (Must, Reject, Hint)
- Explain consequences ("must include..." vs "will be rejected if...")
- Provide examples in hints

**DON'T**:
- Use technical jargon
- Overwhelm with too many rules
- Contradict must/reject rules

### 6. Confidential Information

**DO**:
- Clearly mark confidential fields
- Explain why they're confidential
- Provide guidance on when to record

**DON'T**:
- Mix confidential and non-confidential in prompts
- Reveal cast definitions to users
- Ask users about confidential fields

### 7. Testing Templates

**DO**:
- Test with minimal interviews (1 field)
- Test with complex interviews (10+ fields, all spec types)
- Verify output has no template variables (`{{var}}`)
- Check for proper markdown formatting

**DON'T**:
- Only test with examples
- Skip edge cases (no fields, all confidential, etc.)
- Ignore whitespace issues

### 8. Debugging

**DO**:
- Use `Interviewer.debug_prompt()` to visualize whitespace
- Use `{{debug var "label"}}` during development
- Clear template cache when editing templates

**DON'T**:
- Leave debug helpers in production templates
- Assume caching works (verify in logs)
- Edit templates without reloading

---

## Advanced Topics

### Dynamic Tool Descriptions

Tool schemas include field specs in descriptions:

```python
def llm_update_tool(self, state: State):
    args_schema = {}

    for field_name in interview._fields():
        field_metadata = interview._chatfield['fields'][field_name]
        field_definition = self.mk_field_definition(interview, field_name, field_metadata)
        args_schema[field_name] = Optional[field_definition]

    UpdateToolArgs = create_model('UpdateToolArgs', **args_schema)

    @tool('update_' + interview._id(), args_schema=UpdateToolArgs)
    def wrapper(**kwargs):
        raise Exception('Tool should not run directly')

    return wrapper
```

### Cast Prompts in Tools

Cast prompts become field descriptions in tool schemas:

```python
def mk_field_definition(self, interview: Interview, field_name: str, chatfield: Dict):
    casts_definitions = {}

    for cast_name, cast_info in chatfield['casts'].items():
        cast_type = cast_info['type']  # 'int', 'str', etc.
        cast_prompt = cast_info['prompt']  # "Parse as integer"

        casts_definitions[cast_name] = (
            cast_type,
            Field(description=cast_prompt)
        )

    return create_model(
        field_name,
        value=(str, Field(description=f'Natural value of {field_name}')),
        **casts_definitions
    )
```

### Prompt Debugging

```python
# In Python
prompt = interviewer.mk_system_prompt(state)
visible = Interviewer.debug_prompt(prompt, use_color=True)
print(visible)

# Output shows:
# - Template variables as ⚠{var}⚠ (errors)
# - Newlines as ↵
# - Trailing spaces with yellow background
# - Multiple spaces as ␣␣␣
# - Tabs as →
# - Invisible Unicode as [ZWSP], [NBSP], etc.
```

---

## Conclusion

The Chatfield prompt system provides:

1. **Flexibility**: Templates adapt to interview configuration
2. **Maintainability**: Separate logic from presentation
3. **Reusability**: Partials and helpers reduce duplication
4. **Debuggability**: Visualization tools and caching controls
5. **Security**: Confidential cast handling built into prompts
6. **Consistency**: Same system in Python and TypeScript

By centralizing prompt generation in templates with structured context, Chatfield ensures consistent, high-quality LLM interactions across all interview types.
