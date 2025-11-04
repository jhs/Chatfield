**CRITICAL: ALL PDF forms MUST use the Chatfield conversational workflow.**

**You MUST complete these steps in order. Do not skip ahead to writing code.**

If you need to fill out a PDF form, first check to see if the PDF has fillable form fields. Run this script from this file's directory:
 `python scripts/check_fillable_fields <file.pdf>`, and depending on the result:
- **Fillable fields detected**: Follow the instructions in this file (forms.md)
- **Non-fillable fields**: See ./nonfillable-forms.md for complete workflow

**Both workflows use Chatfield** - the difference is only in how field definitions are extracted (programmatic vs. visual analysis).

**Documentation**:
- **This file (forms.md)**: Fillable PDF workflow
- **./nonfillable-forms.md**: Non-fillable PDF workflow
- **./chatfield.md**: Complete Chatfield API reference (builder methods, transformations, validation, roles)
- **./reference.md**: Advanced PDF processing techniques

# Fillable fields

**MANDATORY: All fillable PDF forms MUST use the Chatfield conversational workflow.**

Chatfield transforms rigid form filling into natural conversations. The conversational workflow collects data, validates responses, transforms types, and populates PDF fields automatically. **See ./chatfield.md for complete Chatfield API documentation.**

## Chatfield Workflow Overview

The workflow has these stages:

**Stage 1: PDF Analysis** → Extract form field metadata from the PDF
**Stage 2: Interview Definition** → Edit `Python/chatfield/server/interview.py` with Chatfield builder code
**Stage 3: Server Execution** → Start Chatfield server subprocess for browser-based data collection
**Stage 4: Data Collection** → User completes interview in browser, when done the server prints all results and exits
**Stage 5: PDF Population** → Parse server output and fill PDF form fields to create `<basename>.done.pdf`

**File naming convention**: For any PDF `foo.pdf`, the workflow creates:
- `foo.form.md` - PDF content as Markdown
- `foo.form.json` - Form definition
- `foo.values.json` - Collected data
- `foo.done.pdf` - Filled PDF

## Complete Workflow Steps

### Step 1: Extract Content and Form Fields

**Step 1a: Convert PDF to Markdown**

YOU MUST call the `mcp__markitdown__convert_to_markdown` tool to extract the PDF content:
- Parameter: `uri` = `"file:///absolute/path/to/input.pdf"` (use the full absolute path)
- This tool **returns markdown content as output** (it does NOT create files)

**Step 1b: Save Markdown to File**

YOU MUST use the Write tool to save the markdown content from Step 1a:
- Target file: `<basename>.form.md` (e.g., for `fw9.pdf` → `fw9.form.md`)
- Content: The exact markdown output from the MCP tool in Step 1a

**Step 1c: Extract Form Field Metadata**

Run the extraction script to create form field metadata:

```bash
python scripts/extract_form_field_info.py input.pdf input.form.json
```

This creates a JSON file containing field metadata in this format:

```json
[
  {
    "field_id": (unique ID for the field),
    "page": (page number, 1-based),
    "rect": ([left, bottom, right, top] bounding box in PDF coordinates, y=0 is the bottom of the page),
    "type": ("text", "checkbox", "radio_group", or "choice"),
    "tooltip": (optional: tooltip text from PDF field metadata, if present)
  },
  // Checkboxes have "checked_value" and "unchecked_value" properties:
  {
    "field_id": (unique ID for the field),
    "page": (page number, 1-based),
    "type": "checkbox",
    "checked_value": (Set the field to this value to check the checkbox),
    "unchecked_value": (Set the field to this value to uncheck the checkbox),
    "tooltip": (optional: tooltip text, if present)
  },
  // Radio groups have a "radio_options" list with the possible choices.
  {
    "field_id": (unique ID for the field),
    "page": (page number, 1-based),
    "type": "radio_group",
    "tooltip": (optional: tooltip text, if present),
    "radio_options": [
      {
        "value": (set the field to this value to select this radio option),
        "rect": (bounding box for the radio button for this option)
      },
      // Other radio options
    ]
  },
  // Multiple choice fields have a "choice_options" list with the possible choices:
  {
    "field_id": (unique ID for the field),
    "page": (page number, 1-based),
    "type": "choice",
    "tooltip": (optional: tooltip text, if present),
    "choice_options": [
      {
        "value": (set the field to this value to select this option),
        "text": (display text of the option)
      },
      // Other choice options
    ],
  }
]
```

