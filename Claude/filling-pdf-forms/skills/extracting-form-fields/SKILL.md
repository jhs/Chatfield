---
name: extracting-form-fields
description: Extract form field data from PDFs as a first step to filling PDF forms
allowed-tools: Read, Write, Edit, Glob, Bash
version: 1.0.0a2
license: Apache 2.0
---

# Extracting Form Fields

Prepare working directory and extract field data from PDF forms.

## Purpose

This skill extracts PDF form information into useful JSON.
- Detects fillable vs. non-fillable PDFs
- Extracts PDF content as readable Markdown
- Creates field metadata in common JSON format

## When to Use This Skill

Use when you need to extract form field information from a PDF as the first step in form filling workflows.

**Note**: This skill is typically invoked by the `filling-pdf-forms` skill via an agent, not used directly.

## Inputs

- **PDF path**: Absolute path to PDF file (e.g., `/home/user/input.pdf`)

## Outputs

For `input.pdf`, creates:
```
input.chatfield/
├── input.form.md           # PDF content as Markdown
├── input.form.json         # Field metadata
└── interview.py            # Form Data Model starting template
```

## Process

### 1. Check Fillability

```bash
python scripts/check_fillable_fields.py <pdf_path>
```

**Output:**
- `"This PDF has fillable form fields"` → use fillable workflow
- `"This PDF does not have fillable form fields; you will need to visually determine where to enter data"` → use non-fillable workflow

### 2. Create Working Directory

```bash
mkdir <basename>.chatfield
```

### 3. Extract PDF Content

```bash
markitdown <pdf_path> > <basename>.chatfield/<basename>.form.md
```

### 4. Branch Based on Fillability

#### If Fillable:
Follow ./references/fillable-forms.md:
- Use `scripts/extract_form_field_info.py` to create `.form.json`
- Extracts programmatic field metadata automatically

#### If Non-fillable:
Follow ./references/nonfillable-forms.md:
- Convert PDF to images using `scripts/convert_pdf_to_images.py`
- Guide visual analysis and bounding box creation
- Create `.fields.json` with field definitions
- Validate using `scripts/create_validation_image.py` and `scripts/check_bounding_boxes.py`

### 5. Copy Interview Template

Requires access to `filling-pdf-forms` skill's template:
```bash
cp ../filling-pdf-forms/scripts/chatfield_interview_template.py <basename>.chatfield/interview.py
```

## Output Format

### Fillable PDFs - .form.json

```json
[
  {
    "field_id": "topmostSubform[0].Page1[0].f1_01[0]",
    "type": "text",
    "page": 1,
    "rect": [100, 200, 300, 220],
    "tooltip": "Enter your full legal name",
    "max_length": null
  },
  {
    "field_id": "checkbox_over_18",
    "type": "checkbox",
    "page": 1,
    "rect": [150, 250, 165, 265],
    "checked_value": "/1",
    "unchecked_value": "/Off"
  }
]
```

### Non-fillable PDFs - .fields.json

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

## Completion Report

Return to calling skill:

```
Extraction complete for <pdf_path>:

Created:
- <basename>.chatfield/ directory
- <basename>.chatfield/<basename>.form.md (PDF content as Markdown)
- <basename>.chatfield/<basename>.form.json (field metadata for N fields)
  OR <basename>.chatfield/<basename>.fields.json (for non-fillable)
- <basename>.chatfield/interview.py (template ready for editing)

Form type: FILLABLE (or NON-FILLABLE)

Ready for Form Data Model creation.
```

## Scripts Reference

### Fillable PDF Scripts
- `check_fillable_fields.py` - Detect fillable fields
- `extract_form_field_info.py` - Extract programmatic field metadata
- `fill_fillable_fields.py` - Populate fillable PDF (used later by filling-pdf-forms)

### Non-fillable PDF Scripts
- `convert_pdf_to_images.py` - Convert PDF pages to PNG images
- `create_validation_image.py` - Visualize bounding boxes
- `check_bounding_boxes.py` - Validate field definitions
- `fill_pdf_form_with_annotations.py` - Annotate PDF visually (used later by filling-pdf-forms)

## References

- ./references/fillable-forms.md - Fillable PDF extraction workflow
- ./references/nonfillable-forms.md - Non-fillable PDF extraction workflow

## Integration

This skill is designed to be used by the `filling-pdf-forms` skill via the `extracting-form-fields` agent. The agent orchestrates this skill's resources to prepare the PDF for chatfield interview creation.
