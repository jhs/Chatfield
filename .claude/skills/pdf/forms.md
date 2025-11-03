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

**File naming convention**: For any PDF `foo.pdf`, the workflow creates `foo.form.json` (form definition), `foo.values.json` (collected data), and `foo.done.pdf` (filled PDF).

## Complete Workflow Steps

### Step 1: Extract Form Fields

Extract fillable form field metadata from your PDF:

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

Read the created `<basename>.form.json` file to learn and understand this form definition.

Next, define that form as a Chatfield Interview object by editing `Python/chatfield/server/interview.py`. Defining the `interview` to be identical to the form definition from `<basename>.form.json` within the "EDITABLE ZONE" BEGIN and END markers. For example:

```python
interview = (chatfield()
    .type("W9TaxForm")
    .desc("IRS Form W-9")
    .alice()
        .type("Tax Form Assistant")
        .trait("professional and accurate")
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

### Step 3: Customize Interview (RECOMMENDED)

The interview definition in `Python/chatfield/server/interview.py` is fully customizable. You should enhance it to provide better user experience. **See ./chatfield.md for complete API reference.**

**Recommended customizations**:
- **Clear descriptions**: Use `.desc("What is your Social Security Number?")` instead of field IDs
- **Helpful context**: Add `.hint("Most individuals select 'Individual/sole proprietor'")`
- **Use PDF tooltips**: If a field has a `tooltip` in the `.form.json`, use it as `.hint()` text prefixed with "Tooltip: " - tooltips are user-facing guidance from the original PDF
- **Role configuration**: Use `.alice()` with `.type()` and `.trait()` methods, configure `.bob()` similarly

**Example improvements**:
```python
# Example showing tooltip usage
# If the .form.json shows: {"field_id": "ssn_field", "tooltip": "Enter 9-digit SSN"}
interview = (chatfield()
    .type("W9TaxForm")
    .alice()
        .type("Tax Form Assistant")
        .trait("professional and accurate")
    .field("ssn_field")
        .desc("What is your Social Security Number?")
        .hint("Tooltip: Enter 9-digit SSN")  # Prefix tooltip text with "Tooltip: "
    .field("f1_02[0]")
        .desc("What is your email address?")
        .hint("Format: user@example.com")  # Add your own hints too
    .build())
```

**For all builder methods, validation syntax, transformations, and role configuration, see ./chatfield.md**

### Step 4: Run Chatfield Server and Capture Results

Start the Chatfield server subprocess to collect data via browser-based interview:

```bash
python -m chatfield.server.cli
```

Wait for the server CLI to exit. When the user input is complete and valid, the server auto-shuts down and prints all collected data to stdout.

### Step 5: Parse Results and Fill PDF

Extract field values from server output and populate the PDF.

The server prints interview results to stdout (pretty-printed Python object) which is easy to parse.

Use the collected data to populate the PDF form:

```bash
python scripts/fill_fillable_fields.py input.pdf input.values.json input.done.pdf
```

## Complete Example: W-9 Form

### 1. Check if form has fillable fields

```bash
python scripts/check_fillable_fields.py fw9.pdf
```

### 2. Extract form field metadata

```bash
python scripts/extract_form_field_info.py fw9.pdf fw9.form.json
```

### 3. Use the fields JSON file to build interview.py

First read the file using any tool you wish, example:
```bash
cat fw9.form.json
```

Next, edit from this software project root: `Python/chatfield/server/interview.py`
- Replace interview with builder code for W-9 fields
- Add clear field descriptions
- Add helpful hints for complex fields
- Configure interview roles and traits

### 4. Run Chatfield server subprocess

```bash
python -m chatfield.server.cli
```

- Server prints SERVER_READY to stderr
- Browser opens automatically
- User completes interview in browser
- Server auto-shuts down
- Capture results from stdout

### 5. Create field values JSON and fill PDF

ing the field values from server output, create `fw9.values.json` with those values populated. The format must match what the `fill_fillable_fields.py` script expects:

```json
[
  {
    "field_id": "topmostSubform[0].Page1[0].f1_01[0]",
    "page": 1,
    "value": "John Smith"
  },
  {
    "field_id": "topmostSubform[0].Page1[0].FederalClassification[0].c1_01[0]",
    "page": 1,
    "value": "/On"
  }
]
```

**Required fields in each entry**:
- `field_id`: Must exactly match the field ID from the `.form.json` file
- `page`: Page number (1-based) where the field appears
- `value`: The field value (string for text fields, "/On"/"/Off" for checkboxes, option values for radio/choice fields)

Then fill the PDF:

```bash
python scripts/fill_fillable_fields.py fw9.pdf fw9.values.json fw9.done.pdf
```

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
       .trait("professional and accurate")
       .trait("records optional fields as empty string when user indicates or implies no answer")
   ```

**Complete Example**:
```python
interview = (chatfield()
    .alice()
        .type("Tax Form Assistant")
        .trait("records optional fields as empty string when explicitly or implicitly left blank by the user")
    .field("legal_name")
        .desc("Full legal name")
        .must("match your tax return exactly")  # Mandatory content
    .field("middle_name")
        .desc("Middle name (optional)")  # Optional content - can be ""
    .field("business_name")
        .desc("Business name (optional, leave blank if same as legal name)")
    .field("preferred_contact")
        .desc("Preferred contact method (optional)")
        .as_maybe("method", "email", "phone", "mail")  # Optional selection
    .build())
```

**Result**: All four fields must be discussed and populated, but `middle_name`, `business_name`, and possibly `preferred_contact` can contain empty values.

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
