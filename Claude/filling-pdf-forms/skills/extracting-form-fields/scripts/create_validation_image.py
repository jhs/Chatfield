import json
import sys

from PIL import Image, ImageDraw
from pypdf import PdfReader


# Creates "validation" images with rectangles for the bounding box information that
# Claude creates when determining where to add text annotations in PDFs. See forms.md.


def pdf_to_image_coords(pdf_bbox, image_width, image_height, pdf_width, pdf_height):
    """Transform bounding box from PDF coordinates to image coordinates

    PDF coordinates: origin at bottom-left, y increases upward
    Image coordinates: origin at top-left, y increases downward
    """
    x_scale = image_width / pdf_width
    y_scale = image_height / pdf_height

    # Scale X coordinates
    left = pdf_bbox[0] * x_scale
    right = pdf_bbox[2] * x_scale

    # Flip Y coordinates: PDF bottom-left origin → Image top-left origin
    # PDF y1 is bottom, y2 is top (in PDF coords where y increases upward)
    # Image needs top edge at smaller y value (since y increases downward)
    top = image_height - (pdf_bbox[3] * y_scale)
    bottom = image_height - (pdf_bbox[1] * y_scale)

    return [left, top, right, bottom]


def create_validation_image(page_number, fields_json_path, pdf_path, input_path, output_path):
    # Input file should be in the `fields.json` format described in forms.md.
    with open(fields_json_path, 'r') as f:
        fields = json.load(f)

    # Get PDF dimensions for coordinate transformation
    reader = PdfReader(pdf_path)
    page = reader.pages[page_number - 1]  # Convert to 0-indexed
    pdf_width = float(page.mediabox.width)
    pdf_height = float(page.mediabox.height)

    img = Image.open(input_path)
    image_width = img.width
    image_height = img.height
    draw = ImageDraw.Draw(img)
    num_boxes = 0

    for field in fields:
        if field['page'] == page_number:
            # Transform PDF coordinates to image coordinates
            entry_box_pdf = field['rect']
            entry_box_img = pdf_to_image_coords(entry_box_pdf, image_width, image_height, pdf_width, pdf_height)

            label_box_pdf = field.get('label_rect', [0, 0, 0, 0])

            # Draw red rectangle over entry bounding box
            draw.rectangle(entry_box_img, outline='red', width=2)
            num_boxes += 1

            if label_box_pdf != [0, 0, 0, 0]:
                label_box_img = pdf_to_image_coords(label_box_pdf, image_width, image_height, pdf_width, pdf_height)
                draw.rectangle(label_box_img, outline='blue', width=2)
                num_boxes += 1

    img.save(output_path)
    print(f"Created validation image at {output_path} with {num_boxes} bounding boxes")


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: create_validation_image.py [page number] [fields.json file] [pdf path] [input image path] [output image path]")
        sys.exit(1)
    page_number = int(sys.argv[1])
    fields_json_path = sys.argv[2]
    pdf_path = sys.argv[3]
    input_image_path = sys.argv[4]
    output_image_path = sys.argv[5]
    create_validation_image(page_number, fields_json_path, pdf_path, input_image_path, output_image_path)
