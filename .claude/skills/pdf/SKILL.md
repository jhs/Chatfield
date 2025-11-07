---
name: pdf-form-filler
description: Fill PDF forms conversationally through natural dialogue. This skill should be used when filling out PDF forms (fillable or non-fillable) through natural conversation instead of rigid form interfaces. Transforms form completion into LLM-powered dialogues that collect, validate, and populate structured data.
license: Apache 2.0
---

# PDF Form Filler

Fill PDF forms through natural conversation instead of rigid form interfaces.

## When to Use This Skill

Use this skill when filling out PDF forms with user-provided information, whether the PDF has fillable form fields or not.

## Determine Form Type

**Check fillability first:**
```bash
python scripts/check_fillable_fields.py <file.pdf>
```

- **Fillable fields detected** → Follow "Fillable Forms Workflow" below
- **No fillable fields** → See references/nonfillable-forms.md

Both workflows use conversational data collection powered by the Chatfield library.

---

## Fillable Forms Workflow

### Step 1: Extract PDF Content and Field Metadata

**a) Convert PDF to markdown:**
```python
mcp__markitdown__convert_to_markdown(uri="file:///absolute/path/to/input.pdf")
```
Returns markdown content. Analyze directly, do not write to file.

**b) Extract form fields:**
```bash
python scripts/extract_form_field_info.py input.pdf input.form.json
```

Creates JSON with field_id, type (text/checkbox/radio_group/choice), page, rect, tooltip, and type-specific properties.

---

### Step 2: Edit Interview Definition

**Target:** `Python/chatfield/server/interview.py` (EDITABLE ZONE only)

**a) Extract form knowledge from markdown:**

Extract actionable knowledge ONLY:
- Form purpose (1-2 sentences)
- Key term definitions (e.g., "U.S. person", "disregarded entity")
- Field completion instructions
- Valid options/codes
- Decision logic ("If X then Y")

Place in interview:
- **Form-level** → Alice traits: `.trait("Background: Form W-9 collects taxpayer IDs...")`
- **Field-level** → Field hints: `.hint("Background: Individuals use SSN, entities use EIN")`

**b) Write interview using builder API:**

```python
interview = (chatfield()
    .type("FormType")
    .desc("Brief form description")

    .alice()
        .type("Form Assistant")
        .trait("Uses plain language, converts to valid form data")
        .trait("Accepts format variations (SSN with/without hyphens)")
        .trait("Background: [extracted form knowledge]")
    .bob()
        .type("Person completing form")
        .trait("Speaks naturally, needs format help")

    # Default: map directly (one PDF field_id → one question)
    .field("topmostSubform[0].Page1[0].f1_01[0]")
        .desc("What is your full legal name?")
        .hint("Background: Should match tax return exactly per IRS instructions")

    # Split pattern: collect once, split for PDF fields
    .field("ssn")
        .desc("What is your Social Security Number?")
        .as_str("formatted", "9 digits formatted as ###-##-####")
        .hint("Background: Accepts with or without hyphens")
    .field("topmostSubform[0].Page1[0].ssn_1[0]")
        .desc("First 3 digits of ssn")
        .conclude()
    .field("topmostSubform[0].Page1[0].ssn_2[0]")
        .desc("Middle 2 digits of ssn")
        .conclude()
    .field("topmostSubform[0].Page1[0].ssn_3[0]")
        .desc("Last 4 digits of ssn")
        .conclude()

    .build())
```

**Use conclude for one-to-many UX improvements:**
- **Split pattern:** 1 value → N fields (SSN "123456789" → 3 parts: "123", "45", "6789")
- **Expand pattern:** 1 choice → N checkboxes (tax classification → 7 checkboxes)
- **Roll-up pattern:** N mutually-exclusive fields → 1 master + N concludes

**CRITICAL: `.must()` vs `.as_*` Usage**

`.must()` defines **CONTENT** constraints (mandatory semantic requirements):
- Use SPARINGLY - only when field MUST contain specific information
- Creates a hard blocking constraint: field cannot be empty/skipped unless explicitly stated
- Example: `.must("match tax return exactly")` OR `.must("be exactly 9 digits, or leave blank for N/A")`

`.as_*()` defines **TYPE/FORMAT** transformations (computed by LLM):
- Use LIBERALLY - for any type casting, formatting, or derived values
- Alice accepts format variations, then computes the transformation
- Example: `.as_int()`, `.as_bool()`, `.as_str("name", "description")`

**Rule of thumb:** Expect MORE `.as_*` calls than `.must()` in your interview definition.

**Roll-up pattern for mutually-exclusive fields:**

When PDF requires exactly ONE of several mutually-exclusive fields (e.g., SSN xor EIN), use a master field with `.as_one()` for discrimination and `.as_str()` for value extraction, then conclude fields to populate specific PDF field_ids:

