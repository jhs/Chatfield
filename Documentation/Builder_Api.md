# Builder API Reference

## Overview

Both Python and TypeScript implementations use a fluent builder pattern as the primary API for defining interviews. The builder provides method chaining for readable, declarative interview definitions.

## Basic Usage

### Python

```python
from chatfield import chatfield

interview = chatfield()\
    .type("Contact Form")\
    .desc("Collect contact information")\
    .field("name")\
        .desc("Your full name")\
        .must("include first and last")\
        .hint("Format: First Last")\
    .field("email")\
        .desc("Email address")\
        .must("be valid email format")\
    .field("age")\
        .desc("Your age")\
        .as_int()\
        .must("be between 18 and 120")\
    .build()

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
  - `.trait.possible(key, condition)`: Add conditional trait
- `.bob()`: Configure the interviewee role (returns RoleBuilder)
  - `.type(role_type)`: Set the role type
  - `.trait(trait)`: Add a personality trait
  - `.trait.apply(trait)`: Add trait that always applies
  - `.trait.possible(key, condition)`: Add conditional trait

### Field Definition

- `.field(name)`: Define a new field to collect
  - `name`: Field identifier (required)
- `.desc(description)`: Set the field description (user-facing prompt)

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

### Build

- `.build()`: Complete the builder and return an Interview instance

## Field Value Access

### Python

```python
# During definition
interview = chatfield()\
    .field("age")\
    .desc("Your age")\
    .must("be specific")\
    .as_int()\
    .as_lang("fr")\
    .build()

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
interview = chatfield()\
    .alice()\
        .type("Interviewer")\
        .trait("friendly and professional")\
    .bob()\
        .type("Job Candidate")\
    .field("desired_position")\
        .desc("What position are you applying for?")\
        .must("include company name")\
        .must("mention specific role")\
    .field("years_experience")\
        .desc("Years of relevant experience")\
        .as_int()\
        .must("be realistic number")\
    .field("languages")\
        .desc("Programming languages you know")\
        .as_multi(["Python", "JavaScript", "Go", "Rust"])\
    .build()
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
