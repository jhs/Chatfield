# Non-fillable PDF Forms with Chatfield

**MANDATORY: All non-fillable PDF forms MUST use the Chatfield conversational workflow.**

For non-fillable PDFs, the extraction process differs (visual bounding box analysis instead of programmatic field extraction), but the Chatfield interview model is identical.

**Documentation**:
- **../SKILL.md**: Workflow selection and shared Interview Validation Checklist
- **fillable-forms.md**: Fillable PDF workflow (alternative to this file)
- **This file (nonfillable-forms.md)**: Non-fillable PDF workflow orchestration and steps
- **api-reference.md**: Complete API reference (builder methods, transformations, validation, roles)

## Contents
- Workflow Overview
- Step 1: Visual Analysis (REQUIRED)
- Step 2: Create *_fields.json with field definitions (REQUIRED)
- Step 3: Validate Bounding Boxes (REQUIRED)
- Step 4: Define Interview in Server File (REQUIRED)
- Step 5: Customize Interview (RECOMMENDED)
- Step 6: Run Chatfield Server and Capture Results
- Step 7: Map Results to fields.json and Annotate PDF
- Complete Example: Non-fillable Application Form
- Key Differences: Fillable vs. Non-fillable
- Troubleshooting

## Workflow Overview

Copy this checklist and track progress:

```
Non-fillable PDF Form Progress:
- [ ] Step 1: Visual Analysis - Convert PDF to images and identify fields
- [ ] Step 2: Create fields.json with bounding boxes
- [ ] Step 3: Validate bounding boxes (automated + manual inspection)
- [ ] Step 4: Define interview in chatfield_interview.py
- [ ] Step 5: Customize interview (validate with Interview Validation Checklist in ../SKILL.md)
- [ ] Step 6: Run Chatfield server and capture results
- [ ] Step 7: Map results to fields.json and annotate PDF
```

**Stage 1: Visual Analysis** → Determine field locations and bounding boxes
**Stage 2: Interview Definition** → Edit `scripts/chatfield_interview.py` with Chatfield builder code
**Stage 3: Server Execution** → Start Chatfield server subprocess for browser-based data collection
**Stage 4: Data Collection** → User completes interview in browser, when done the server prints all results and exits
**Stage 5: PDF Population** → Parse server output and annotate PDF at bounding box locations

Follow the below steps *exactly* to ensure accurate form completion.

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

## Step 2: Create *_fields.json with field definitions (REQUIRED)

