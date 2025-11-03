# Converting PDF Forms to Chatfield

This guide provides considerations and best practices for converting PDF forms into Chatfield interview definitions.

## Overview

PDF forms are often complex, print-oriented documents with specific layouts and field placements. Converting them to Chatfield interviews requires extracting the essential data collection needs while leaving behind the layout constraints of the PDF format.

## Key Considerations

### 1. PDF Form Field Extraction

- **Field names**: PDF form fields have internal names—use these as Chatfield field identifiers
- **Field types**: Map PDF field types (text, checkbox, radio button, dropdown) to Chatfield transformations
- **Tooltips**: PDF fields may have tooltip text—excellent source for hints
- **Required fields**: Often marked with asterisks or visual indicators
- **Field validation**: Some PDFs have JavaScript validation—extract this logic

### 2. Layout vs. Logic

- **Ignore layout**: PDF layouts are for printing, not conversation flow
- **Focus on data**: What information does the form collect? Why?
- **Group related fields**: Fields visually grouped in the PDF are often logically related
- **Section headers**: Use these to understand field context and conversation flow

### 3. PDF-Specific Challenges

- **Tables**: PDF forms often use tables for layout—focus on the data, not the structure
- **Repeated sections**: "List all previous employers" might become `.as_list()` in Chatfield
- **Signature fields**: Consider whether these are needed in a conversational flow
- **Date fields**: Convert to `.must('be a valid date')` with appropriate format guidance

### 4. Text Content Analysis

- **Instructions**: Often contain valuable validation rules or hints
- **Legal text**: May inform what must be collected vs. optional
- **Examples**: "e.g., 555-1234" becomes `.hint('Format: 555-1234')`

## PDF Form Field Mapping

| PDF Field Type | Chatfield Equivalent |
|----------------|----------------------|
| Text Field | `.field(name).desc(desc)` |
| Checkbox | `.field().as_bool()` |
| Radio Button Group | `.field().as_one()` |
| Dropdown List | `.field().as_one()` or `.as_maybe()` |
| List Box (multi-select) | `.field().as_multi()` or `.as_any()` |
| Signature Field | Consider if needed; might be post-conversation |
| Date Field | `.field().must('be a valid date in MM/DD/YYYY format')` |
| Numeric Field | `.field().as_int()` or `.as_float()` |

### Handling Optional Fields

**IMPORTANT: Chatfield does not have an `.optional()` method.** When a PDF form field is marked as optional:

1. **For text fields**: Describe the field as optional in `.desc()` or `.hint()`:
   ```python
   .field("middle_name")
       .desc("Middle name (optional)")
   ```

2. **For choice fields**: Use optional cardinality methods:
   - `.as_maybe()` - select zero or one option
   - `.as_any()` - select zero or more options

3. **Avoid strict validation on optional fields**: Don't use `.must()` rules that would fail on empty responses

4. **The LLM understands optionality**: If you clearly describe a field as optional, the conversational agent will naturally allow users to skip it

**Example**:
```python
.field("business_name")
    .desc("Business name (leave blank if same as legal name)")
.field("preferred_contact")
    .desc("Preferred contact method (optional)")
    .as_maybe("method", "email", "phone", "mail")
```

## Workflow

1. **Extract PDF metadata**: Use PDF parsing tools to extract field names, types, and properties
2. **Read form instructions**: Understand the purpose and requirements from human-readable text
3. **Map fields**: Create Chatfield field for each PDF form field
4. **Extract validation**: Look for format requirements, ranges, required markers
5. **Analyze structure**: Use section headings and groupings to inform conversation flow
6. **Simplify**: Eliminate fields that exist only for PDF layout purposes (e.g., "Page X of Y")
7. **Test**: Ensure the conversational flow makes sense, not just that all fields are present

## Example Conversion

