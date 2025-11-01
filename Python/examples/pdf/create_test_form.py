#!/usr/bin/env python3
"""Create a minimal test PDF with fillable form fields for quick testing.

This creates a simple PDF with 2-3 fields that can be quickly filled via Chatfield.
"""

import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, DictionaryObject, ArrayObject, NumberObject, TextStringObject


def create_base_pdf(output_path: str):
    """Create a base PDF with text labels using reportlab."""
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Test Form")

    # Instructions
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 80, "This is a minimal test form for Chatfield workflow testing.")

    # Field labels
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 120, "Name:")
    c.drawString(50, height - 160, "Age:")
    c.drawString(50, height - 200, "Subscribe to newsletter:")

    c.save()


def add_form_fields(input_path: str, output_path: str):
    """Add fillable form fields to the PDF."""
    reader = PdfReader(input_path)
    writer = PdfWriter()

    page = reader.pages[0]
    writer.add_page(page)

    # Get the writer's page object
    writer_page = writer.pages[0]

    # Page dimensions
    page_height = float(page.mediabox.height)

    # Create field annotations
    fields = []

    # Add Name text field
    name_field = DictionaryObject({
        NameObject("/Type"): NameObject("/Annot"),
        NameObject("/Subtype"): NameObject("/Widget"),
        NameObject("/Rect"): ArrayObject([
            NumberObject(150), NumberObject(page_height - 135),
            NumberObject(400), NumberObject(page_height - 115)
        ]),
        NameObject("/FT"): NameObject("/Tx"),  # Text field
        NameObject("/T"): TextStringObject("name"),
        NameObject("/V"): TextStringObject(""),
        NameObject("/F"): NumberObject(4),  # Print flag
        NameObject("/P"): writer_page.indirect_reference
    })
    fields.append(writer._add_object(name_field))

    # Add Age text field
    age_field = DictionaryObject({
        NameObject("/Type"): NameObject("/Annot"),
        NameObject("/Subtype"): NameObject("/Widget"),
        NameObject("/Rect"): ArrayObject([
            NumberObject(150), NumberObject(page_height - 175),
            NumberObject(250), NumberObject(page_height - 155)
        ]),
        NameObject("/FT"): NameObject("/Tx"),  # Text field
        NameObject("/T"): TextStringObject("age"),
        NameObject("/V"): TextStringObject(""),
        NameObject("/F"): NumberObject(4),
        NameObject("/P"): writer_page.indirect_reference
    })
    fields.append(writer._add_object(age_field))

    # Add Subscribe checkbox
    # Create appearance dictionary for checkbox states
    ap_dict = DictionaryObject({
        NameObject("/N"): DictionaryObject({
            NameObject("/Yes"): DictionaryObject(),
            NameObject("/Off"): DictionaryObject()
        })
    })

    subscribe_field = DictionaryObject({
        NameObject("/Type"): NameObject("/Annot"),
        NameObject("/Subtype"): NameObject("/Widget"),
        NameObject("/Rect"): ArrayObject([
            NumberObject(250), NumberObject(page_height - 205),
            NumberObject(265), NumberObject(page_height - 190)
        ]),
        NameObject("/FT"): NameObject("/Btn"),  # Button/checkbox field
        NameObject("/T"): TextStringObject("subscribe"),
        NameObject("/V"): NameObject("/Off"),
        NameObject("/AS"): NameObject("/Off"),
        NameObject("/AP"): ap_dict,
        NameObject("/_States_"): ArrayObject([NameObject("/Yes"), NameObject("/Off")]),
        NameObject("/F"): NumberObject(4),
        NameObject("/P"): writer_page.indirect_reference
    })
    fields.append(writer._add_object(subscribe_field))

    # Add fields to page annotations
    if NameObject("/Annots") not in writer_page:
        writer_page[NameObject("/Annots")] = ArrayObject()
    writer_page[NameObject("/Annots")].extend(fields)

    # Create AcroForm
    writer._root_object.update({
        NameObject("/AcroForm"): DictionaryObject({
            NameObject("/Fields"): ArrayObject(fields),
            NameObject("/NeedAppearances"): NameObject("/true"),
            NameObject("/DR"): DictionaryObject(),
            NameObject("/DA"): TextStringObject("/Helv 0 Tf 0 g")
        })
    })

    with open(output_path, "wb") as output_file:
        writer.write(output_file)


def main():
    """Create a minimal test PDF form."""
    if len(sys.argv) < 2:
        print("Usage: python create_test_form.py <output.pdf>")
        print("\nExample: python create_test_form.py test_form.pdf")
        sys.exit(1)

    output_path = sys.argv[1]
    temp_path = "/tmp/test_form_base.pdf"

    print("Creating base PDF...")
    create_base_pdf(temp_path)

    print("Adding form fields...")
    add_form_fields(temp_path, output_path)

    print(f"\n✓ Created test form: {output_path}")
    print("\nThis form contains 3 fields:")
    print("  1. name (text field) - Your full name")
    print("  2. age (text field) - Your age in years")
    print("  3. subscribe (checkbox) - Subscribe to newsletter")
    print("\nThis is a minimal form designed for quick Chatfield workflow testing.")


if __name__ == "__main__":
    main()