**Key Information Extracted**:
- Field IDs and types (text, checkbox, radio_group, choice)
- Page numbers and coordinates
- **Tooltips** (optional): User-facing guidance text embedded in PDF field metadata
- For checkboxes: checked/unchecked values
- For radio/choice fields: available options

### Step 2: Define Interview in Server File

**YOU MUST NOW EDIT THE SERVER FILE - This is the critical step**

**Step 2a: Extract ALL Form Knowledge (CRITICAL)**

**This is the most critical step** - The Chatfield interview definition is the ONLY source of information during the conversation. The PDF and all files will be absent. Alice must have ALL form knowledge embedded as traits and hints to function as a RAG system.

YOU MUST thoroughly read and extract ALL instructional content from `<basename>.form.md`:

**What to extract (KEY KNOWLEDGE ONLY):**
1. **Purpose/overview** - What this form is for, when it's used (1-2 sentences)
2. **Definitions of key terms** - Only terms that directly help complete fields (e.g., "U.S. person", "disregarded entity", "EIN vs SSN")
3. **How to complete specific fields** - Instructions for each line/field
4. **Valid options/codes** - Tables of codes, options, mappings needed to populate fields
5. **Decision logic** - "If X, then Y" rules that affect field completion
6. **Common scenarios** - Brief examples that clarify confusing fields

**What NOT to extract:**
- Legal statements, privacy notices, penalty descriptions
- Procedural info (where to send form, how to get forms)
- Lengthy background that doesn't help complete the form
- Certification language, signature requirements (user will handle this separately)

**Where to put extracted knowledge:**
- **Form-level knowledge** → Alice traits using `.trait("Background knowledge: ...")`
  - Purpose of form
  - Definitions of key terms
  - General instructions
  - Legal context and penalties
  - Special cases and exceptions

- **Field-level knowledge** → Field hints using `.hint("Background: ...")` or `.hint("Tooltip: ...")`
  - Line-by-line instructions for that specific field
  - Valid options/codes for that field
  - Validation rules and requirements
  - Examples for that field

**Example extractions from W-9 form:**

**Form-level knowledge (Alice traits):**
```python
.alice()
    .type("Tax Form Assistant")
    .trait("Uses plain language when asking questions rather than strict field format rules")
    .trait("Converts received plain language into the valid form data")
    .trait("records optional fields as empty string when user indicates or implies no answer")
    .trait("Background knowledge: Form W-9 collects taxpayer ID numbers for IRS information returns")
    .trait("Background knowledge: U.S. persons include citizens, resident aliens, U.S. entities, and domestic trusts")
    .trait("Background knowledge: Individuals use SSN, entities use EIN. Sole proprietors can use either")
    .trait("Background knowledge: Disregarded entities report owner's information, not entity information")
    .trait("Background knowledge: LLC tax classification depends on how it's taxed: C, S, or P for partnership")
```

**Field-level knowledge (field hints):**
```python
.field("topmostSubform[0].Page1[0].f1_01[0]")
    .desc("What is your full legal name?")
    .hint("Background: For individuals, use name as shown on tax return. For sole proprietors, this is the owner's name (business name goes on line 2)")
    .hint("Background: For disregarded entities, enter the owner's name, never the entity's name")

.field("topmostSubform[0].Page1[0].Boxes3a-b_ReadOrder[0].c1_1[0]")
    .desc("Are you an Individual/sole proprietor?")
    .hint("Background: Only ONE of the seven tax classification boxes should be checked")
    .hint("Background: Sole proprietors are individuals who own unincorporated businesses")
    .as_bool()

.field("topmostSubform[0].Page1[0].Boxes3a-b_ReadOrder[0].f1_03[0]")
    .desc("LLC tax classification code")
    .hint("Background: Only complete if LLC box is checked. Enter C, S, or P based on how the LLC is taxed")
    .hint("Background: C = C corporation, S = S corporation, P = Partnership")
```

