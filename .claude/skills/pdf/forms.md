**CRITICAL: ALL PDF forms MUST use the Chatfield conversational workflow.**

**You MUST complete these steps in order. Do not skip ahead to writing code.**

If you need to fill out a PDF form, first check to see if the PDF has fillable form fields. Run this script from this file's directory:
 `python scripts/check_fillable_fields <file.pdf>`, and depending on the result go to either the "Fillable fields" or "Non-fillable fields" section below.

**Both workflows use Chatfield** - the difference is only in how field definitions are extracted (programmatic vs. visual analysis).

**Documentation**:
- **This file (forms.md)**: PDF workflow orchestration and steps
- **./chatfield.md**: Complete Chatfield API reference (builder methods, transformations, validation, roles)
- **./reference.md**: Advanced PDF processing techniques

# Fillable fields

**MANDATORY: All fillable PDF forms MUST use the Chatfield conversational workflow.**

Chatfield transforms rigid form filling into natural conversations. The conversational workflow collects data, validates responses, transforms types, and populates PDF fields automatically. **See ./chatfield.md for complete Chatfield API documentation.**

## Chatfield Workflow Overview

The workflow has these stages:

**Stage 1: PDF Analysis** → Extract form field metadata from the PDF
**Stage 2: Interview Generation** → Chatfield creates a conversational interview from field definitions
**Stage 3: Data Collection** → User converses with Chatfield to provide form data
**Stage 4: PDF Population** → Collected data fills the PDF form fields

## Complete Workflow Steps

### Step 1: Extract Form Fields

Extract fillable form field metadata from your PDF:

```bash
python scripts/extract_form_field_info.py input.pdf field_info.json
```

This creates a JSON file containing field metadata in this format:

```json
[
  {
    "field_id": (unique ID for the field),
    "page": (page number, 1-based),
    "rect": ([left, bottom, right, top] bounding box in PDF coordinates, y=0 is the bottom of the page),
    "type": ("text", "checkbox", "radio_group", or "choice"),
  },
  // Checkboxes have "checked_value" and "unchecked_value" properties:
  {
    "field_id": (unique ID for the field),
    "page": (page number, 1-based),
    "type": "checkbox",
    "checked_value": (Set the field to this value to check the checkbox),
    "unchecked_value": (Set the field to this value to uncheck the checkbox),
  },
  // Radio groups have a "radio_options" list with the possible choices.
  {
    "field_id": (unique ID for the field),
    "page": (page number, 1-based),
    "type": "radio_group",
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
- For checkboxes: checked/unchecked values
- For radio/choice fields: available options

### Step 2: Generate Chatfield Interview Script

Generate a Python script that uses Chatfield to collect form data conversationally:

```bash
python scripts/generate_chatfield_interview.py field_info.json interview.py
```

This creates an executable Python script that:
- Builds a Chatfield interview with `.field()` calls for each PDF field
- Maps field types to appropriate Chatfield transformations:
  - Text fields → basic string collection
  - Checkboxes → `.as_bool()` transformation
  - Radio groups → `.as_one("option1", "option2", ...)`
  - Choice fields → `.as_one("choice1", "choice2", ...)`
- Runs the conversational interview
- Saves results in `field_values.json` format

### Step 3: Customize Interview (RECOMMENDED)

The generated script is fully customizable. You should enhance it to provide better user experience. **See ./chatfield.md for complete API reference.**

**Recommended customizations**:
- **Clear descriptions**: Use `.desc("What is your Social Security Number?")` instead of auto-generated text
- **Validation rules**: Add `.must("be in format ###-##-####")` and `.reject("temporary emails")`
- **Helpful context**: Add `.hint("Most individuals select 'Individual/sole proprietor'")`
- **Role configuration**: Use `.alice()` with `.type()` and `.trait()` methods, configure `.bob()` similarly

**Example improvements**:
```python
.field("ssn")
    .desc("What is your Social Security Number?")
    .must("be in format ###-##-####")

.field("email")
    .must("be a valid email address")
    .reject("temporary or disposable email addresses")

