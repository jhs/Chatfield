# Builder API Reference

## Overview

Both Python and TypeScript implementations use a fluent builder pattern as the primary API for defining interviews. The builder provides method chaining for readable, declarative interview definitions.

## Basic Usage

### Python

```python
from chatfield import chatfield

interview = (chatfield()
    .type("Contact Form")
    .desc("Collect contact information")
    .field("name")
        .desc("Your full name")
        .must("include first and last")
        .hint("Format: First Last")
    .field("email")
        .desc("Email address")
        .must("be valid email format")
    .field("age")
        .desc("Your age")
        .as_int()
        .must("be between 18 and 120")
    .build())

# After collection
interview.name        # string value
interview.age         # string (access .as_int for integer)
interview.age.as_int  # 25 (transformed to integer)
```

### TypeScript

```typescript
import { chatfield } from '@chatfield/core'

const interview = chatfield()
  .type('Contact Form')
  .desc('Collect contact information')
  .field('name')
    .desc('Your full name')
    .must('include first and last')
    .hint('Format: First Last')
  .field('email')
    .desc('Email address')
    .must('be valid email format')
    .as_string()  // Explicit type
  .field('age')
    .desc('Your age')
    .as_int()
    .must('be between 18 and 120')
  .build()

// After collection
const result = await Interviewer.go()
result.name        // string
result.age         // number (transformed)
```

## Builder Methods

### Interview Configuration

- `.type(name)`: Set the interview type/title
- `.desc(description)`: Set the interview description
- `.alice()`: Configure the interviewer role (returns RoleBuilder)
  - `.type(role_type)`: Set the role type
  - `.trait(trait)`: Add a personality trait
  - `.trait.apply(trait)`: Add trait that always applies
- `.bob()`: Configure the interviewee role (returns RoleBuilder)
  - `.type(role_type)`: Set the role type
  - `.trait(trait)`: Add a personality trait
  - `.trait.apply(trait)`: Add trait that always applies

### Field Definition

- `.field(name)`: Define a new field to collect
  - `name`: Field identifier (required)
- `.desc(description)`: Set the field description (user-facing prompt)

### Field Naming and Special Characters

Field names can contain any characters including brackets, dots, spaces, and reserved words. Use **bracket notation** to access fields with special characters:

**Python**:
```python
# PDF form fields with complex hierarchical names
interview["topmostSubform[0].Page1[0].f1_01[0]"]
interview["user.name"]
interview["full name"]
interview["class"]  # Reserved words work with bracket notation
```

**TypeScript**:
```typescript
// Same bracket notation syntax
interview["topmostSubform[0].Page1[0].f1_01[0]"]
interview["user.name"]
interview["full name"]
interview["class"]  // Reserved words work with bracket notation
```

**Regular fields** (alphanumeric + underscores) can use dot notation:
```python
interview.age        # Python
interview.age        # TypeScript
```

**PDF forms** commonly use hierarchical names with brackets - always use bracket notation for these.

### Field Validation

- `.must(requirement)`: Add a requirement the response must meet
- `.reject(pattern)`: Add a pattern to avoid in responses
- `.hint(guidance)`: Add guidance shown to the user

### Type Transformations

- `.as_int()`: Parse response to integer
- `.as_float()`: Parse response to float
- `.as_bool()`: Parse response to boolean
- `.as_list()`: Parse response to list/array
- `.as_json()`: Parse response as JSON object
- `.as_percent()`: Parse response to 0.0-1.0 range
- `.as_string()`: Explicit string type (TypeScript)
- `.as_lang(code)`: Translate to language code (e.g., 'fr', 'es')

### Choice Cardinality

- `.as_one(choices)`: Choose exactly one option from choices
- `.as_maybe(choices)`: Choose zero or one option from choices
- `.as_multi(choices)`: Choose one or more options from choices
- `.as_any(choices)`: Choose zero or more options from choices

### Field Lifecycle Control

- `.confidential()`: Mark field as confidential - tracked silently without asking user directly
- `.conclude()`: Mark field for post-conversation synthesis (automatically sets confidential)

#### Confidential Fields

Confidential fields are collected silently during conversation without explicit questions:

**Python**:
```python
interview = (chatfield()
    .field("salary_expectation")
        .desc("Salary expectations")  # Asked explicitly
    .field("actual_budget")
        .desc("Company's actual budget for this role")
        .confidential()  # NOT asked - derived from conversation context
    .build())
```

