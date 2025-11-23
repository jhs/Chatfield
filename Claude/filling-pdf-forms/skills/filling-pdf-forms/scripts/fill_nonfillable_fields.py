#!/usr/bin/env python3
"""
Fills a non-fillable PDF by adding text annotations.

This script reads:
- .form.json (field definitions with bounding boxes in PDF coordinates)
- .values.json (field values from the interview)

And creates an annotated PDF with the values placed at the specified locations.

Usage:
    python fill_nonfillable_fields.py <input.pdf> <basename>.chatfield/<basename>.values.json <output.pdf>
"""

import json
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.annotations import FreeText


def fill_nonfillable_pdf(input_pdf_path, values_json_path, output_pdf_path):
    """
    Fill a non-fillable PDF with text annotations.

    Args:
        input_pdf_path: Path to the input PDF file
        values_json_path: Path to .values.json file with field values
        output_pdf_path: Path to write the filled PDF
    """
    # Derive .form.json path from .values.json path
    values_path = Path(values_json_path)
    if not values_path.name.endswith('.values.json'):
        raise ValueError(f"Expected .values.json file, got: {values_path.name}")

    form_json_path = values_path.parent / values_path.name.replace('.values.json', '.form.json')

    if not form_json_path.exists():
        raise FileNotFoundError(
            f"Form definition file not found: {form_json_path}\n"
            f"Expected to find .form.json alongside .values.json"
        )

    # Load field definitions (with bounding boxes in PDF coordinates)
    with open(form_json_path, 'r') as f:
        form_fields = json.load(f)

    # Load field values
    with open(values_json_path, 'r') as f:
        values_data = json.load(f)

    # Create a lookup map: field_id -> value
    values_map = {field['field_id']: field['value'] for field in values_data['fields']}

    # Open the PDF
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # Copy all pages to writer
    writer.append(reader)

    # Process each form field
    annotations_added = 0

    for field_def in form_fields:
        field_id = field_def.get('field_id')

        # Get the value for this field
        if field_id not in values_map:
            # No value provided for this field, skip it
            continue

        value = values_map[field_id]

        # Skip empty values
        if not value:
            continue

        # Get field properties
        page_num = field_def.get('page', 1)
        rect = field_def.get('rect')

        if not rect:
            print(f"Warning: Field {field_id} has no rect, skipping", file=sys.stderr)
            continue

        # Default font settings
        # Note: Font size/color may not work reliably across all PDF viewers
        # https://github.com/py-pdf/pypdf/issues/2084
        font_name = "Arial"
        font_size = "12pt"
        font_color = "000000"  # Black

        # Create the annotation
        annotation = FreeText(
            text=str(value),
            rect=rect,  # Already in PDF coordinates
            font=font_name,
            font_size=font_size,
            font_color=font_color,
            border_color=None,
            background_color=None,
        )

        # Add annotation to the appropriate page (pypdf uses 0-based indexing)
        writer.add_annotation(page_number=page_num - 1, annotation=annotation)
        annotations_added += 1

    # Save the filled PDF
    with open(output_pdf_path, 'wb') as output:
        writer.write(output)

    print(f"Successfully filled PDF and saved to {output_pdf_path}")
    print(f"Added {annotations_added} text annotations")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: fill_nonfillable_fields.py <input.pdf> <basename>.values.json <output.pdf>")
        print()
        print("Example:")
        print("  python fill_nonfillable_fields.py form.pdf form.chatfield/form.values.json form.done.pdf")
        sys.exit(1)

    input_pdf = sys.argv[1]
    values_json = sys.argv[2]
    output_pdf = sys.argv[3]

    try:
        fill_nonfillable_pdf(input_pdf, values_json, output_pdf)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
