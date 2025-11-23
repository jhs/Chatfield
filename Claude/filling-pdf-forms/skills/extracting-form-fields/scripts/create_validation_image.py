import json
import sys

from PIL import Image, ImageDraw


# Creates "validation" images with rectangles for the bounding box information that
# Claude creates when determining where to add text annotations in PDFs.
# This version works with IMAGE coordinates (from .scan.json files).


def create_validation_image(page_number, fields_json_path, input_path, output_path):
    """
    Create a validation image with bounding boxes overlaid.

    Args:
        page_number: Page number (1-indexed)
        fields_json_path: Path to .scan.json file (IMAGE coordinates)
        input_path: Path to input PNG image
        output_path: Path to output validation image
    """
    # Input file should be in the .scan.json format with IMAGE coordinates
    with open(fields_json_path, 'r') as f:
        fields = json.load(f)

    img = Image.open(input_path)
    draw = ImageDraw.Draw(img)
    num_boxes = 0

    for field in fields:
        if field['page'] == page_number:
            # Coordinates are already in image space - use them directly!
            entry_box_img = field['rect']
            label_box_img = field.get('label_rect', [0, 0, 0, 0])

            # Draw red rectangle over entry bounding box
            draw.rectangle(entry_box_img, outline='red', width=2)
            num_boxes += 1

            if label_box_img != [0, 0, 0, 0]:
                draw.rectangle(label_box_img, outline='blue', width=2)
                num_boxes += 1

    img.save(output_path)
    print(f"Created validation image at {output_path} with {num_boxes} bounding boxes")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: create_validation_image.py [page number] [scan.json file] [input image path] [output image path]")
        print()
        print("Example:")
        print("  python create_validation_image.py 1 form.chatfield/form.scan.json form.chatfield/page_1.png form.chatfield/page_1_validation.png")
        sys.exit(1)
    page_number = int(sys.argv[1])
    fields_json_path = sys.argv[2]
    input_image_path = sys.argv[3]
    output_image_path = sys.argv[4]
    create_validation_image(page_number, fields_json_path, input_image_path, output_image_path)
