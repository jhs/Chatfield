#!/usr/bin/env python3
"""
Converts bounding box coordinates from image coordinates to PDF coordinates.

This script takes a .scan.json file (with image coordinates) and converts all
bounding boxes to PDF coordinates, producing a .form.json file.

Image coordinates: Origin at top-left, Y increases downward
PDF coordinates: Origin at bottom-left, Y increases upward

Usage:
    python convert_coordinates.py <scan.json> <pdf_file>
"""

import json
import sys
from pathlib import Path

from PIL import Image
from pypdf import PdfReader


def image_to_pdf_coords(image_bbox, image_width, image_height, pdf_width, pdf_height):
    """
    Convert bounding box from image coordinates to PDF coordinates.

    Args:
        image_bbox: [x1, y1, x2, y2] in image coordinates (top-left origin)
        image_width: Width of the image in pixels
        image_height: Height of the image in pixels
        pdf_width: Width of the PDF page in points
        pdf_height: Height of the PDF page in points

    Returns:
        [x1, y1, x2, y2] in PDF coordinates (bottom-left origin)
    """
    x_scale = pdf_width / image_width
    y_scale = pdf_height / image_height

    # Convert X coordinates (simple scaling, same origin)
    pdf_x1 = image_bbox[0] * x_scale
    pdf_x2 = image_bbox[2] * x_scale

    # Convert Y coordinates (flip vertical axis)
    # Image: y1 is top, y2 is bottom (y1 < y2 in image coords)
    # PDF: need to flip - what's at top of image is high Y in PDF
    pdf_y1 = (image_height - image_bbox[3]) * y_scale  # Bottom in PDF (was bottom in image)
    pdf_y2 = (image_height - image_bbox[1]) * y_scale  # Top in PDF (was top in image)

    return [pdf_x1, pdf_y1, pdf_x2, pdf_y2]


def get_image_dimensions(images_dir, page_number):
    """Get dimensions of the PNG image for a specific page."""
    image_path = Path(images_dir) / f"page_{page_number}.png"
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    with Image.open(image_path) as img:
        return img.width, img.height


def convert_scan_to_form(scan_json_path, pdf_path, output_json_path):
    """
    Convert .scan.json (image coords) to .form.json (PDF coords).

    Args:
        scan_json_path: Path to input .scan.json file
        pdf_path: Path to the PDF file
        output_json_path: Path to output .form.json file
    """
    # Load scan data
    with open(scan_json_path, 'r') as f:
        fields = json.load(f)

    # Get PDF dimensions
    reader = PdfReader(pdf_path)

    # Determine images directory (same directory as scan.json)
    scan_path = Path(scan_json_path)
    images_dir = scan_path.parent

    if not images_dir.exists():
        raise FileNotFoundError(
            f"Images directory not found: {images_dir}\n"
            f"Expected to find page images in {images_dir}"
        )

    # Convert each field
    converted_fields = []

    for field in fields:
        page_num = field.get('page', 1)

        # Get dimensions for this page
        page = reader.pages[page_num - 1]  # Convert to 0-indexed
        pdf_width = float(page.mediabox.width)
        pdf_height = float(page.mediabox.height)
        image_width, image_height = get_image_dimensions(images_dir, page_num)

        # Create converted field
        converted_field = field.copy()

        # Convert main rect
        if 'rect' in field:
            converted_field['rect'] = image_to_pdf_coords(
                field['rect'],
                image_width, image_height,
                pdf_width, pdf_height
            )

        # Convert label_rect if present
        if 'label_rect' in field:
            converted_field['label_rect'] = image_to_pdf_coords(
                field['label_rect'],
                image_width, image_height,
                pdf_width, pdf_height
            )

        # Convert radio button options if present
        if 'radio_options' in field:
            converted_options = []
            for option in field['radio_options']:
                converted_option = option.copy()
                if 'rect' in option:
                    converted_option['rect'] = image_to_pdf_coords(
                        option['rect'],
                        image_width, image_height,
                        pdf_width, pdf_height
                    )
                converted_options.append(converted_option)
            converted_field['radio_options'] = converted_options

        converted_fields.append(converted_field)

    # Write output
    with open(output_json_path, 'w') as f:
        json.dump(converted_fields, f, indent=2)

    print(f"Converted {len(converted_fields)} fields from image to PDF coordinates")
    print(f"Input:  {scan_json_path}")
    print(f"Output: {output_json_path}")

    # Show an example conversion
    if converted_fields:
        print("\nExample conversion (first field):")
        orig = fields[0]
        conv = converted_fields[0]
        print(f"  Field: {orig.get('field_id')}")
        print(f"  Image rect: {orig.get('rect')}")
        print(f"  PDF rect:   {conv.get('rect')}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: convert_coordinates.py <scan.json> <pdf_file>")
        print()
        print("Example:")
        print("  python convert_coordinates.py my_form.chatfield/my_form.scan.json my_form.pdf")
        print()
        print("Output filename is automatically computed by replacing .scan.json with .form.json")
        sys.exit(1)

    scan_json_path = sys.argv[1]
    pdf_path = sys.argv[2]

    # Compute output filename by replacing .scan.json with .form.json
    scan_path = Path(scan_json_path)
    if not scan_path.name.endswith('.scan.json'):
        print(f"Error: Input file must end with .scan.json, got: {scan_path.name}", file=sys.stderr)
        sys.exit(1)

    output_json_path = str(scan_path.parent / scan_path.name.replace('.scan.json', '.form.json'))

    try:
        convert_scan_to_form(scan_json_path, pdf_path, output_json_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