**Critical:** Comprehensive extraction of actionable knowledge is essential. Alice relies entirely on these traits and hints.

**Step 2b: Edit the Interview Definition**

Target file for editing: `/home/dev/src/Chatfield/Python/chatfield/server/interview.py`

This file contains an EDITABLE ZONE marked by these exact comments:
- BEGIN marker: `# ---- BEGIN PDF SKILL EDITABLE ZONE ----`
- END marker: `# ---- END PDF SKILL EDITABLE ZONE ----`

**What you must do:**
1. Use the Read tool to read `Python/chatfield/server/interview.py` to see the current content and locate the EDITABLE ZONE
2. Use the Edit tool to replace ONLY the content between the BEGIN and END markers
3. The new content must be a complete Chatfield interview definition using the builder API
4. Include all fields from `<basename>.form.json` with the exact field IDs as-is

**What you must NOT do:**
- Do NOT create new Python files (e.g., in `examples/` or anywhere else)
- Do NOT create standalone scripts that run the interview directly
- Do NOT modify anything outside the EDITABLE ZONE markers
- Do NOT change the file location - it must be `Python/chatfield/server/interview.py`

**REQUIRED: Always configure Alice and Bob roles** with these traits as a starting point:
- **Alice**: Uses plain language when asking questions, converts responses to valid form data
- **Alice**: Records optional fields as empty string when the feedback indicates or implies no answer
- **Bob**: Speaks colloquially, needs help converting plain language to form format

For example:

```python
interview = (chatfield()
    .type("W9TaxForm")
    .desc("IRS Form W-9")
    .alice()
        .type("Tax Form Assistant")
        .trait("Uses plain language when asking questions rather than strict field format rules")
        .trait("Converts received plain language into the valid form data")
    .bob()
        .type("Person completing W-9")
        .trait("speaks colloquially and plainly, needs help converting to the form format")
    .field("topmostSubform[0].Page1[0].f1_01[0]")
        .desc("What is your full legal name?")
        .must("match the name on your tax return exactly")
    .field("topmostSubform[0].Page1[0].FederalClassification[0].c1_01[0]")
        .desc("Federal tax classification")
        .as_bool()
    # ... additional fields for each PDF form field
    .build())
```

**Field type mapping**:
- Text fields → basic string collection with `.desc()`
- Checkboxes → add `.as_bool()` transformation
- Radio groups → use `.as_one("option1", "option2", ...)`
- Choice fields → use `.as_one("choice1", "choice2", ...)`

### Step 3: Additional Customizations (Optional)

After completing the core interview definition with extracted knowledge (Step 2), you may add these optional customizations to improve the user experience:

**UX Improvements**:
- **User-friendly descriptions**: Use `.desc("Social Security Number")` instead of field IDs
- **Tooltips for users**: Add `.hint("Tooltip: ...")` for user-facing guidance (appears in the UI). Use this for all `tooltip` fields from `.form.json`, plus add your own where helpful
- **Roll-up related fields**: When a PDF splits one logical value into multiple fields (e.g., SSN as 3 separate fields: XXX-XX-XXXX), use hints to ask once and populate all:
  ```python
  .field("ssn_field_1")
      .desc("What is your Social Security Number?")
      .hint("Background: Ask for full SSN (XXX-XX-XXXX), populate this field with first 3 digits")
  .field("ssn_field_2")
      .desc("SSN middle digits")
      .hint("Background: Populate with digits 4-5 from the SSN asked earlier")
  .field("ssn_field_3")
      .desc("SSN last digits")
      .hint("Background: Populate with last 4 digits from the SSN asked earlier")
  ```

**Important**: Keep field IDs unchanged - downstream software needs the exact IDs from `.form.json`