interview = (chatfield()
    .type("W9TaxForm")
    .alice()
        .type("Tax Form Assistant")
        .trait("professional")
    .build())
```

**For all builder methods, validation syntax, transformations, and role configuration, see ./chatfield.md**

### Step 4: Run Conversational Interview

Execute the interview script to collect data through conversation:

```bash
export OPENAI_API_KEY=your-api-key
python interview.py --output field_values.json
```

The script will:
- Start a conversational interview in the terminal
- Ask about each form field naturally
- Validate responses using Chatfield's LLM-powered validation
- Transform data to appropriate types (booleans for checkboxes, etc.)
- Save collected data to `field_values.json`

**Example conversation**:
```
Assistant: Hi! I'll help you complete this form. What is your full legal name?
You: John Smith
Assistant: Thank you, John. What is your Social Security Number?
You: 123-45-6789
Assistant: Got it. What is your business name, if different from your name?
You: Not applicable
...
```

### Step 5: Fill PDF with Collected Data

Use the collected data to populate the PDF form:

```bash
python scripts/fill_fillable_fields.py input.pdf field_values.json output.pdf
```

This populates the PDF form fields with the conversationally collected data.

## Complete Example: W-9 Form

```bash
# 1. Check if form has fillable fields
python scripts/check_fillable_fields.py fw9.pdf

# 2. Extract form field metadata
python scripts/extract_form_field_info.py fw9.pdf fw9_fields.json

# 3. Generate Chatfield interview script
python scripts/generate_chatfield_interview.py fw9_fields.json fw9_interview.py

# 4. Customize fw9_interview.py (RECOMMENDED)
#    - Add clear field descriptions
#    - Add validation rules for SSN, ZIP, email, etc.
#    - Add helpful hints for complex fields
#    - Configure interview roles and traits

# 5. Run conversational interview
python fw9_interview.py --output fw9_values.json

