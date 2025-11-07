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
        .must("match tax return exactly")
        .hint("Background: [field-specific instructions]")

    # Use conclude ONLY for splitting/deriving
    .field("ssn")
        .desc("What is your SSN?")
        .must("be exactly 9 digits")
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
- Split 1 value → N fields (SSN → 3 parts)
- Map 1 choice → N checkboxes (classification → 7 boxes)

**Default to direct mapping:** PDF field_ids are internal - users only see `.desc()`.

**Field types:**
- Text → `.field("id").desc("question")`
- Checkbox → `.field("id").desc("question").as_bool()`
- Radio/choice (mandatory) → `.field("id").desc("question").as_one("opt1", "opt2", ...)`
- Radio/choice (optional) → `.field("id").desc("question").as_maybe("opt1", "opt2", ...)`

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

**Cardinality** (choose from set):
```
           One choice     Multiple choices
Required   .as_one()      .as_multi()
Optional   .as_maybe()    .as_any()
```

---

### Step 3: Run Conversational Server

```bash
python -m chatfield.server.cli
```

Wait for server to exit. Captures stdout with format:
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