**Example improvements**:
```python
# Example showing complete role configuration, tooltip usage, and roll-up pattern
interview = (chatfield()
    .type("W9TaxForm")
    .alice()
        .type("Tax Form Assistant")
        .trait("Uses plain language when asking questions rather than strict field format rules")
        .trait("Converts received plain language into the valid form data")
        .trait("Professional and accurate")  # Additional context-specific trait
        .trait("records optional fields as empty string when user indicates or implies no answer")
    .bob()
        .type("Person completing W-9")
        .trait("speaks colloquially and plainly, needs help converting to the form format")

    # Roll-up pattern: Ask for SSN once, populate three separate PDF fields
    .field("topmostSubform[0].Page1[0].social_security[0]")
        .desc("What is your Social Security Number?")
        .hint("Background: Ask for the full SSN, then populate this field with the first 3 digits")
    .field("topmostSubform[0].Page1[0].social_security[1]")
        .desc("SSN middle digits")
        .hint("Background: Populate this with digits 4-5 from the SSN asked earlier")
    .field("topmostSubform[0].Page1[0].social_security[2]")
        .desc("SSN last digits")
        .hint("Background: Populate this with the last 4 digits from the SSN asked earlier")

    # Roll-up pattern: Ask for date of birth once, populate separate year/month/day fields
    .field("topmostSubform[0].Page1[0].dob_month[0]")
        .desc("What is your date of birth?")
        .hint("Background: Ask for the full date of birth, then populate this field with the month (MM)")
    .field("topmostSubform[0].Page1[0].dob_day[0]")
        .desc("Birth day")
        .hint("Background: Populate this with the day (DD) from the date of birth asked earlier")
    .field("topmostSubform[0].Page1[0].dob_year[0]")
        .desc("Birth year")
        .hint("Background: Populate this with the year (YYYY) from the date of birth asked earlier")

    .field("topmostSubform[0].Page1[0].email[0]")
        .desc("What is your email address?")
        .hint("Background: Format: user@example.com")
    .build())
```

**For all builder methods, validation syntax, transformations, and role configuration, see ./chatfield.md**

### Step 4: Run Chatfield Server and Capture Results

Start the Chatfield server subprocess to collect data via browser-based interview:

```bash
python -m chatfield.server.cli
```

Wait for the server CLI to exit. When the user input is complete and valid, the server auto-shuts down and prints all collected data to stdout.

**Server Output Format**

The server prints collected field values to stdout in this format:

```python
{
    'topmostSubform[0].Page1[0].f1_01[0]': {
        'value': 'Jason Smith',
        'context': 'User provided their full legal name',
        'as_quote': 'My name is Jason Smith'
    },
    'topmostSubform[0].Page1[0].Boxes3a-b_ReadOrder[0].c1_1[0]': {
        'value': True,
        'context': 'User confirmed they are an individual/sole proprietor'
    },
    'topmostSubform[0].Page1[0].Address_ReadOrder[0].f1_07[0]': {
        'value': '123 Main St',
        'context': 'User provided street address'
    },
    # ... all other fields with their collected values
}
```

YOU MUST capture this stdout output and parse it to extract field values for Step 5.

### Step 5: Parse Results and Fill PDF

**Step 5a: Parse Server Output**

Extract the field values from the server's stdout output (format shown in Step 4).

For each field in the output dictionary:
- Get the field ID (e.g., `'topmostSubform[0].Page1[0].f1_01[0]'`)
- Get the `'value'` property from the nested dictionary
- The value may be a string, boolean, number, or other type

**Step 5b: Create Values JSON File**

YOU MUST use the Write tool to create `<basename>.values.json` with the collected data.

Format requirements:
- Must be a JSON array of objects
- Each object must have exactly three keys: `field_id`, `page`, and `value`
- Convert boolean values to checkbox format:
  - Read the `.form.json` to find the `checked_value` and `unchecked_value` for each checkbox field
  - `True` → use the `checked_value` (typically `"/1"` or `"/On"`)
  - `False` → use the `unchecked_value` (typically `"/Off"`)
- Convert all other values to strings

Example `<basename>.values.json` format:

```json
[
  {
    "field_id": "topmostSubform[0].Page1[0].f1_01[0]",
    "page": 1,
    "value": "Jason Smith"
  },
  {
    "field_id": "topmostSubform[0].Page1[0].Boxes3a-b_ReadOrder[0].c1_1[0]",
    "page": 1,
    "value": "/1"
  }
]
```

