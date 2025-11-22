from dataclasses import dataclass
import json
import sys


# Script to check that bounding boxes in a JSON file do not overlap or have other issues.
# Works with any coordinate system since it only checks geometric relationships.


@dataclass
class RectAndField:
    rect: list[float]
    rect_type: str
    field: dict


# Returns a list of messages that are printed to stdout for Claude to read.
def get_bounding_box_messages(fields_json_stream) -> list[str]:
    messages = []
    fields = json.load(fields_json_stream)
    messages.append(f"Read {len(fields)} fields")

    def rects_intersect(r1, r2):
        disjoint_horizontal = r1[0] >= r2[2] or r1[2] <= r2[0]
        disjoint_vertical = r1[1] >= r2[3] or r1[3] <= r2[1]
        return not (disjoint_horizontal or disjoint_vertical)

    rects_and_fields = []
    for f in fields:
        # Skip empty label rects (used for fields without labels)
        label_rect = f.get('label_rect', [0, 0, 0, 0])
        if label_rect != [0, 0, 0, 0]:
            rects_and_fields.append(RectAndField(label_rect, "label", f))
        rects_and_fields.append(RectAndField(f['rect'], "entry", f))

    has_error = False
    for i, ri in enumerate(rects_and_fields):
        # This is O(N^2); we can optimize if it becomes a problem.
        for j in range(i + 1, len(rects_and_fields)):
            rj = rects_and_fields[j]
            if ri.field['page'] == rj.field['page'] and rects_intersect(ri.rect, rj.rect):
                has_error = True
                if ri.field is rj.field:
                    messages.append(f"FAILURE: intersection between label and entry bounding boxes for `{ri.field['field_id']}` ({ri.rect}, {rj.rect})")
                else:
                    messages.append(f"FAILURE: intersection between {ri.rect_type} bounding box for `{ri.field['field_id']}` ({ri.rect}) and {rj.rect_type} bounding box for `{rj.field['field_id']}` ({rj.rect})")
                if len(messages) >= 20:
                    messages.append("Aborting further checks; fix bounding boxes and try again")
                    return messages
        if ri.rect_type == "entry":
            if "entry_text" in ri.field:
                font_size = ri.field["entry_text"].get("font_size", 14)
                entry_height = ri.rect[3] - ri.rect[1]
                if entry_height < font_size:
                    has_error = True
                    messages.append(f"FAILURE: entry bounding box height ({entry_height}) for `{ri.field['field_id']}` is too short for the text content (font size: {font_size}). Increase the box height or decrease the font size.")
                    if len(messages) >= 20:
                        messages.append("Aborting further checks; fix bounding boxes and try again")
                        return messages

    if not has_error:
        messages.append("SUCCESS: All bounding boxes are valid")
    return messages

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: check_bounding_boxes.py [fields.json or scan.json]")
        print()
        print("Examples:")
        print("  python check_bounding_boxes.py form.chatfield/form.scan.json")
        print("  python check_bounding_boxes.py form.chatfield/form.form.json")
        sys.exit(1)
    # Input file can be .scan.json (image coords) or .form.json (PDF coords)
    # The geometry checks work the same either way
    with open(sys.argv[1]) as f:
        messages = get_bounding_box_messages(f)
    for msg in messages:
        print(msg)