### PDF Form (W-9 Tax Form Example)
```
Name (as shown on your income tax return): _______________
Business name/disregarded entity name: _______________
Federal tax classification (check one):
  ☐ Individual/sole proprietor
  ☐ C Corporation
  ☐ S Corporation
  ☐ Partnership
  ☐ Trust/estate
  ☐ LLC (enter tax classification): _______________
Address: _______________
City, State, ZIP: _______________
Taxpayer Identification Number:
  ☐ Social Security Number: ___-__-____
  ☐ Employer Identification Number: __-_______
```

### Chatfield Interview
```python
from chatfield import chatfield

interview = chatfield()\
    .type('W-9 Tax Information')\
    .desc('Collecting taxpayer information for form W-9')\
    .field('legal_name')\
    .desc('Name as shown on your income tax return')\
        .must('match your tax records exactly')\
    .field('business_name')\
    .desc('Business name or disregarded entity name')\
        .hint('Leave blank if same as legal name')\
    .field('tax_classification')\
    .desc('Federal tax classification')\
        .as_one('selection',
                'Individual/sole proprietor',
                'C Corporation',
                'S Corporation',
                'Partnership',
                'Trust/estate',
                'LLC')\
    .field('llc_classification')\
    .desc('LLC tax classification')\
        .hint('Required only if you selected LLC above')\
    .field('address')\
    .desc('Street address')\
        .must('include street number and name')\
    .field('city')\
    .desc('City')\
    .field('state')\
    .desc('State')\
        .hint('Two-letter state code')\
    .field('zip')\
    .desc('ZIP code')\
        .must('be a valid 5-digit ZIP code')\
    .field('tin_type')\
    .desc('Taxpayer identification number type')\
        .as_one('selection', 'Social Security Number', 'Employer Identification Number')\
    .field('tin')\
    .desc('Taxpayer identification number')\
        .must('be in proper format (SSN: XXX-XX-XXXX or EIN: XX-XXXXXXX)')\
    .build()
```

## Advanced Patterns

### Repeated Sections (e.g., "List all dependents")

PDF forms often have fixed rows for repeated data. In Chatfield:
```python
.field('dependents')\
    .desc('List all dependents')\
    .as_list()\
    .hint('Include name, relationship, and date of birth for each')
```

Or use multiple conversations/interviews for complex repeated structures.

### Complex Tables

PDF tables often collect matrix data. Consider:
- Converting to multiple fields with clear descriptions
- Using `.as_dict()` or `.as_obj()` for structured data
- Breaking into multiple conversation turns

### Calculated Fields

PDFs sometimes have fields that auto-calculate. In Chatfield:
- Don't collect calculated values—compute them after the interview
- Or use `.conclude()` to have the LLM compute based on other fields

### PDF-Specific Metadata (Page numbers, form version, etc.)

Ignore these—they're artifacts of the PDF format, not data to collect.

## Tips for Natural Conversations

1. **Combine address fields**: Instead of separate fields for street, city, state, ZIP, consider one "address" field with smart parsing
2. **Handle conditional logic**: "If yes, explain" in PDFs becomes natural follow-up in conversation
3. **Simplify options**: Long dropdown lists in PDFs might become text fields with validation in Chatfield
4. **Progressive disclosure**: Don't ask everything upfront—let the conversation reveal complexity naturally
5. **Context matters**: PDF forms lack context—you can add it in field descriptions

## Extracting from PDF Tools

### Python PDF Parsing
```python
from PyPDF2 import PdfReader

reader = PdfReader('form.pdf')
fields = reader.get_fields()

for field_name, field in fields.items():
    field_type = field.get('/FT')  # Field type
    field_value = field.get('/V')   # Default value
    field_tooltip = field.get('/TU') # Tooltip
    # Map to Chatfield...
```

### Considerations for Scanned PDFs
- OCR may be needed to extract text
- Field boundaries might not be machine-readable
- Manual interpretation may be required

## See Also

- [CLAUDE/CORE_API_GUIDANCE.md](CORE_API_GUIDANCE.md) - Complete Chatfield API reference
- [Documentation/Builder_Api.md](../Documentation/Builder_Api.md) - Builder API details
- [Documentation/Cookbook.md](../Documentation/Cookbook.md) - Usage patterns and recipes
