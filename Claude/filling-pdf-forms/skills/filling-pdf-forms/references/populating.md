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

Create a JSON file with the collected field values:

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

### 3. Populate PDF

Run the population script (note, the `scripts` directory is relative to the base directory for this skill):

```bash
python scripts/fill_fillable_fields.py input.pdf input.values.json input.done.pdf
```

### 4. Verify Output

- Check that `input.done.pdf` was created
- Open in PDF viewer to verify all fields populated correctly
- Leave `<basename>.chatfield/` directory for inspection/debugging

## Complete Example

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

## Troubleshooting

**Missing fields:**
- Check that all field_ids from `.form.json` are in `.values.json`
- Verify field_id spelling matches exactly

**Wrong checkbox values:**
- Check `checked_value`/`unchecked_value` in `.form.json`
- Common values: `/1`, `/On`, `/Yes` for checked; `/Off`, `/No` for unchecked

**Type errors:**
- Ensure numeric fields use numbers, not strings: `25` not `"25"`
- Ensure boolean checkboxes use proper values from `.form.json`

---

**Result**: `input.done.pdf` (completed form ready for submission)
