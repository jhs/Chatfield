#!/usr/bin/env python3
"""
Generate Chatfield Interview Script from PDF Form Fields
=========================================================

This script generates a Python Chatfield interview script from PDF form field metadata.

Usage:
    python generate_chatfield_interview.py <field_info.json> <output_interview.py>

Input:
    field_info.json - JSON file from extract_form_field_info.py containing form fields

Output:
    Python script that:
    - Conducts Chatfield interview for each form field
    - Saves results in field_values.json format for fill_fillable_fields.py
"""

import json
import os
import sys
from pathlib import Path


def field_id_to_description(field_id):
    """Convert field_id to natural language description."""
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
    field_type = field['type']

    # Start with field definition
    lines = [f'{spaces}.field("{field_id}")']

    # Add description
    desc = field_id_to_description(field_id)
    lines.append(f'{spaces}    .desc("{desc}")')

    # Add type-specific transformations
    if field_type == 'checkbox':
        lines.append(f'{spaces}    .as_bool()')
    elif field_type == 'radio_group':
        # Extract option values from radio_options
        options = field.get('radio_options', [])
        if options:
            option_values = [opt['value'] for opt in options]
            # Format as string literals
            option_strs = ', '.join(f'"{v}"' for v in option_values)
            lines.append(f'{spaces}    .as_one({option_strs})')
    elif field_type == 'choice':
        # Extract option values from choice_options
        options = field.get('choice_options', [])
        if options:
            option_values = [opt['value'] for opt in options]
            # Format as string literals
            option_strs = ', '.join(f'"{v}"' for v in option_values)
            lines.append(f'{spaces}    .as_one({option_strs})')

    return lines


def convert_field_value_to_pdf_format(field_info, interview_obj, field_id):
    """Generate code to convert interview field value to PDF format."""
    field_type = field_info['type']

    if field_type == 'checkbox':
        checked_val = field_info.get('checked_value', '/On')
        unchecked_val = field_info.get('unchecked_value', '/Off')
        return f'''    # Checkbox field
    field_val = interview["{field_id}"] if "{field_id}" in interview._chatfield['fields'] else None
    if field_val is not None:
        value = "{checked_val}" if field_val.as_bool else "{unchecked_val}"
        field_values.append({{
            "field_id": "{field_id}",
            "page": {field_info['page']},
            "value": value
        }})'''
    else:
        # Text, radio_group, choice - just use the string value
        return f'''    # {field_type} field
    field_val = interview["{field_id}"] if "{field_id}" in interview._chatfield['fields'] else None
    if field_val is not None:
        field_values.append({{
            "field_id": "{field_id}",
            "page": {field_info['page']},
            "value": str(field_val)
        }})'''


def generate_interview_script(field_info_path, output_path):
    """Generate complete Chatfield interview Python script."""

    # Read field info
    with open(field_info_path) as f:
        fields = json.load(f)

    if not fields:
        print("Error: No fields found in field_info.json")
        sys.exit(1)

    # Generate script content
    script_lines = [
        '#!/usr/bin/env python3',
        '"""',
        'Chatfield Interview for PDF Form',
        '=================================',
        '',
        'Auto-generated from PDF form fields.',
        'Customize this script to add validation, better descriptions, etc.',
        '',
        'Usage:',
        '    python SCRIPT_NAME [--output field_values.json]',
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
    for field in fields:
        field_lines = generate_field_builder_code(field, indent=8)
        script_lines.extend(field_lines)
        script_lines.append('')  # Blank line between fields

    script_lines.extend([
        '        .build())',
        '',
        '',
        'def run_interview(output_path):',
        '    """Run the interview and save results."""',
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
        '    # Convert interview results to field_values.json format',
        '    field_values = []',
        '',
    ])

    # Add conversion code for each field
    for field in fields:
        conversion_code = convert_field_value_to_pdf_format(field, 'interview', field['field_id'])
        script_lines.append(conversion_code)
        script_lines.append('')

    script_lines.extend([
        '    # Save to JSON',
        '    with open(output_path, "w") as f:',
        '        json.dump(field_values, f, indent=2)',
        '    ',
        '    print(f"\\nSaved {len(field_values)} field values to {output_path}")',
        '    return True',
        '',
        '',
        'def main():',
        '    """Main entry point."""',
        '    parser = argparse.ArgumentParser(description="PDF Form Interview")',
        '    parser.add_argument("--output", default="field_values.json",',
        '                        help="Output JSON file for field values")',
        '    args = parser.parse_args()',
        '    ',
        '    # Check for API key',
        '    if not os.getenv("OPENAI_API_KEY"):',
        '        print("Error: OPENAI_API_KEY not found in environment")',
        '        print("Please set your OpenAI API key")',
        '        sys.exit(1)',
        '    ',
        '    success = run_interview(args.output)',
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
    print(f"Found {len(fields)} form fields")
    print()
    print("Next steps:")
    print(f"1. (Optional) Customize {output_path} to add validation, better descriptions, etc.")
    print(f"2. Run: python {output_path} --output field_values.json")
    print(f"3. Fill PDF: python scripts/fill_fillable_fields.py <input.pdf> field_values.json <output.pdf>")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: generate_chatfield_interview.py <field_info.json> <output_interview.py>")
        sys.exit(1)

    field_info_path = sys.argv[1]
    output_path = sys.argv[2]

    if not Path(field_info_path).exists():
        print(f"Error: Field info file not found: {field_info_path}")
        sys.exit(1)

    generate_interview_script(field_info_path, output_path)