**Use cases**:
- Assessment fields evaluated from conversation (politeness, enthusiasm)
- Internal categorizations not shown to user
- Derived insights from explicit answers

**Behavior**:
- Excluded from `._enough` calculation
- When `._enough` becomes true, confidential fields are auto-processed
- Fields not mentioned in conversation get marked as N/A

#### Conclude Fields

Conclude fields are synthesized after the main conversation completes, perfect for deriving structured data:

**Python**:
```python
interview = (chatfield()
    # Master field - conversational
    .field("social_security_number")
        .desc("What is your Social Security Number?")
        .must("be a valid 9-digit SSN")

    # Conclude fields - derived from master
    .field("ssn_part1")
        .desc("First 3 digits of social_security_number")
        .conclude()

    .field("ssn_part2")
        .desc("Middle 2 digits of social_security_number")
        .conclude()

    .field("ssn_part3")
        .desc("Last 4 digits of social_security_number")
        .conclude()
    .build())
```

**Use cases**:
- Splitting one input into multiple fields (SSN → 3 parts, name → first/middle/last)
- Mapping choices to multiple checkboxes (one classification → 7 boolean fields)
- Format transformations (full address → street + city/state/zip)
- Post-conversation assessments combining multiple inputs

**Behavior**:
- Automatically sets `.confidential()` (conclude fields are always confidential)
- Excluded from `._enough` calculation
- When `._enough` is true, conclude fields are auto-synthesized in one pass
- All conclude fields can use `.as_int()`, `.as_bool()`, `.as_one()`, etc.
- Required fields in tool schema - LLM must populate all of them

**Execution order**:
1. Regular fields collected → `._enough` becomes true
2. Confidential fields processed first
3. Conclude fields synthesized second
4. All fields populated → `._done` becomes true

**PDF form example**:
```python
# One master question
.field("tax_classification")
    .desc("What is your tax classification?")
    .as_one("Individual", "C Corp", "S Corp", "Partnership", "Trust/Estate", "LLC", "Other")

# Seven conclude fields mapping to PDF checkboxes
.field("pdf_checkbox_individual")
    .desc("True if tax_classification is 'Individual', else false")
    .conclude()
    .as_bool()

.field("pdf_checkbox_ccorp")
    .desc("True if tax_classification is 'C Corp', else false")
    .conclude()
    .as_bool()

# ... 5 more conclude fields for remaining options
```

This pattern enables natural conversation while automatically populating technical PDF field requirements.

### Build

- `.build()`: Complete the builder and return an Interview instance

## Field Value Access

### Python

```python
# During definition
interview = (chatfield()
    .field("age")
        .desc("Your age")
        .must("be specific")
        .as_int()
        .as_lang("fr")
    .build())

# After collection (via FieldProxy)
interview.age              # "25" (base string value)
interview.age.as_int       # 25 (integer)
interview.age.as_lang_fr   # "vingt-cinq" (French translation)
interview.age.as_quote     # "I am 25 years old" (original quote)
interview.age.as_context   # Full conversation context
```

### TypeScript

```typescript
// After collection
interview.age              // number (if as_int() was used)
const field = interview.getField('age')
field.asQuote              // Original quote
field.asContext            // Conversational context
```

## Complete Example

### Python

```python
interview = (chatfield()
    .alice()
        .type("Interviewer")
        .trait("friendly and professional")
    .bob()
        .type("Job Candidate")
    .field("desired_position")
        .desc("What position are you applying for?")
        .must("include company name")
        .must("mention specific role")
    .field("years_experience")
        .desc("Years of relevant experience")
        .as_int()
        .must("be realistic number")
    .field("languages")
        .desc("Programming languages you know")
        .as_multi(["Python", "JavaScript", "Go", "Rust"])
    .build())
```

### TypeScript

```typescript
const interview = chatfield()
  .alice()
    .type('Interviewer')
    .trait('friendly and professional')
  .bob()
    .type('Job Candidate')
  .field('desiredPosition')
    .desc('What position are you applying for?')
    .must('include company name')
    .must('mention specific role')
  .field('yearsExperience')
    .desc('Years of relevant experience')
    .as_int()
    .must('be realistic number')
  .field('languages')
    .desc('Programming languages you know')
    .as_multi(['Python', 'JavaScript', 'Go', 'Rust'])
  .build()
```

## Notes

- All transformations are computed by the LLM during collection, not post-processing
- Validation rules (must, reject, hint) are enforced by the LLM
- Field order determines conversation flow
- See `Documentation/Architecture.md` for internal structure details
