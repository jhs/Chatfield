#!/usr/bin/env python3
"""
Generate Chatfield Interview Script from Non-Fillable PDF Form Fields
======================================================================

This script generates a Python Chatfield interview script from non-fillable PDF
form field definitions (with bounding boxes).

Usage:
    python generate_chatfield_interview_nonfillable.py <fields.json> <output_interview.py>

Input:
    fields.json - JSON file with field definitions and bounding boxes from visual analysis

Output:
    Python script that:
    - Conducts Chatfield interview for each form field
    - Saves results by populating entry_text values in fields.json format
"""

import json
import os
import sys
from pathlib import Path


def field_id_to_description(field_id, existing_desc=None):
    """Convert field_id to natural language description."""
    if existing_desc:
        return existing_desc

    # Replace underscores and dots with spaces
    readable = field_id.replace('_', ' ').replace('.', ' ')
    # Capitalize first letter
    readable = readable.strip()
    if readable:
        readable = readable[0].upper() + readable[1:]
    return f"What is your {readable}?"


def generate_field_builder_code(field, indent=4):
    """Generate Chatfield builder code for a single field."""
    spaces = ' ' * indent
    field_id = field['field_id']
    field_type = field.get('field_type', 'text')

    # Start with field definition
    lines = [f'{spaces}.field("{field_id}")']

    # Add description
    desc = field_id_to_description(field_id, field.get('description'))
    lines.append(f'{spaces}    .desc("{desc}")')

    # Add type-specific transformations
    if field_type == 'checkbox':
        lines.append(f'{spaces}    .as_bool()')
    # Add more type mappings as needed

    return lines