# 6. Fill PDF with collected data
python scripts/fill_fillable_fields.py fw9.pdf fw9_values.json fw9_filled.pdf
```

## Field Type Mapping

Chatfield automatically maps PDF field types to appropriate conversational patterns:

| PDF Field Type | Chatfield Method | Behavior | Example |
|----------------|-----------------|----------|---------|
| Text | `.field("name")` | Collects string value | "What is your name?" |
| Checkbox | `.as_bool()` | Collects boolean, maps to checked/unchecked values | "Are you a U.S. citizen?" |
| Radio Group | `.as_one("opt1", "opt2", ...)` | Presents choices, ensures one selection | "Individual, C Corp, or Partnership?" |
| Dropdown/Choice | `.as_one("choice1", ...)` | Presents options from PDF metadata | "Select your state" |

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
- **Field names with special characters**: The generator uses `getattr(interview, "field_id", None)` to safely access fields with brackets, dots, or other special characters in their IDs.
- **Checkbox not filling correctly**: Verify `checked_value` and `unchecked_value` in `field_info.json` match what the PDF expects (usually "/On" and "/Off").
- **PDF fields not populating**: Ensure field IDs in `field_values.json` exactly match those from `extract_form_field_info.py`.

**Chatfield issues**: See ./chatfield.md troubleshooting section for API key configuration, validation tuning, and field access patterns.

## Why Chatfield is Mandatory

Chatfield provides natural conversation flow, contextual guidance, intelligent validation, and consistent data quality—replacing tedious, error-prone traditional form filling. **See ./chatfield.md for detailed benefits.**

# Non-fillable fields

**MANDATORY: All PDF forms MUST use the Chatfield conversational workflow, including non-fillable PDFs.**

For non-fillable PDFs, the extraction process differs (visual bounding box analysis instead of programmatic field extraction), but the Chatfield interview model is identical.

**Workflow Overview**:
1. **Visual Analysis** → Determine field locations and bounding boxes
2. **Generate Chatfield Interview** → Create conversational script from field definitions
3. **Customize Interview** → Add validation and better descriptions
4. **Collect Data** → Run conversation to gather values
5. **Annotate PDF** → Apply text annotations at bounding box locations

Follow the below steps *exactly*. You MUST perform all of these steps to ensure accurate form completion.

## Step 1: Visual Analysis (REQUIRED)
- Convert the PDF to PNG images. Run this script from this file's directory:
`python scripts/convert_pdf_to_images.py <file.pdf> <output_directory>`
The script will create a PNG image for each page in the PDF.
- Carefully examine each PNG image and identify all form fields and areas where the user should enter data. For each form field where the user should enter text, determine bounding boxes for both the form field label, and the area where the user should enter text. The label and entry bounding boxes MUST NOT INTERSECT; the text entry box should only include the area where data should be entered. Usually this area will be immediately to the side, above, or below its label. Entry bounding boxes must be tall and wide enough to contain their text.

These are some examples of form structures that you might see:

*Label inside box*
```
┌────────────────────────┐
│ Name:                  │
└────────────────────────┘
```
The input area should be to the right of the "Name" label and extend to the edge of the box.

*Label before line*
```
Email: _______________________
```
The input area should be above the line and include its entire width.

*Label under line*
```
_________________________
Name
```
The input area should be above the line and include the entire width of the line. This is common for signature and date fields.

*Label above line*
```
Please enter any special requests:
________________________________________________
```
The input area should extend from the bottom of the label to the line, and should include the entire width of the line.

*Checkboxes*
```
Are you a US citizen? Yes □  No □
```
For checkboxes:
- Look for small square boxes (□) - these are the actual checkboxes to target. They may be to the left or right of their labels.
- Distinguish between label text ("Yes", "No") and the clickable checkbox squares.
- The entry bounding box should cover ONLY the small square, not the text label.

### Step 2: Create fields.json with field definitions (REQUIRED)

Create `fields.json` with field metadata and bounding boxes. **Do NOT populate entry_text.text values yet** - these will come from the Chatfield conversation.

```json
{
  "pages": [
    {
      "page_number": 1,
      "image_width": 1200,
      "image_height": 1600
    }
  ],
  "form_fields": [
    {
      "field_id": "last_name",
      "page_number": 1,
      "description": "User's last name",
      "field_label": "Last name",
      "field_type": "text",
      "label_bounding_box": [30, 125, 95, 142],
      "entry_bounding_box": [100, 125, 280, 142],
      "entry_text": {
        "font_size": 14,
        "font_color": "000000"
      }
    },
    {
      "field_id": "is_over_18",
      "page_number": 1,
      "description": "Checkbox for age verification",
      "field_label": "Yes",
      "field_type": "checkbox",
      "label_bounding_box": [100, 525, 132, 540],
      "entry_bounding_box": [140, 525, 155, 540]
    }
  ]
}
```

**Key points**:
- `field_id`: Unique identifier for Chatfield interview
- `field_type`: "text", "checkbox", or other types (maps to Chatfield transformations)
- `description`: Used for Chatfield interview questions
- Bounding boxes are `[left, top, right, bottom]` in pixels
- **Do NOT include `entry_text.text` values** - these come from Chatfield conversation

Create validation images by running this script from this file's directory for each page:
`python scripts/create_validation_image.py <page_number> <path_to_fields.json> <input_image_path> <output_image_path>

The validation images will have red rectangles where text should be entered, and blue rectangles covering label text.

