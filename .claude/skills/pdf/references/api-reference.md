# Conversational Form API Reference

**Library:** `chatfield` Python package

API reference for building conversational form interviews. Powered by the Chatfield library.

## Contents
- Quick Start
- Builder API
  - Interview Configuration
  - Roles
  - Fields
  - Validation
  - Special Field Types
  - Transformations
  - Cardinality
- Running Interviews
- Field Access
- Optional Fields
- API Configuration
- Next Steps

---

## Quick Start

```python
from chatfield import chatfield, Interviewer

# Define
interview = (chatfield()
    .field("name")
        .desc("What is your full name?")
        .must("include first and last")
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
print(interview.name, interview.age.as_int)
```

---

## Builder API

### Interview Configuration

```python
interview = (chatfield()
    .type("Job Application")            # Interview type
    .desc("Collect applicant info")     # Description
    .build())
```

### Roles

```python
.alice()                                # Configure AI assistant
    .type("Tax Assistant")
    .trait("Professional and accurate")
    .trait("Never provides tax advice")

.bob()                                  # Configure user
    .type("Taxpayer")
    .trait("Speaks colloquially")
```

### Fields

```python
.field("email")                         # Define field (becomes interview.email)
    .desc("What is your email?")        # User-facing question
```

**All fields mandatory to populate** (must be non-`None` for `._done`). Content can be empty string `""`.
Exception: `.as_one()`, `.as_multi()`, and fields with strict validation require non-empty values.

### Validation

```python
.field("email")
    .must("be valid email format")      # Requirement (AND logic)
    .must("not be disposable")
    .reject("profanity")                # Block pattern
    .hint("user@example.com format")    # Advisory (not enforced)
```

### Special Field Types

```python
.field("sentiment_score")
    .confidential()                     # Track silently, never ask Bob

.field("summary")
    .conclude()                         # Compute after regular fields (auto-confidential)
```

### Transformations

LLM computes during collection. Access via `interview.field.as_*`

```python
.field("age").as_int()                  # → interview.age.as_int = 25
.field("price").as_float()              # → interview.price.as_float = 99.99
.field("citizen").as_bool()             # → interview.citizen.as_bool = True
.field("hobbies").as_list()             # → interview.hobbies.as_list = ["reading", "coding"]
.field("config").as_json()              # → interview.config.as_json = {"theme": "dark"}
.field("progress").as_percent()         # → interview.progress.as_percent = 0.75
.field("greeting").as_lang("fr")        # → interview.greeting.as_lang_fr = "Bonjour"

# Optional descriptions guide edge cases
.field("has_partners")
    .as_bool("true if you have partners; false if not or N/A")

.field("zip")
    .as_int("parse 5-digit ZIP, ignore +4 extension")

# Named string casts for formatting
.field("ssn")
    .must("be exactly 9 digits")
    .as_str("formatted", "Format as ###-##-####")
# Access: interview.ssn.as_str_formatted → "123-45-6789"
```

**Validation vs. Casts:**
- **Validation** (`.must()`): Check content ("9 digits", "valid email")
- **Casts** (`.as_*()`): Provide format (hyphens, capitalization)

### Choice Cardinality

Select from predefined options:

```python
.field("tax_class")
    .as_one("Individual", "C Corp", "S Corp")       # Exactly one choice required

.field("dietary")
    .as_nullable_one("Vegetarian", "Vegan")         # Zero or one

.field("languages")
    .as_multi("Python", "JavaScript", "Go")         # One or more choices required

.field("interests")
    .as_nullable_multi("ML", "Web Dev", "DevOps")   # Zero or more
```

### Build

```python
.build()                                # Return Interview instance
```

---

## Running Interviews

```python
interviewer = Interviewer(interview)
user_input = None
while not interview._done:
    message = interviewer.go(user_input)
    print(f"Assistant: {message}")
    if not interview._done:
        user_input = input("You: ").strip()
```

**Interview properties:**
- `interview._done` - All fields collected
- `interview._enough` - Non-confidential/conclude fields collected
- `interview.field_name` - Field value (FieldProxy string)
- `interview.field_name.as_*` - Transformations
- `interview["field[0].name"]` - Bracket notation for special chars

---

## Field Access

**Dot notation** (regular fields):
```python
interview.name
interview.age.as_int
```

**Bracket notation** (special characters):
```python
interview["topmostSubform[0].Page1[0].f1_01[0]"]    # PDF form fields
interview["user.name"]                               # Dots
interview["full name"]                               # Spaces
interview["class"]                                   # Reserved words
```

---

## Optional Fields

Fields known to be optional (from PDF tooltip, nearby context, or instructions):

```python
.alice()
    .trait("Records optional fields as empty string when user says blank/none/skip")

.field("middle_name")
    .desc("Middle name")
    .hint("Background: Optional per form instructions")

.field("extension")
    .desc("Phone extension")
    .hint("Background: Leave blank if none")
```

For optional **choices**, use `.as_nullable_one()` or `.as_nullable_multi()` (see examples above).

---

## API Configuration

```python
# Environment variable (default)
interviewer = Interviewer(interview)

# Explicit API key
interviewer = Interviewer(interview, api_key='your-key')

# Custom base URL (LiteLLM proxy)
interviewer = Interviewer(
    interview,
    api_key='your-key',
    base_url='https://my-proxy.com/v1'
)
```

---

## Next Steps

- **PDF forms:** ../SKILL.md for PDF workflow