def generate_interview_script(fields_json_path, output_path):
    """Generate complete Chatfield interview Python script."""

    # Read fields.json
    with open(fields_json_path) as f:
        fields_data = json.load(f)

    form_fields = fields_data.get('form_fields', [])

    if not form_fields:
        print("Error: No form_fields found in fields.json")
        sys.exit(1)

    # Generate script content
    script_lines = [
        '#!/usr/bin/env python3',
        '"""',
        'Chatfield Interview for Non-Fillable PDF Form',
        '==============================================',
        '',
        'Auto-generated from non-fillable PDF form field definitions.',
        'Customize this script to add validation, better descriptions, etc.',
        '',
        'Usage:',
        '    python SCRIPT_NAME --fields-json <fields.json> --output <output.json>',
        '"""',
        '',
        'import os',
        'import sys',
        'import json',
        'import argparse',
        'from pathlib import Path',
        '',
        '# Import Chatfield - adjust path if needed',
        'chatfield_path = Path(__file__).parent.parent.parent.parent / "Python"',
        'if chatfield_path.exists():',
        '    sys.path.insert(0, str(chatfield_path))',
        '',
        'from chatfield import chatfield, Interviewer',
        '',
        '',
        'def create_interview():',
        '    """Build the Chatfield interview."""',
        '    return (chatfield()',
        '        .type("PDFFormInterview")',
        '        .desc("PDF Form Data Collection")',
        '',
    ]

    # Add field definitions
    for field in form_fields:
        field_lines = generate_field_builder_code(field, indent=8)
        script_lines.extend(field_lines)
        script_lines.append('')  # Blank line between fields

    script_lines.extend([
        '        .build())',
        '',
        '',
        'def run_interview(fields_json_path, output_path):',
        '    """Run the interview and save results."""',
        '    # Load original fields.json',
        '    with open(fields_json_path) as f:',
        '        fields_data = json.load(f)',
        '    ',
        '    interview = create_interview()',
        '    ',
        '    print("=" * 60)',
        '    print("PDF Form Interview")',
        '    print("=" * 60)',
        '    print()',
        '    ',
        '    interviewer = Interviewer(interview)',
        '    user_input = None',
        '    ',
        '    while not interview._done:',
        '        message = interviewer.go(user_input)',
        '        ',
        '        if message:',
        '            print(f"\\nAssistant: {message}")',
        '        ',
        '        if not interview._done:',
        '            try:',
        '                user_input = input("\\nYou: ").strip()',
        '            except (KeyboardInterrupt, EOFError):',
        '                print("\\n[Interview ended by user]")',
        '                return False',
        '    ',
        '    if not interview._done:',
        '        print("\\n[Interview not completed]")',
        '        return False',
        '    ',
        '    print("\\n[Interview complete]")',
        '    ',
        '    # Map interview results back to fields.json structure',
    ])

    # Add conversion code for each field
    script_lines.append('    # Populate entry_text values for each field')
    script_lines.append('    for field in fields_data.get("form_fields", []):')
    script_lines.append('        field_id = field["field_id"]')
    script_lines.append('        field_type = field.get("field_type", "text")')
    script_lines.append('        field_val = getattr(interview, field_id, None)')
    script_lines.append('        ')
    script_lines.append('        if field_val is not None:')
    script_lines.append('            # Initialize entry_text if not present')
    script_lines.append('            if "entry_text" not in field:')
    script_lines.append('                field["entry_text"] = {}')
    script_lines.append('            ')
    script_lines.append('            # Set text value based on field type')
    script_lines.append('            if field_type == "checkbox":')
    script_lines.append('                # Use "X" for checked, empty for unchecked')
    script_lines.append('                field["entry_text"]["text"] = "X" if field_val.as_bool else ""')
    script_lines.append('            else:')
    script_lines.append('                # Text fields - use string value')
    script_lines.append('                field["entry_text"]["text"] = str(field_val)')
    script_lines.append('')

    script_lines.extend([
        '    # Save completed fields.json',
        '    with open(output_path, "w") as f:',
        '        json.dump(fields_data, f, indent=2)',
        '    ',
        '    field_count = len(fields_data.get("form_fields", []))',
        '    print(f"\\nPopulated {field_count} field values in {output_path}")',
        '    return True',
        '',
        '',
        'def main():',
        '    """Main entry point."""',
        '    parser = argparse.ArgumentParser(description="PDF Form Interview (Non-fillable)")',
        '    parser.add_argument("--fields-json", required=True,',
        '                        help="Input fields.json with field definitions")',
        '    parser.add_argument("--output", required=True,',
        '                        help="Output JSON file with populated entry_text values")',
        '    args = parser.parse_args()',
        '    ',
        '    # Check for API key',
        '    if not os.getenv("OPENAI_API_KEY"):',
        '        print("Error: OPENAI_API_KEY not found in environment")',
        '        print("Please set your OpenAI API key")',
        '        sys.exit(1)',
        '    ',
        '    # Check input file exists',
        '    if not Path(args.fields_json).exists():',
        '        print(f"Error: Input file not found: {args.fields_json}")',
        '        sys.exit(1)',
        '    ',
        '    success = run_interview(args.fields_json, args.output)',
        '    sys.exit(0 if success else 1)',
        '',
        '',
        'if __name__ == "__main__":',
        '    main()',
    ])

    # Replace script name placeholder in docstring
    script_name = Path(output_path).name
    script_content = '\n'.join(script_lines).replace('SCRIPT_NAME', script_name)

    # Write output file
    with open(output_path, 'w') as f:
        f.write(script_content)

    # Make executable
    os.chmod(output_path, 0o755)

    print(f"Generated Chatfield interview script: {output_path}")
    print(f"Found {len(form_fields)} form fields")
    print()
    print("Next steps:")
    print(f"1. (Optional) Customize {output_path} to add validation, better descriptions, etc.")
    print(f"2. Run: python {output_path} --fields-json <fields.json> --output <output.json>")
    print(f"3. Fill PDF: python scripts/fill_pdf_form_with_annotations.py <input.pdf> <output.json> <result.pdf>")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: generate_chatfield_interview_nonfillable.py <fields.json> <output_interview.py>")
        sys.exit(1)

    fields_json_path = sys.argv[1]
    output_path = sys.argv[2]

    if not Path(fields_json_path).exists():
        print(f"Error: Fields file not found: {fields_json_path}")
        sys.exit(1)

    generate_interview_script(fields_json_path, output_path)
