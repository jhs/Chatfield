# Non-fillable PDF Forms - Extraction Guide

This guide is for the "extracting-form-fields" agent performing extraction on non-fillable PDFs.

The main skill uses ../../filling-pdf-forms/references/converting-pdf-to-chatfield.md for building the interview - this document focuses solely on the extraction process.

## What is a Non-fillable PDF?

A non-fillable PDF lacks programmatic form fields. Field locations must be identified visually and defined with bounding boxes for annotation.

## Extraction Process

### 1. Verify Non-fillability

```bash
python scripts/check_fillable_fields.py input.pdf
```

This script prints to stdout:
- `"This PDF has fillable form fields"` - Has fillable fields (use fillable-forms.md instead)
- `"This PDF does not have fillable form fields; you will need to visually determine where to enter data"` - No fillable fields (correct workflow for this guide)

### 2. Create Working Directory

```bash
# For input.pdf, create input.chatfield/
mkdir input.chatfield
```

### 3. Extract PDF Content as Markdown

```bash
markitdown input.pdf > input.chatfield/input.form.md
```

This provides readable PDF content that will be used later for:
- Understanding form purpose and context
- Extracting instructions and guidance
- Identifying field relationships

### 4. Convert PDF to Images

```bash
python scripts/convert_pdf_to_images.py input.pdf input.chatfield/images/
```

Creates PNG images for each page:
- `input.chatfield/images/page_1.png`
- `input.chatfield/images/page_2.png`
- etc.

### 5. Visual Analysis and Field Definition

**Analyze each PNG image** to identify form fields and determine bounding boxes.

For each field:
1. Identify the **label** (e.g., "Name:", "Date of Birth:")
2. Identify the **entry area** (where data should be written)
3. Define bounding box for the entry area ONLY (label and entry must not intersect)

**Common form structures:**

**Label inside box:**
```
┌────────────────────────┐
│ Name:                  │
└────────────────────────┘
```
Entry area: Right of "Name:" label to edge of box

**Label before line:**
```
Email: _______________________
```
Entry area: Above the line, full width

**Label under line:**
```
_________________________
Name
```
Entry area: Above the line, full width (common for signatures/dates)

**Label above line:**
```
Please enter special requests:
________________________________________________
```
Entry area: From bottom of label to line, full line width

**Checkboxes:**
```
Are you a US citizen? Yes □  No □
```
Define separate bounding boxes for each checkbox

### 6. Create .fields.json

Create `input.chatfield/input.fields.json` with field definitions:

```json
[
  {
    "field_id": "full_name",
    "type": "text",
    "page": 1,
    "label": {
      "text": "Full Name:",
      "bounding_box": {"x1": 50, "y1": 700, "x2": 150, "y2": 720}
    },
    "entry_text": {
      "bounding_box": {"x1": 160, "y1": 700, "x2": 500, "y2": 720}
    }
  },
  {
    "field_id": "is_citizen",
    "type": "checkbox",
    "page": 1,
    "label": {
      "text": "US Citizen",
      "bounding_box": {"x1": 50, "y1": 650, "x2": 150, "y2": 670}
    },
    "checkbox": {
      "bounding_box": {"x1": 155, "y1": 650, "x2": 170, "y2": 665}
    }
  }
]
```

**Field structure:**
- `field_id` - Unique identifier (will be used in chatfield definition)
- `type` - "text" or "checkbox"
- `page` - Page number (1-indexed)
- `label` - Optional label information
  - `text` - Label text
  - `bounding_box` - Label coordinates
- For text fields: `entry_text.bounding_box` - Where text will be written
- For checkboxes: `checkbox.bounding_box` - Where checkmark will appear

**Bounding box coordinates:**
- PDF coordinate system: Origin (0,0) at bottom-left
- Format: `{"x1": left, "y1": bottom, "x2": right, "y2": top}`
- Entry boxes must be tall and wide enough to contain text
- Checkboxes should be at least 15x15 pixels

### 7. Validate Bounding Boxes

**Create validation image:**
```bash
python scripts/create_validation_image.py \
  input.pdf \
  input.chatfield/input.fields.json \
  input.chatfield/validation.pdf
```

This overlays colored rectangles on the PDF to visualize bounding boxes.

**Automated validation:**
```bash
python scripts/check_bounding_boxes.py \
  input.chatfield/input.fields.json \
  input.chatfield/images/
```

Checks for:
- Label/entry bounding box intersections (must not overlap)
- Boxes outside page boundaries
- Boxes too small to contain text
- Missing required fields

**Review validation.pdf:**
- Open in PDF viewer
- Verify boxes align with form fields
- Adjust coordinates in `.fields.json` if needed
- Re-run validation until all checks pass

### 8. Copy Interview Template

```bash
cp scripts/chatfield_interview_template.py input.chatfield/interview.py
```

This creates the template file that the main skill will edit to build the Form Data Model.

## Completion Report

After extraction and validation, report back to the main skill:

```
Extraction complete for input.pdf:

Created:
- input.chatfield/ directory
- input.chatfield/input.form.md (PDF content as Markdown)
- input.chatfield/input.fields.json (field metadata for 12 fields)
- input.chatfield/images/ (3 page images)
- input.chatfield/validation.pdf (bounding box visualization)
- input.chatfield/interview.py (template ready for editing)

Form type: NON-FILLABLE (visual annotation required)

Validation: All bounding boxes verified and validated

Ready for Form Data Model creation using converting-pdf-to-chatfield.md
```

## Notes for Main Skill

The `.fields.json` file provides:
- **Field IDs**: Use exactly as-is for `.field()` calls or cast names
- **Field types**: Determines whether to use `.as_bool()` for checkboxes
- **Bounding boxes**: Will be used later during PDF population (see populating.md)

The main skill will build the chatfield interview by reading both `.form.md` (for context/instructions) and `.fields.json` (for field structure), just like with fillable PDFs.

## Troubleshooting

**Bounding boxes don't align:**
- Review validation.pdf
- Adjust coordinates in `.fields.json`
- Remember: PDF coordinates start at bottom-left (0,0)
- Re-run validation after changes

**Text gets cut off:**
- Increase bounding box height and/or width
- Entry boxes should have extra space for text

**Validation script errors:**
- Ensure all page images exist in `images/` directory
- Verify JSON syntax in `.fields.json`
- Check that page numbers are 1-indexed

---

**See Also:**
- ../../filling-pdf-forms/references/converting-pdf-to-chatfield.md - How the main skill builds the interview
- ./fillable-forms.md - Alternative extraction for fillable PDFs
- ../../filling-pdf-forms/references/populating.md - How bounding boxes are used during PDF population
