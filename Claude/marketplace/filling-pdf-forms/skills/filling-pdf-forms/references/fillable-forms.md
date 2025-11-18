# Fillable PDF Forms Workflow

Complete fillable PDF forms using conversational interviews to collect data, then populate form fields programmatically.

## Contents
- Workflow Overview
- Step 1: Extract PDF Content and Field Metadata
- Step 2: Create Interview Definition
- Step 3: Run Conversational Server
- Step 4: Parse Results and Fill PDF
- Key Rules
- Complete Example

## Workflow Overview

Copy this checklist and track progress:

```
Fillable PDF Form Progress:
- [ ] Step 1: Extract PDF content and field metadata
- [ ] Step 2: Build interview definition (validate with checklist in ../SKILL.md)
- [ ] Step 3: Run conversational server
- [ ] Step 4: Parse results and fill PDF
```

**CRITICAL: If any script fails, HALT and report the error. Do NOT proceed or attempt workarounds.**

---

## Step 1: Extract PDF Content and Field Metadata

1a. Examine the PDF content as markdown:

```bash
markitdown input.pdf
```

Returns PDF content as markdown, to stdout.

1b. Extract form fields:

**b) Extract form fields:**
```bash
python scripts/extract_form_field_info.py input.pdf input.form.json
```

Creates JSON with field_id, type (text/checkbox/radio_group/choice), page, rect, tooltip, and type-specific properties.

---

## Step 2: Build Interview Definition

**Source template:** `scripts/chatfield/chatfield_interview.py`

**a) Extract form knowledge from markdown:**

Extract actionable knowledge ONLY:
- Form purpose (1-2 sentences)
- Key term definitions
- Field completion instructions
- Valid options/codes
- Decision logic ("If X then Y")

Place in interview:
- **Form-level** → Alice traits: `.trait("Background: [form purpose and context]...")`
- **Field-level** → Field hints: `.hint("Background: [field-specific guidance]")`

**b) Write interview using builder API:**

**Multilingual Forms:** If the form is in a language the user doesn't speak, see ./multilingual.md for guidance on preserving the original form language while translating the conversation.


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
        .trait("Speaks naturally and freely")

    # Default: map directly (one PDF field_id → one question)
    .field("topmostSubform[0].Page1[0].f1_01[0]")
        .desc("What is your full legal name?")
        .hint("Background: Should match official records per form instructions")

    # Fan-out pattern: collect once, use .as_*() to populate multiple PDF fields
    .field("age")
        .desc("What is your age in years?")
        .as_int("age_years", "Age as integer")
        .as_bool("over_18", "True if 18 or older")
        .as_str("age_display", "Age formatted for display")

    .build())
```

**Fan-out patterns:** Collect once with lenient formatting, use `.as_*()` casts to populate multiple PDF fields from single value.

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

**Discriminate + split:** For mutually-exclusive field sets, use `.as_*()` casts with conditional logic:

```python
.field("tin")
    .desc("Is your taxpayer identification number EIN or SSN and what is that number?")
    .must("be exactly 9 digits")
    .must("indicate SSN or EIN type")
    .as_str("ssn_part1", "First 3 of SSN, or empty if N/A")
    .as_str("ssn_part2", "Middle 2 of SSN, or empty if N/A")
    .as_str("ssn_part3", "Last 4 of SSN, or empty if N/A")
    .as_str("ein_full", "Full 9-digit EIN, or empty if N/A")
    .as_bool("is_ssn", "True if SSN, False if EIN")
```

**When to use `.conclude()`:**

Use `.conclude()` when derived field depends on multiple previous fields or requires complex logic that can't be expressed in single field's casts.

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

**Hint conventions (all hints must have a prefix):**
- **Background hints** (start with "Background:"): Internal notes for Alice only. Alice uses these to handle formatting, conversions, and context without mentioning them to Bob. Example: `.hint("Background: Convert to Buddhist calendar by adding 543 years")`
- **Tooltip hints** (start with "Tooltip:"): May be shared with Bob if helpful. Example: `.hint("Tooltip: Your employer should provide this number")`

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

**c) Validate interview definition:**

Before proceeding, use the **Interview Validation Checklist** in ../SKILL.md to verify the interview meets quality standards.

If any items fail validation:
1. Review the specific issue in the checklist
2. Fix the interview definition
3. Re-run validation checklist
4. Proceed only when all items pass

---

## Step 3: Run Conversational Server

**Create working directory:**
```bash
# For PDF named input.pdf, create input.chatfield/
mkdir input.chatfield
cp scripts/chatfield/run_server.py input.chatfield/
cp scripts/chatfield/chatfield_interview.py input.chatfield/
```

**Edit interview in working directory:**
Edit `input.chatfield/chatfield_interview.py` with the interview definition from Step 2.

**Run server:**
```bash
cd input.chatfield
python run_server.py
```

Wait for server to exit normally. Server outputs collected data to stdout in format:
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

**Cleanup:**
```bash
cd ..
# Leave input.chatfield/ directory for inspection
```

---

## Step 4: Parse Results and Fill PDF

**a) Parse server output** → extract field_id and value.

**b) Create `input.values.json`** (Write tool):
```json
[
  {"field_id": "field_name", "page": 1, "value": "Jason Smith"},
  {"field_id": "age_years", "page": 1, "value": 25},
  {"field_id": "age_display", "page": 1, "value": "25"},
  {"field_id": "checkbox_over_18", "page": 1, "value": "/1"}
]
```

Convert booleans: Read `.form.json` for `checked_value`/`unchecked_value` (typically "/1" or "/On" for checked, "/Off" for unchecked).

**c) Fill PDF:**
```bash
python scripts/fill_fillable_fields.py input.pdf input.values.json input.done.pdf
```

---

## Key Rules

1. **Working directory:** Create `<basename>.chatfield/` directory (replace .pdf with .chatfield), copy scripts, edit interview copy, run server, then cleanup
2. **Direct mapping default:** Use PDF field_ids directly unless using fan-out patterns
3. **Fan-out patterns:** Use `.as_*()` casts to populate multiple PDF fields from single collected value
4. **Exact field_ids:** Keep from `.form.json` unchanged (use as cast names or direct field names)
5. **Extract knowledge:** ALL form instructions go into traits/hints
6. **Format flexibility:** Never specify format in `.desc()` - Alice accepts variations

---

## Complete Example

### 1. Check fillability
```bash
python scripts/check_fillable_fields.py input.pdf
```

### 2. Extract content and fields
```bash
python scripts/as_markdown.py input.pdf
```
```bash
python scripts/extract_form_field_info.py input.pdf input.form.json
```

### 3. Build interview definition
- Extract actionable knowledge from markdown
- Add form-level knowledge as Alice traits
- Add field-level knowledge as field hints
- Define fields with exact IDs from input.form.json
- Validate with Interview Validation Checklist (see ../SKILL.md)

### 4. Setup working directory and run server
```bash
mkdir input.chatfield
cp scripts/chatfield/run_server.py input.chatfield/
cp scripts/chatfield/chatfield_interview.py input.chatfield/
# Edit input.chatfield/chatfield_interview.py with interview definition
cd input.chatfield
python run_server.py
cd ..
# Leave input.chatfield/ directory for inspection
```

### 5. Parse results and fill
```bash
python scripts/fill_fillable_fields.py input.pdf input.values.json input.done.pdf
```

---

## Additional Resources

- **Interview Validation Checklist:** ../SKILL.md (shared validation checklist for interview quality)
- **API Reference:** api-reference.md (builder methods, transformations, validation)
- **Non-fillable PDFs:** nonfillable-forms.md (alternative workflow for visual annotation)