```python
# Master field: collect the data with type discrimination
.field("tin")
    .desc("What is your taxpayer identification number?")
    .as_one("number_type", "SSN", "EIN")
    .as_str("number_value", "The 9 digits only, formatted #########")
    .hint("Background: Individuals use SSN, entities use EIN")

# Conclude fields: populate specific PDF fields based on master data
.field("topmostSubform[0].Page1[0].f1_11[0]")
    .desc("First 3 digits of SSN (or empty if EIN)")
    .conclude()
.field("topmostSubform[0].Page1[0].f1_12[0]")
    .desc("Middle 2 digits of SSN (or empty if EIN)")
    .conclude()
.field("topmostSubform[0].Page1[0].f1_13[0]")
    .desc("Last 4 digits of SSN (or empty if EIN)")
    .conclude()
.field("topmostSubform[0].Page1[0].f1_14[0]")
    .desc("First 2 digits of EIN (or empty if SSN)")
    .conclude()
.field("topmostSubform[0].Page1[0].f1_15[0]")
    .desc("Last 7 digits of EIN (or empty if SSN)")
    .conclude()
```

This ensures the system reaches "_enough" after collecting the master field, then uses conclude to derive all specific fields.

**Default to direct mapping:** PDF field_ids are internal - users only see `.desc()`.

**Field types:**
- Text → `.field("id").desc("question")`
- Checkbox → `.field("id").desc("question").as_bool()`
- Radio/choice (mandatory) → `.field("id").desc("question").as_one("opt1", "opt2", ...)`
- Radio/choice (optional) → `.field("id").desc("question").as_nullable_one("opt1", "opt2", ...)`

**Optional fields** (from PDF tooltip, content context clues, stated in instructions, etc.):
```python
.field("middle_name")
    .desc("Middle name")
    .hint("Background: Optional per form instructions")
```

**Transformations** (`.as_*` methods compute derived values as "cast" operations):
- `.as_int()`, `.as_float()`, `.as_bool()` - Type casts
- `.as_list()`, `.as_json()` - Structure parsing
- `.as_percent()`, `.as_lang()` - Derived values
- `.as_str("name", "description")` - Custom string extractions

**Cardinality** (choose from set):
```
.as_one()             Exactly one choice required
.as_nullable_one()    Zero or one choice
.as_multi()           One or more choices required
.as_nullable_multi()  Zero or more choices
```

---

### Step 3: Run Conversational Server

```bash
python -m chatfield.server.cli
```

**IMPORTANT: Track the server PID** from the server logs when it starts. The server will log its process ID at startup.

Wait for server to exit normally. The server captures stdout with format:
```python
{
    'field_id': {
        'value': 'collected value',
        'context': 'conversation context',
        'as_quote': 'original quote'
    },
    ...
}
```

**If server fails to exit properly:** Send SIGTERM to the server PID (NOT to the parent shell):
```bash
kill -TERM <server_pid>
```

DO NOT use `kill` on the parent shell process or any shell job control commands that would terminate the shell session.

---

### Step 4: Parse Results and Fill PDF

**a) Parse server output** → extract field_id and value.

**b) Create `input.values.json`** (Write tool):
```json
[
  {
    "field_id": "topmostSubform[0].Page1[0].f1_01[0]",
    "page": 1,
    "value": "Jason Smith"
  },
  {
    "field_id": "topmostSubform[0].Page1[0].checkbox[0]",
    "page": 1,
    "value": "/1"
  }
]
```

Convert booleans: Read `.form.json` for `checked_value`/`unchecked_value` (typically "/1" or "/On" for True, "/Off" for False).

**c) Fill PDF:**
```bash
python scripts/fill_fillable_fields.py input.pdf input.values.json input.done.pdf
```

---

## Key Rules

1. **ONE file:** Edit `Python/chatfield/server/interview.py` only (EDITABLE ZONE)
2. **Direct mapping default:** Use PDF field_ids directly unless splitting/deriving
3. **Exact field_ids:** Keep from `.form.json` unchanged
4. **Extract knowledge:** ALL form instructions go into traits/hints
5. **Format flexibility:** Never specify format in `.desc()` - Alice accepts variations

---

## Example: Complete W-9 Form

### 1. Check fillability
```bash
python scripts/check_fillable_fields.py fw9.pdf
```

### 2. Extract content and fields
```python
mcp__markitdown__convert_to_markdown(uri="file:///absolute/path/to/fw9.pdf")
```
```bash
python scripts/extract_form_field_info.py fw9.pdf fw9.form.json
```

### 3. Extract knowledge and edit interview.py
- Extract actionable knowledge from markdown
- Add form-level knowledge as Alice traits
- Add field-level knowledge as field hints
- Define fields with exact IDs from fw9.form.json

### 4. Run server
```bash
python -m chatfield.server.cli
```

### 5. Parse results and fill
```bash
python scripts/fill_fillable_fields.py fw9.pdf fw9.values.json fw9.done.pdf
```

---

## Additional Resources

- **API Reference:** references/api-reference.md (builder methods, transformations, validation)
- **Non-fillable PDFs:** references/nonfillable-forms.md (visual field extraction workflow)

---

## Implementation Note

This skill uses the Chatfield library (`/home/dev/src/Chatfield/Python`) to transform rigid form fields into conversational dialogues. The library orchestrates natural language data collection, validates responses, computes transformations, and populates structured form data.
