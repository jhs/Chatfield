# Chatfield API Reference

## What is Chatfield?

Chatfield transforms rigid forms into natural, LLM-powered conversations. Instead of traditional form fields, you collect structured data through intelligent dialogue.

**Location**: `/home/dev/src/Chatfield/Python`

## Core Concepts

**Interview**: Defines what to collect (fields), how to validate (specs), how to transform (casts), and participant roles (alice/bob).

**Field**: Single data item with name, description, validation rules, and transformations.

**Interviewer**: Orchestrates conversation, manages LLM, validates responses, computes transformations, provides `go()` method.

**Field Values**: After collection, fields act as strings but provide transformation access:
```python
interview.age              # "25" (string)
interview.age.as_int       # 25 (integer)
interview.age.as_float     # 25.0 (float)
interview.age.as_quote     # Original quote
```

## Quick Start

```python
from chatfield import chatfield, Interviewer

# Define
interview = (chatfield()
    .field("name")
        .desc("What is your full name?")
        .must("include first and last")
    .field("email")
        .desc("Email address?")
        .must("be valid email format")
    .field("age")
        .desc("Your age?")
        .as_int()
        .must("be between 18 and 120")
    .build())

# Run
interviewer = Interviewer(interview)
user_input = None
while not interview._done:
    message = interviewer.go(user_input)
    print(f"Assistant: {message}")
    if not interview._done:
        user_input = input("You: ").strip()

# Access
print(interview.name, interview.email, interview.age.as_int)
```

## Builder API

### Interview Configuration

**`.type(name: str)`** - Set interview type/title (appears in prompts)
**`.desc(description: str)`** - Set interview description/purpose

```python
interview = (chatfield()
    .type("Job Application")
    .desc("Collect applicant information")
    .build())
```

### Roles

**`.alice()`** - Configure interviewer (AI assistant). Returns RoleBuilder.
**`.bob()`** - Configure interviewee (user). Returns RoleBuilder.

RoleBuilder methods:
- **`.type(role_type: str)`** - Set role type
- **`.trait(trait: str)`** - Add personality trait

```python
.alice().type("Tax Assistant").trait("professional").trait("never provides tax advice")
.bob().type("Taxpayer")
```

### Fields

**`.field(name: str)`** - Define field to collect. Returns FieldBuilder. Names become Interview attributes.
**`.desc(description: str)`** - User-facing question/prompt.

```python
.field("email").desc("What is your email address?")
```

### Validation Specifications

**`.must(requirement: str)`** - Requirement LLM enforces (AND logic for multiple)
**`.reject(pattern: str)`** - Pattern LLM blocks
**`.hint(guidance: str)`** - Advisory guidance (not enforced)
**`.confidential()`** - Track silently, don't ask (use for: sentiment, scores)
**`.conclude()`** - Compute after other fields (use for: summaries, recommendations)

```python
# Example field definitions
    .field("email")
        .must("be valid email format")
        .must("not be temporary/disposable")
        .reject("profanity")

    .field("tax_classification")
        .hint("Most individuals select 'Individual/sole proprietor'")

    .field("internal_score")
        .confidential()  # Tracked silently

    .field("summary")
        .conclude()  # Computed post-conversation
```

### Transformations

LLM computes transformations **during** collection. Access via `interview.field.as_*`

**`.as_int()`** - Parse to integer
**`.as_float()`** - Parse to float
**`.as_bool()`** - Parse to boolean
**`.as_list()`** - Parse to list/array/set
**`.as_json()`** - Parse as JSON object
**`.as_percent()`** - Parse to 0.0-1.0 range
**`.as_lang(code)`** - Translate to language (ISO 639-1 or other guidance) e.g. fr, zh, SQL, Python, etc.

```python
.field("age").as_int()              # interview.age.as_int → 25
.field("salary").as_float()         # interview.salary.as_float → 75000.0
.field("is_citizen").as_bool()      # interview.is_citizen.as_bool → True
.field("hobbies").as_list()         # interview.hobbies.as_list → ["reading", "swimming"]
.field("prefs").as_json()           # interview.prefs.as_json → {"theme": "dark"}
.field("completion").as_percent()   # interview.completion.as_percent → 0.75
.field("greeting")                  # Multiple translations
    .as_lang("fr")
    .as_lang("es")
    .as_lang("Python print() statement")
```

### Choice Cardinality

**`.as_one(*choices)`** - Exactly one (required)
**`.as_maybe(*choices)`** - Zero or one (optional)
**`.as_multi(*choices)`** - One or more (at least one required)
**`.as_any(*choices)`** - Zero or more (all optional)

```python
.field("tax_class")
    .as_one("Individual", "C Corp", "S Corp", "Partnership")
.field("dietary")
    .as_maybe("Vegetarian", "Vegan", "Gluten-free", "None")
.field("languages")
    .as_multi("Python", "JavaScript", "Go", "Rust")
.field("interests")
    .as_any("ML", "Web Dev", "DevOps", "Security")
```

### Build

**`.build()`** - Complete builder, return Interview instance

```python
interview = (chatfield()
    .field("name")
        .desc("Name?")
    .build())
```

## Running Interviews

**Interviewer Constructor**:
```python
Interviewer(interview)
```

**Conversation Loop**:
```python
interviewer = Interviewer(interview)
user_input = None
while not interview._done:
    message = interviewer.go(user_input)  # Always returns string
    print(f"Assistant: {message}")
    if not interview._done:
        user_input = input("You: ").strip()
```

**Interview Properties**:
- `interview._done` - All fields collected
- `interview._enough` - Non-confidential/conclude fields collected
- `interview._name` - Interview type
- `interview._fields()` - Field names list
- `interview._alice` / `interview._bob` - Role configs
- `interview._pretty()` - Debug representation
- `interview.field_name` - Field access
- `interview.field_name.as_*` - Transformations

## Best Practices

1. **Clear descriptions**: `.desc("What is your Social Security Number?")` not `.desc("SSN?")`
2. **Add validation**: `.must("be valid email").reject("temporary emails")`
3. **Helpful hints**: `.hint("5-digit ZIP or ZIP+4 format")`
4. **Appropriate transforms**: Numbers→`.as_int()`, Booleans→`.as_bool()`, Choices→`.as_one()`
5. **Configure roles**: `.alice().type("Assistant").trait("professional")`
6. **Order fields logically**: Prerequisites first (natural skip if not applicable)
7. **Special fields**: `.confidential()` for tracking, `.conclude()` for post-conversation synthesis

## Troubleshooting

**Field access before collection**: Evaluates to None (check `interview._done`)
**Special char field names**: Use `getattr(interview, "field[0].name", None)` (but avoid defining these)
**Validation issues**: Adjust `.must()`/`.reject()` specificity
**LLM handles validation**: Invalid input prompts clarification automatically

## Next Steps

- **PDF forms**: See ./forms.md for PDF form filling workflow with Chatfield
- **Architecture**: /home/dev/src/Chatfield/Documentation/Architecture.md
- **Examples**: /home/dev/src/Chatfield/Python/examples/