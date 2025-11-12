# Converting Forms from Screenshots to Chatfield

This guide provides considerations and best practices for converting forms captured as screenshots into Chatfield interview definitions.

## Overview

Screenshots provide visual representation of forms but lack structured data. Converting screenshots to Chatfield requires visual analysis, text extraction (OCR), and interpretation of layout, labels, and validation cues.

## Key Considerations

### 1. Visual Analysis

- **Field labels**: Identify labels and their associated input fields
- **Field types**: Infer from visual appearance (text boxes, checkboxes, dropdowns)
- **Required indicators**: Look for asterisks (*), "required" text, or visual emphasis
- **Help text**: Identify tooltips, placeholder text, or explanatory notes
- **Validation messages**: Note any visible error messages or format examples

### 2. Layout Interpretation

- **Grouping**: Visually grouped fields are often logically related
- **Section headers**: Use to understand context and conversation flow
- **Field order**: May indicate intended completion sequence
- **Conditional visibility**: Grayed-out or hidden fields suggest dependencies

### 3. OCR and Text Extraction

- **Label text**: Extract field labels and descriptions
- **Placeholder text**: Often contains format guidance or examples
- **Button text**: "Submit", "Next", "Continue" may indicate multi-step flows
- **Error messages**: If visible, use to infer validation rules

### 4. Inferring Validation Rules

Since screenshots don't contain code, you must infer:
- **Format examples**: "555-1234" suggests phone number format
- **Field length**: Visual width may suggest expected input length
- **Special characters**: Masked fields (••••) suggest passwords
- **Dropdown options**: Visible options in screenshots should be extracted

## Workflow

1. **OCR extraction**: Use OCR tools to extract text from screenshot
2. **Identify fields**: List all input fields, checkboxes, dropdowns, etc.
3. **Map relationships**: Connect labels to fields, group related fields
4. **Infer types**: Determine field types from visual appearance
5. **Extract validation cues**: Note required indicators, format examples, hints
6. **Create Chatfield definition**: Build interview with extracted information
7. **Validate assumptions**: Test conversational flow and adjust as needed

## Visual Cue Mapping

| Visual Cue | Likely Meaning | Chatfield Equivalent |
|------------|----------------|----------------------|
| Asterisk (*) after label | Required field | Implicit (all fields required by default) |
| "Optional" text | Not required | Consider if truly needed |
| Placeholder "e.g., ..." | Example format | `.hint('e.g., ...')` |
| Masked input (•••) | Password field | Depends on use case |
| Dropdown arrow | Select field | `.as_one()` or `.as_maybe()` |
| Multiple checkboxes | Multi-select | `.as_multi()` or `.as_any()` |
| Single checkbox | Boolean field | `.as_bool()` |
| Radio buttons | Single choice | `.as_one()` |
| Calendar icon | Date field | `.must('be a valid date')` |
| Number spinner | Numeric input | `.as_int()` or `.as_float()` |

## Example Conversion

### Screenshot Description
```
[Form: "Contact Us"]

Name: [___________] *
Email: [___________] *
Phone: [___________] (e.g., 555-1234)
Subject: [Dropdown: "General", "Support", "Sales"] *
Message: [_______________________]
         [                       ]
         [_______________________]
☐ Subscribe to newsletter

[Submit Button]
```

### Chatfield Interview
```python
from chatfield import chatfield

interview = chatfield()\
    .type('Contact Us Form')\
    .desc('Contact form submission')\
    .field('name')\
    .desc('Your name')\
        .must('be provided')\
    .field('email')\
    .desc('Email address')\
        .must('be a valid email format')\
    .field('phone')\
    .desc('Phone number')\
        .hint('Format: 555-1234')\
    .field('subject')\
    .desc('Subject of inquiry')\
        .as_one('selection', 'General', 'Support', 'Sales')\
    .field('message')\
    .desc('Your message')\
        .must('be provided')\
    .field('newsletter')\
    .desc('Newsletter subscription')\
        .as_bool()\
    .build()
```

## Advanced Patterns

### Multi-Page Forms (Multiple Screenshots)

If you have screenshots of multiple pages:
1. Identify the sequence (page 1, page 2, etc.)
2. Determine if steps are linear or conditional
3. Create single Chatfield interview with all fields in logical order
4. Consider using `.conclude()` for summary/confirmation fields

### Partially Filled Forms

Screenshots showing filled examples can reveal:
- Expected format (filled data demonstrates proper formatting)
- Validation rules (what values are accepted)
- Field relationships (how fields interact)

### Error State Screenshots

Screenshots showing validation errors are valuable:
- Extract exact error messages for validation rule guidance
- Note which fields failed validation
- Use error text to write `.must()` rules

## OCR Tools and Techniques

### Command-line OCR (Tesseract)
```bash
tesseract screenshot.png output.txt
```

### Python with OCR
```python
from PIL import Image
import pytesseract

image = Image.open('screenshot.png')
text = pytesseract.image_to_string(image)
print(text)
```

### Advanced: Layout Detection
Use tools that detect UI elements (not just text):
- OpenCV for field boundary detection
- ML models trained on UI screenshots
- Manual annotation for complex layouts

## Tips for Accurate Conversion

1. **High-quality screenshots**: Higher resolution = better OCR accuracy
2. **Multiple screenshots**: Capture normal state, hover states, error states
3. **Interactive elements**: Note dropdown options, calendar pickers, etc.
4. **Context matters**: Understand the purpose of the form to infer missing validation
5. **Test assumptions**: If you infer a rule, test it conversationally to ensure it makes sense

## Limitations and Workarounds

### Screenshots Don't Show:
- **JavaScript validation logic**: Infer from error messages or field behavior
- **Backend validation**: May need to test the actual form to discover server-side rules
- **Dynamic field updates**: Conditional fields may not be visible in a single screenshot
- **All dropdown options**: May need to capture expanded dropdown state

### Workarounds:
- Capture multiple states (before/after interactions)
- Inspect live form if available (use Playwright MCP approach)
- Make educated guesses based on common patterns
- Document assumptions for later refinement

## When to Use Screenshots vs. Live Inspection

| Scenario | Screenshot | Live Inspection (Playwright) |
|----------|-----------|------------------------------|
| Form no longer accessible | ✅ | ❌ |
| Quick visual reference | ✅ | ⚠️ |
| Need exact validation rules | ⚠️ | ✅ |
| Form has dynamic behavior | ❌ | ✅ |
| Need to capture all dropdown options | ⚠️ | ✅ |
| Form requires login | ⚠️ | ✅ |

## See Also

- [Builder_Api.md](Builder_Api.md) - Builder API details
- [Architecture.md](Architecture.md) - System architecture overview
- [Getting_Started_Python.md](Getting_Started_Python.md) - Python quickstart guide
- [Getting_Started_TypeScript.md](Getting_Started_TypeScript.md) - TypeScript quickstart guide
