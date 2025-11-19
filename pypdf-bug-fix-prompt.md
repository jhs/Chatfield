# pypdf Bug Fix: AttributeError in AcroForm /DR Handling

## Bug Report

**Error**: `AttributeError: 'dict' object has no attribute 'get_object'`

**Location**: `pypdf/generic/_appearance_stream.py` (around line 435-437)

**Trigger Condition**: When filling PDF form fields in documents where:
1. The AcroForm dictionary lacks a `/DR` (Default Resources) entry
2. The font used is not in `CORE_FONT_METRICS` (e.g., `/Helv` instead of `/Helvetica`)

**Full Traceback**:
```
pypdf/_writer.py:1045: in update_page_form_field_values
    appearance_stream_obj = TextStreamAppearance.from_text_annotation(
pypdf/generic/_appearance_stream.py:437: in from_text_annotation
    document_font_resources = document_resources.get_object().get("/Font", DictionaryObject()).get_object()
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'dict' object has no attribute 'get_object'
```

## Root Cause

In `pypdf/generic/_appearance_stream.py`, lines 433-437, the code uses `{}` (plain Python dict) as the default value:

```python
# BUGGY CODE (current)
document_resources = cast(
    dict[Any, Any],
    acro_form.get("/DR", {}),  # ← Returns plain dict when /DR missing
)
document_font_resources = document_resources.get_object().get("/Font", DictionaryObject()).get_object()
```

**Problem**: The `cast()` function is only a type hint—it doesn't convert objects. When `/DR` is missing, `acro_form.get("/DR", {})` returns the plain Python dict `{}`, which doesn't have a `.get_object()` method, causing the AttributeError.

**Note**: The same function already uses the correct pattern on lines 419-428, but lines 433-437 use the buggy pattern.

## The Fix

Replace lines 433-437 with:

```python
# FIXED CODE
document_resources = cast(
    DictionaryObject,
    cast(
        DictionaryObject,
        acro_form.get("/DR", DictionaryObject()),  # ← Use DictionaryObject() not {}
    ).get_object(),
)
document_font_resources = document_resources.get("/Font", DictionaryObject()).get_object()
```

**Key Change**: Replace the default value `{}` with `DictionaryObject()` on line 435 (now line 437 in the fixed version).

## Test Case

Add this test to `tests/test_forms.py`:

```python
def test_update_form_field_without_acroform_dr():
    """
    Test that updating form fields works when AcroForm lacks /DR entry.

    This tests the fix for a bug where pypdf would crash with:
    AttributeError: 'dict' object has no attribute 'get_object'

    when filling form fields in PDFs where the AcroForm dictionary
    doesn't have a /DR (Default Resources) entry and the font used
    is not in the standard font metrics (e.g., /Helv instead of /Helvetica).
    """
    # Use a PDF with forms
    writer = PdfWriter(clone_from=RESOURCE_ROOT / "FormTestFromOo.pdf")

    # Delete /DR from AcroForm and /DA from a field to trigger the bug scenario
    # When /DA is missing, the default font is /Helv (not in CORE_FONT_METRICS)
    # This causes the code to fall back to checking AcroForm /DR, triggering the bug
    if "/DR" in writer.root_object["/AcroForm"]:
        del writer.root_object["/AcroForm"]["/DR"]

    # Delete /DA from the field to force the use of default /Helv font
    # Also delete /DR from annotation to force fallback to AcroForm /DR
    field_ref = writer.root_object["/AcroForm"]["/Fields"][0]
    field = field_ref.get_object()
    if "/DA" in field:
        del field["/DA"]
    if "/DR" in field:
        del field["/DR"]

    # Remove /DR from the annotation (which is also the field in this case)
    if "/Annots" in writer.pages[0]:
        for annot_ref in writer.pages[0]["/Annots"]:
            annot = annot_ref.get_object()
            if "/DR" in annot:
                del annot["/DR"]
            if "/DA" in annot:
                del annot["/DA"]

    # This should not raise AttributeError: 'dict' object has no attribute 'get_object'
    writer.update_page_form_field_values(
        writer.pages[0],
        {"Text1": "test value"},
        auto_regenerate=False,
    )

    # Verify the field was updated
    output = BytesIO()
    writer.write(output)
    reader = PdfReader(output)
    fields = reader.get_fields()
    assert fields["Text1"]["/V"] == "test value"
```

**Required imports** (add to top of `tests/test_forms.py` if missing):
```python
from io import BytesIO
from pathlib import Path
from pypdf import PdfReader, PdfWriter

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"
```

## Verification Steps

1. **Before fix** - Test should fail:
   ```bash
   pytest tests/test_forms.py::test_update_form_field_without_acroform_dr -v
   # Expected: FAILED with AttributeError
   ```

2. **Apply the fix** to `pypdf/generic/_appearance_stream.py`

3. **After fix** - Test should pass:
   ```bash
   pytest tests/test_forms.py::test_update_form_field_without_acroform_dr -v
   # Expected: PASSED
   ```

4. **No regressions** - All form tests should pass:
   ```bash
   pytest tests/test_forms.py tests/test_appearance_stream.py -v
   pytest tests/test_writer.py -k form -v
   # Expected: All tests PASSED
   ```

## Files to Modify

1. **pypdf/generic/_appearance_stream.py** - Apply the fix (lines 433-437)
2. **tests/test_forms.py** - Add the regression test

## Expected Changes Summary

- **Files changed**: 2
- **Insertions**: ~64 lines (mostly test)
- **Deletions**: ~3 lines (in fix)
- **Net change**: Minimal, focused fix matching existing correct pattern

## Commit Message

```
Fix AttributeError when AcroForm lacks /DR entry

When filling form fields in PDFs without a /DR (Default Resources)
entry in the AcroForm dictionary, pypdf would crash with:
AttributeError: 'dict' object has no attribute 'get_object'

The bug was in _appearance_stream.py line 435 where it used an
empty dict {} as the default value instead of DictionaryObject().
The cast() type hint doesn't convert the object, so when acro_form.get()
returns the default {}, calling .get_object() fails.

Fixed by using DictionaryObject() as default, matching the pattern
already used correctly on lines 419-428 in the same function.

Added unit test to prevent regression.
```

## Quick Summary for AI Agent

Fix the bug in `pypdf/generic/_appearance_stream.py` around line 435 where `acro_form.get("/DR", {})` uses `{}` as default instead of `DictionaryObject()`. Replace the buggy code block (lines 433-437) with the corrected version that uses `DictionaryObject()` as the default value. Add the comprehensive regression test to `tests/test_forms.py`. The test should fail before the fix (AttributeError) and pass after. Verify all existing form tests still pass.