Create `*.fields.json` (i.e. the PDF filename with field metadata and bounding boxes. **Do NOT populate entry_text.text values yet** - these will come from the Chatfield conversation.

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

## Step 3: Validate Bounding Boxes (REQUIRED)

### Automated intersection check
- Verify that none of bounding boxes intersect and that the entry bounding boxes are tall enough by checking the fields.json file with the `check_bounding_boxes.py` script (run from this file's directory):
`python scripts/check_bounding_boxes.py <JSON file>`

If there are errors, reanalyze the relevant fields, adjust the bounding boxes, and iterate until there are no remaining errors. Remember: label (blue) bounding boxes should contain text labels, entry (red) boxes should not.

### Manual image inspection
**CRITICAL: Do not proceed without visually inspecting validation images**
- Red rectangles must ONLY cover input areas
- Red rectangles MUST NOT contain any text
- Blue rectangles should contain label text
- For checkboxes:
  - Red rectangle MUST be centered on the checkbox square
  - Blue rectangle should cover the text label for the checkbox

- If any rectangles look wrong, fix fields.json, regenerate the validation images, and verify again. Repeat this process until the bounding boxes are fully accurate.

## Step 4: Define Interview in Server File (REQUIRED)

Edit `scripts/chatfield_interview.py` with Chatfield builder code based on your field definitions:

**File to edit**: `scripts/chatfield_interview.py`

**Create builder code from fields.json**:
- Read `field_id`, `field_type`, and `description` from fields.json
- Build Chatfield interview with appropriate transformations:
  - `field_type: "text"` → `.field("field_id").desc(...)`
  - `field_type: "checkbox"` → `.field("field_id").as_bool().desc(...)`
  - Other types map similarly to fillable form workflow (see fillable-forms.md)

**Example**:
```python
interview = (chatfield()
    .type("ApplicationForm")
    .desc("Non-fillable PDF application")
    .field("last_name")
        .desc("What is your last name?")
        .must("be your legal last name")
    .field("is_over_18")
        .desc("Are you over 18 years old?")
        .as_bool()
    .build())
```

## Step 5: Customize Interview (RECOMMENDED)

Enhance the interview definition in `scripts/chatfield_interview.py` to improve user experience. **See api-reference.md for complete API reference.**

**Required configuration**:
- **Alice and Bob roles**: Always configure with `.alice().type()` and `.bob().type()` plus these traits:
  - **Alice traits**: "uses plain language when asking questions rather than strict field format rules" and "converts received plain language into the valid form data"
  - **Bob trait**: "speaks colloquially and plainly, needs help converting to the form format"
- **Bob type**: Use "Person completing <form name>" (e.g., "Person completing application form")

**Recommended improvements**:
- Replace generic descriptions with clear questions using `.desc()`
- Add validation rules with `.must()` and `.reject()`
- Add helpful hints with `.hint()`
- **Fan-out for related fields**: Use `.as_*()` casts to populate multiple fields from single value:
  ```python
  .field("age")
      .desc("What is your age in years?")
      .as_int("age_years", "Age as integer")
      .as_bool("over_18", "True if 18 or older")
      .as_str("age_display", "Age formatted for display")
  ```
- Add context-specific traits (e.g., "records optional fields as empty string when user indicates or implies no answer")

**Validate interview quality:**

Before proceeding to Step 6, use the **Interview Validation Checklist** in ../SKILL.md to verify the interview meets quality standards.

If any items fail validation:
1. Review the specific issue in the checklist
2. Fix the chatfield_interview.py definition
3. Re-run validation checklist
4. Proceed only when all items pass

## Step 6: Run Chatfield Server and Capture Results

Start the Chatfield server subprocess to collect data via browser-based interview (same as fillable workflow):

```python
import subprocess
import json

# Start server subprocess
proc = subprocess.Popen(
    ["python", "scripts/run_server.py", "--port", "0"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Capture SERVER_READY signal from stderr
for line in proc.stderr:
    if line.startswith("SERVER_READY:"):
        server_url = line.split("SERVER_READY:")[1].strip()
        break

# User completes interview in browser
# Server auto-shuts down when done

# Capture results from stdout
stdout, stderr = proc.communicate()
results = json.loads(stdout)  # Parse interview results
```

## Step 7: Map Results to fields.json and Annotate PDF

Extract field values from server output, populate fields.json, and annotate the PDF:

```python
# Load original fields.json
with open('fields.json', 'r') as f:
    fields_data = json.load(f)

# Populate entry_text.text values from interview results
for field in fields_data['form_fields']:
    field_id = field['field_id']
    field_value = results[field_id] if field_id in results._chatfield['fields'] else None

    if field_value is not None:
        if field['field_type'] == 'checkbox':
            # Checkbox: add "X" if checked
            is_checked = field_value.as_bool if hasattr(field_value, 'as_bool') else False
            field['entry_text']['text'] = "X" if is_checked else ""
        else:
            # Text field: use string value
            field['entry_text']['text'] = str(field_value)

# Save completed fields.json
with open('fields_completed.json', 'w') as f:
    json.dump(fields_data, f, indent=2)

# Annotate PDF with collected data
subprocess.run([
    "python", "scripts/fill_pdf_form_with_annotations.py",
    "input.pdf", "fields_completed.json", "output.pdf"
])
```

## Complete Example: Non-fillable Application Form

```bash
# 1. Convert to images for visual analysis
python scripts/convert_pdf_to_images.py application.pdf images/

# 2. Analyze images and create fields.json with:
#    - field_id, field_type, description for each field
#    - Bounding boxes (label_bounding_box, entry_bounding_box)
#    - DO NOT populate entry_text.text values yet
# Save as: application.fields.json

# 3. Create validation images
python scripts/create_validation_image.py 1 application.fields.json images/page_1.png validation_1.png
# Repeat for each page

# 4. Validate bounding boxes
python scripts/check_bounding_boxes.py application_fields.json
# Manually inspect validation images, fix any issues

# 5. Edit scripts/chatfield_interview.py
#    - Build interview from application_fields.json field definitions
#    - Add clear descriptions and validation rules
#    - Configure roles and traits

# 6. Start Chatfield server subprocess
#    - Server prints SERVER_READY to stderr
#    - Browser opens automatically
#    - User completes interview in browser
#    - Server auto-shuts down when done
#    - Capture results from stdout

# 7. Parse results and populate fields.json
#    - Map interview results to application_fields.json
#    - Populate entry_text.text values
#    - Save as application_completed.json

# 8. Annotate PDF
python scripts/fill_pdf_form_with_annotations.py application.pdf application_completed.json application_filled.pdf
```

## Key Differences: Fillable vs. Non-fillable

| Aspect | Fillable | Non-fillable |
|--------|----------|--------------|
| **Field Extraction** | Programmatic (`extract_form_field_info.py`) | Visual analysis + manual fields.json |
| **Field Metadata** | Automatic (IDs, types, options) | Manual (bounding boxes, types) |
| **Chatfield Interview** | **Identical** | **Identical** |
| **Data Population** | `fill_fillable_fields.py` | `fill_pdf_form_with_annotations.py` |

**The Chatfield interview model is identical in both cases** - only the extraction and population mechanisms differ.

## Troubleshooting

**Bounding box issues**:
- **Boxes overlap**: Entry boxes must not contain label text. Adjust boundaries.
- **Text doesn't fit**: Make entry boxes taller and wider. Check validation images.
- **Checkbox misalignment**: Entry box should cover only the checkbox square, not the label text.

**Chatfield issues**: See ./chatfield.md troubleshooting section for API key configuration, validation tuning, and field access patterns.