### Step 3: Validate Bounding Boxes (REQUIRED)
#### Automated intersection check
- Verify that none of bounding boxes intersect and that the entry bounding boxes are tall enough by checking the fields.json file with the `check_bounding_boxes.py` script (run from this file's directory):
`python scripts/check_bounding_boxes.py <JSON file>`

If there are errors, reanalyze the relevant fields, adjust the bounding boxes, and iterate until there are no remaining errors. Remember: label (blue) bounding boxes should contain text labels, entry (red) boxes should not.

#### Manual image inspection
**CRITICAL: Do not proceed without visually inspecting validation images**
- Red rectangles must ONLY cover input areas
- Red rectangles MUST NOT contain any text
- Blue rectangles should contain label text
- For checkboxes:
  - Red rectangle MUST be centered on the checkbox square
  - Blue rectangle should cover the text label for the checkbox

- If any rectangles look wrong, fix fields.json, regenerate the validation images, and verify again. Repeat this process until the bounding boxes are fully accurate.

### Step 4: Generate Chatfield Interview (REQUIRED)

Generate a Chatfield interview script from your field definitions:

```bash
python scripts/generate_chatfield_interview_nonfillable.py fields.json interview.py
```

**What this does**:
- Reads `field_id`, `field_type`, and `description` from fields.json
- Generates Chatfield interview with appropriate transformations:
  - `field_type: "text"` → `.field("field_id")`
  - `field_type: "checkbox"` → `.field("field_id").as_bool()`
  - Other types map similarly to fillable form workflow
- Creates conversion logic to:
  - Run Chatfield conversation
  - Map interview results back to fields.json structure
  - Populate `entry_text.text` values (and "X" for checked checkboxes)
  - Accept `--fields-json` and `--output` arguments

### Step 5: Customize Interview (RECOMMENDED)

Edit `interview.py` to improve the conversational experience. **See ./chatfield.md for complete API reference.**

**Recommended improvements**:
- Replace generic descriptions with clear questions using `.desc()`
- Add validation rules with `.must()` and `.reject()`
- Add helpful hints with `.hint()`
- Configure interview and participant roles with `.alice()` and `.bob()`

### Step 6: Run Conversational Interview

Collect data through conversation:

```bash
export OPENAI_API_KEY=your-key
python interview.py --fields-json fields.json --output fields_completed.json
```

**What this does**:
- Runs Chatfield conversation to collect all field values
- Maps interview results back to the fields.json structure
- Populates `entry_text.text` values for each field
- Outputs `fields_completed.json` with all data ready for annotation

### Step 7: Add annotations to the PDF

Use the completed fields.json to annotate the PDF:

```bash
python scripts/fill_pdf_form_with_annotations.py input.pdf fields_completed.json output.pdf
```

## Complete Example: Non-fillable Application Form

```bash
# 1. Convert to images for visual analysis
python scripts/convert_pdf_to_images.py application.pdf images/

# 2. Analyze images and create fields.json with:
#    - field_id, field_type, description for each field
#    - Bounding boxes (label_bounding_box, entry_bounding_box)
#    - DO NOT populate entry_text.text values yet
# Save as: application_fields.json

# 3. Create validation images
python scripts/create_validation_image.py 1 application_fields.json images/page_1.png validation_1.png
# Repeat for each page

# 4. Validate bounding boxes
python scripts/check_bounding_boxes.py application_fields.json
# Manually inspect validation images, fix any issues

# 5. Generate Chatfield interview
python scripts/generate_chatfield_interview_nonfillable.py application_fields.json application_interview.py

# 6. Customize application_interview.py
#    - Improve field descriptions
#    - Add validation rules
#    - Configure roles

# 7. Run conversation
export OPENAI_API_KEY=sk-...
python application_interview.py --fields-json application_fields.json --output application_completed.json

# 8. Annotate PDF
python scripts/fill_pdf_form_with_annotations.py application.pdf application_completed.json application_filled.pdf
```

## Key Differences: Fillable vs. Non-fillable

| Aspect | Fillable | Non-fillable |
|--------|----------|--------------|
| **Field Extraction** | Programmatic (`extract_form_field_info.py`) | Visual analysis + manual fields.json |
| **Field Metadata** | Automatic (IDs, types, options) | Manual (bounding boxes, types) |
| **Interview Generation** | `generate_chatfield_interview.py` | `generate_chatfield_interview_nonfillable.py` |
| **Chatfield Interview** | **Identical** | **Identical** |
| **Data Population** | `fill_fillable_fields.py` | `fill_pdf_form_with_annotations.py` |

**The Chatfield interview model is identical in both cases** - only the extraction and population mechanisms differ.
