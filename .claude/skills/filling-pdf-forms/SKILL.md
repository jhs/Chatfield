---
name: filling-pdf-forms
description: Complete PDF forms by collecting data through conversational interviews and populating form fields. Use when filling forms, completing documents, or when the user mentions PDFs, forms, form completion, or document population.
license: Apache 2.0
---

# Filling PDF Forms

Complete PDF forms by collecting required data through conversational interviews and populating form fields.

## Dependencies

Install required Python packages before using this skill:

```bash
pip install pypdf pdfplumber markitdown[pdf]
```

## When to Use This Skill

Use when completing PDF forms with user-provided data.

## Workflow Selection

PDFs may have programmatic form fields (fillable) or require visual annotation (non-fillable). Check which type:

```bash
python scripts/check_fillable_fields.py input.pdf
```

**Fillable fields detected?** → See [references/fillable-forms.md](references/fillable-forms.md)

**No fillable fields?** → See [references/nonfillable-forms.md](references/nonfillable-forms.md)

Both workflows use identical Chatfield conversational interview models - only the field extraction and PDF population mechanisms differ.

---

## Interview Validation Checklist

Both fillable and non-fillable workflows require building a high-quality Chatfield interview. Use this checklist to validate the interview definition before running the server:

```
Interview Validation Checklist:
- [ ] All field_ids from .form.json or .fields.json are present in interview definition
- [ ] No field_ids are duplicated or missing
- [ ] Human-friendly data model uses roll-up pattern for mutually-exclusive fields
- [ ] Split pattern applied where PDF splits single values (e.g., multi-part identifiers)
- [ ] Expand pattern applied where one choice maps to multiple checkboxes
- [ ] Conclude fields properly reference master fields
- [ ] Alice traits include extracted form knowledge
- [ ] Field hints provide context from PDF instructions
- [ ] Optional fields explicitly marked with hint("Background: Optional...")
- [ ] .must() used sparingly (only for true content requirements)
- [ ] .as_*() transformations used liberally for all type casts and formatting
- [ ] Field .desc() questions are natural and user-friendly (no technical field_ids)
```

**If any items fail validation:**
1. Review the specific issue in the checklist
2. Fix the `Python/chatfield/server/interview.py` definition
3. Re-run validation checklist
4. Proceed only when all items pass

---

## Additional Resources

- **Fillable Forms:** [references/fillable-forms.md](references/fillable-forms.md) - Complete workflow for PDFs with programmatic form fields
- **Non-fillable Forms:** [references/nonfillable-forms.md](references/nonfillable-forms.md) - Complete workflow for PDFs requiring visual annotation
- **API Reference:** [references/api-reference.md](references/api-reference.md) - Builder methods, transformations, and validation rules