**Step 5c: Fill the PDF**

Run the fill script to populate the PDF form:

```bash
python scripts/fill_fillable_fields.py input.pdf input.values.json input.done.pdf
```

This creates the final filled PDF at `<basename>.done.pdf`.

## Complete Example: W-9 Form

### 1. Check if form has fillable fields

```bash
python scripts/check_fillable_fields.py fw9.pdf
```

### 2. Extract content and form fields (Step 1)

**2a. Convert PDF to markdown:**
- Call `mcp__markitdown__convert_to_markdown` with `uri: "file:///absolute/path/to/fw9.pdf"`
- Write the output to `fw9.form.md`

**2b. Extract form field metadata:**
```bash
python scripts/extract_form_field_info.py fw9.pdf fw9.form.json
```

### 3. Extract knowledge and edit interview.py (Step 2)

**3a. Thoroughly read `fw9.form.md`** to extract ALL actionable knowledge:
- Purpose: Form W-9 collects taxpayer ID numbers for IRS information returns
- Key definitions: U.S. person, disregarded entity, LLC classifications, backup withholding
- Line-by-line instructions for each field
- Decision logic (e.g., "If LLC, enter C/S/P classification")
- Valid codes (13 exempt payee codes, FATCA codes)

**3b. Edit `Python/chatfield/server/interview.py`** within the EDITABLE ZONE:
- Add extracted form-level knowledge as Alice traits (`.trait("Background knowledge: ...")`)
- For each field from `fw9.form.json`:
  - Use exact field ID
  - Add user-friendly `.desc()`
  - Add extracted field-level knowledge as hints (`.hint("Background: ...")`)
  - Add appropriate transformations (`.as_bool()`, `.as_one()`, etc.)
- Configure Alice and Bob roles with required baseline traits

### 4. Run Chatfield server subprocess

```bash
python -m chatfield.server.cli
```

- Server prints SERVER_READY to stderr
- Browser opens automatically
- User completes interview in browser
- Server auto-shuts down
- Capture results from stdout

### 5. Parse results and fill PDF (Step 5)

**5a. Parse the server output** from Step 4 to extract field values.

**5b. Create `fw9.values.json`** using the Write tool:
- Format as JSON array with objects containing `field_id`, `page`, and `value`
- Convert boolean checkbox values to "/1" (checked) or "/Off" (unchecked)
- Convert all other values to strings

Example format:
```json
[
  {
    "field_id": "topmostSubform[0].Page1[0].f1_01[0]",
    "page": 1,
    "value": "Jason Smith"
  },
  {
    "field_id": "topmostSubform[0].Page1[0].Boxes3a-b_ReadOrder[0].c1_1[0]",
    "page": 1,
    "value": "/1"
  }
]
```

**5c. Fill the PDF:**
```bash
python scripts/fill_fillable_fields.py fw9.pdf fw9.values.json fw9.done.pdf
```

This creates the completed form at `fw9.done.pdf`.

## Field Type Mapping

Chatfield automatically maps PDF field types to appropriate conversational patterns:

| PDF Field Type | Chatfield Method | Behavior | Example |
|----------------|-----------------|----------|---------|
| Text | `.field("name")` | Collects string value | "What is your name?" |
| Checkbox | `.as_bool()` | Collects boolean, maps to checked/unchecked values | "Are you a U.S. citizen?" |
| Radio Group | `.as_one("opt1", "opt2", ...)` | Presents choices, ensures one selection | "Individual, C Corp, or Partnership?" |
| Dropdown/Choice | `.as_one("choice1", ...)` | Presents options from PDF metadata | "Select your state" |

## Understanding Optional Fields

**Critical Distinction**: In Chatfield, all fields are **mandatory to discuss** but field **content can be optional**.

### Mandatory vs. Optional Concepts

1. **Field Presence (Mandatory)**: All defined fields must be populated (non-`None`) for an interview to be "done"
2. **Field Content (Optional)**: Fields can contain empty strings `""` or other "blank" values
3. **Key Distinction**: Not yet discussed (`None`) vs. explicitly left blank (`""`)

