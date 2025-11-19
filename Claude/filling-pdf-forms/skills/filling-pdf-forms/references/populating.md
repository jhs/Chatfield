# Populating PDF Forms

After collecting data via Chatfield interview, populate the PDF with the results.

## Prerequisites

- Completed Chatfield interview (server has exited)
- Server output captured (field values in stdout)
- Original PDF file
- Working directory (`<basename>.chatfield/`) with `.form.json`

## Process

### 1. Parse Server Output

Server outputs collected data to stdout in format:

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

Extract `field_id` and `value` for each field.

### 2. Create `.values.json`

The format differs for fillable vs. non-fillable PDFs.

#### For Fillable PDFs

```json
[
  {"field_id": "name", "page": 1, "value": "Jason Smith"},
  {"field_id": "age_years", "page": 1, "value": 25},
  {"field_id": "age_display", "page": 1, "value": "25"},
  {"field_id": "checkbox_over_18", "page": 1, "value": "/1"}
]
```

**Boolean conversion for checkboxes:**
- Read `.form.json` for `checked_value` and `unchecked_value`
- Typically: `"/1"` or `"/On"` for checked, `"/Off"` for unchecked
- Convert Python `True`/`False` → PDF checkbox values

#### For Non-fillable PDFs

```json
[
  {
    "field_id": "name",
    "page": 1,
    "entry_text": {
      "text": "Jason Smith",
      "bounding_box": {"x1": 100, "y1": 200, "x2": 300, "y2": 220}
    }
  },
  {
    "field_id": "checkbox_citizen",
    "page": 1,
    "checkbox": {
      "checked": true,
      "bounding_box": {"x1": 150, "y1": 250, "x2": 165, "y2": 265}
    }
  }
]
```

**Mapping from `.fields.json`:**
- Copy bounding boxes from `.fields.json` to `.values.json`
- For text entries: Use `entry_text.bounding_box`
- For checkboxes: Use `checkbox.bounding_box`

**Checkbox handling:**
- If server output `value` is `true` or `"true"` → `"checked": true`
- If server output `value` is `false` or `"false"` → `"checked": false`

### 3. Populate PDF

The command differs for fillable vs. non-fillable PDFs.

#### For Fillable PDFs

```bash
python scripts/fill_fillable_fields.py input.pdf input.values.json input.done.pdf
```

#### For Non-fillable PDFs

```bash
python scripts/fill_pdf_form_with_annotations.py \
  input.pdf \
  input.chatfield/input.fields.json \
  input.values.json \
  input.done.pdf
```

### 4. Verify Output

- Check that `input.done.pdf` was created
- Open in PDF viewer to verify all fields populated correctly
- Leave `<basename>.chatfield/` directory for inspection/debugging

## Complete Examples

### Fillable PDF Example

```bash
# 1. Parse server output (manual extraction from stdout)
# Server printed: {'name': {'value': 'Jason Smith'}, 'age': {'value': '25'}, 'over_18': {'value': true}}

# 2. Create values.json
cat > input.values.json << 'EOF'
[
  {"field_id": "name", "page": 1, "value": "Jason Smith"},
  {"field_id": "age", "page": 1, "value": 25},
  {"field_id": "over_18", "page": 1, "value": "/1"}
]
EOF

# 3. Fill PDF
python scripts/fill_fillable_fields.py input.pdf input.values.json input.done.pdf
```

### Non-fillable PDF Example

```bash
# 1. Parse server output
# Server printed: {'name': {'value': 'Jason Smith'}, 'is_citizen': {'value': true}}

# 2. Read bounding boxes from input.chatfield/input.fields.json
# (Fields were defined during form-extract with visual analysis)

# 3. Create values.json with bounding boxes from .fields.json
cat > input.values.json << 'EOF'
[
  {
    "field_id": "name",
    "page": 1,
    "entry_text": {
      "text": "Jason Smith",
      "bounding_box": {"x1": 100, "y1": 200, "x2": 300, "y2": 220}
    }
  },
  {
    "field_id": "is_citizen",
    "page": 1,
    "checkbox": {
      "checked": true,
      "bounding_box": {"x1": 150, "y1": 250, "x2": 165, "y2": 265}
    }
  }
]
EOF

# 4. Fill PDF
python scripts/fill_pdf_form_with_annotations.py \
  input.pdf \
  input.chatfield/input.fields.json \
  input.values.json \
  input.done.pdf
```

## Troubleshooting

### Fillable PDFs

**Missing fields:**
- Check that all field_ids from `.form.json` are in `.values.json`
- Verify field_id spelling matches exactly

**Wrong checkbox values:**
- Check `checked_value`/`unchecked_value` in `.form.json`
- Common values: `/1`, `/On`, `/Yes` for checked; `/Off`, `/No` for unchecked

**Type errors:**
- Ensure numeric fields use numbers, not strings: `25` not `"25"`
- Ensure boolean checkboxes use proper values from `.form.json`

### Non-fillable PDFs

**Text not appearing:**
- Check bounding boxes in `.fields.json`
- Verify coordinates are correct for the PDF page

**Text cut off:**
- Expand bounding box height/width in `.fields.json`
- Rerun validation image to verify new boxes

**Wrong position:**
- Use validation image from form-extract step
- Adjust coordinates in `.fields.json`
- Remember: PDF coordinates start at bottom-left (0,0)

**Checkbox not showing:**
- Ensure bounding box is large enough (minimum 15x15 pixels)
- Verify checkbox coordinates align with form checkbox location

**Script errors:**
- Ensure `.fields.json` has correct structure
- Verify all referenced images exist in `.chatfield/images/`
- Check that page numbers are 1-indexed

---

**Result**: `input.done.pdf` (completed form ready for submission)