### Exceptions - Truly Mandatory Content

These field types require non-empty values:
- **`.as_one()`** - Must select exactly one choice
- **`.as_multi()`** - Must select at least one choice
- **Fields with strict validation** - e.g., `.must("be a valid email")` requires actual content

### Handling Optional PDF Form Fields

When a PDF form field is marked "optional", follow this process:

1. **Avoid strict validation** - Don't use `.must()` rules that would fail on empty strings:
   ```python
   # ❌ Bad - rejects empty values
   .field("middle_name")
       .desc("Middle name (optional)")
       .must("be at least 2 characters")

   # ✅ Good - allows empty values
   .field("middle_name")
       .desc("Middle name (optional)")
   ```

2. **Describe as optional in `.desc()`**:
   ```python
   .field("phone_extension")
       .desc("Phone extension (optional, leave blank if none)")
   ```

3. **Configure Alice to record blanks** - Give Alice a trait to handle optional fields:
   ```python
   .alice()
       .type("Form Assistant")
       .trait("Professional and accurate")
       .trait("records optional fields as empty string when user indicates or implies no answer")
   ```

**Complete Example**:
```python
interview = (chatfield()
    .alice()
        .type("Tax Form Assistant")
        .trait("Uses plain language when asking questions rather than strict field format rules")
        .trait("Converts received plain language into the valid form data")
        .trait("records optional fields as empty string when explicitly or implicitly left blank by the user")
    .bob()
        .type("Person completing tax form")
        .trait("speaks colloquially and plainly, needs help converting to the form format")
    .field("topmostSubform[0].Page1[0].f1_01[0]")
        .desc("Full legal name")
        .must("match your tax return exactly")  # Mandatory content
    .field("topmostSubform[0].Page1[0].f1_02[0]")
        .desc("Middle name (optional)")  # Optional content - can be ""
    .field("topmostSubform[0].Page1[0].f1_03[0]")
        .desc("Business name (optional, leave blank if same as legal name)")
    .field("topmostSubform[0].Page1[0].contact_method[0]")
        .desc("Preferred contact method (optional)")
        .as_maybe("method", "email", "phone", "mail")  # Optional selection
    .build())
```

**Result**: All four fields must be discussed and populated, but the middle name, business name, and contact method fields can contain empty values.

## Advanced Chatfield Features

Chatfield supports many advanced features for sophisticated form workflows:
- **Type transformations**: `.as_int()`, `.as_float()`, `.as_bool()`, `.as_list()`, `.as_json()`, `.as_percent()`, `.as_lang()`
- **Choice cardinality**: `.as_one()` (required), `.as_maybe()` (optional), `.as_multi()` (1+), `.as_any()` (0+)
- **Conditional logic**: Later fields naturally reference earlier values
- **Confidential fields**: `.confidential()` tracks values silently without asking
- **Concluding fields**: `.conclude()` computes summaries after conversation ends

**See ./chatfield.md for complete API documentation, syntax, and examples.**

## Troubleshooting

**PDF-specific issues**:
- **Field names with special characters**: Use bracket notation to access fields with brackets, dots, spaces, or other special characters: `interview["topmostSubform[0].Page1[0].f1_01[0]"]`
- **Checkbox not filling correctly**: Verify `checked_value` and `unchecked_value` in `<basename>.form.json` match what the PDF expects (usually "/On" and "/Off").
- **PDF fields not populating**: Ensure field IDs in `<basename>.values.json` exactly match those from `extract_form_field_info.py` and include the required `page` field.

**Chatfield issues**: See ./chatfield.md troubleshooting section for API key configuration, validation tuning, and field access patterns.

# Non-fillable PDFs

**For non-fillable PDFs, see ./nonfillable-forms.md for complete workflow instructions.**

Non-fillable PDFs use the same Chatfield conversational workflow as fillable PDFs. The only difference is in field extraction (visual analysis with bounding boxes instead of programmatic extraction) and population (text annotations instead of form field updates).
