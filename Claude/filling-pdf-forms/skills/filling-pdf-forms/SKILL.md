---
name: filling-pdf-forms
description: Complete PDF forms by collecting data through conversational interviews and populating form fields. Use when filling forms, completing documents, or when the user mentions PDFs, forms, form completion, or document population.
allowed-tools: Read, Write, Edit, Glob, Bash, Task
version: 1.0.0a2
license: Apache 2.0
---

# Filling PDF Forms

Complete PDF forms by collecting required data through conversational interviews and populating form fields.

<purpose>
Use when completing PDF forms with user-provided data. Your goal is to produce a `.done.pdf` corresponding to the user's starting PDF file, populated with the user-provided information, by following the below process exactly.
</purpose>

## Process Overview

```plantuml
@startuml SKILL

title Filling PDF Forms - High-Level Workflow

|User|
start
:User provides PDF form to complete;

|filling-pdf-forms skill|

:Step 0: Initialize Chatfield;

:Step 1: Form Extraction;

:Step 2: Build Form Data Model;

:Step 3: Translation Decision;

if (User language == form language?) then (yes)
  :Use base Form Data Model;
else (no)
  :Translation Setup;
endif

:Step 4: Run Interview Server;

partition "Interview Loop" {
  repeat
    :Server generates question → Display to user;
    |User|
    :User provides response;
    |filling-pdf-forms skill|
    :Server validates & processes;
  repeat while (All fields collected?) is (no)
  ->yes;
}

:Capture stdout output;

:Step 5: Populate PDF;

|User|
:**✓ SUCCESS**;
:Receive completed PDF <basename>.done.pdf;
stop

@enduml
```

## Workflow

### Step 0: Initialize Chatfield

Ensure the `chatfield` package is available before proceeding. If not, install its wheel file in ./scripts.

**Check**

```bash
# Check if chatfield is installed
python -c "import chatfield"
```

**Install if missing**
```bash
pip install ./scripts/chatfield-1.0.0a2-py3-none-any.whl
```

### Step 1: Form Extraction

Use the `extracting-form-fields` sub-agent to extract the PDF form into useful files.

**Invoke via Task tool:**

```python
Task(
    subagent_type="general-purpose",
    description="Extract PDF form fields",
    prompt=f"""
    Extract form field data from PDF: {pdf_path}

    Use the extracting-form-fields skill to complete this task.
    """
)
```

When the task reports "Done", it will have created (for `input.pdf`):
- `input.chatfield/` directory
- `input.chatfield/input.form.md` - PDF content as Markdown
- `input.chatfield/input.form.json` - Form field definitions
- `input.chatfield/interview.py` - Template Form Data Model file ready for editing

### Step 2: Build Form Data Model

**First, read entirely:** ./references/data-model-api.md to learn how to build Chatfield data models
**Then, read entirely:** ./references/converting-pdf-to-chatfield.md for guidance on how to make the needed model.

With those references understood, edit `[basename].chatfield/interview.py` to define the Chatfield interview.

This step creates the **Form Data Model** - the faithful representation of the PDF form using the Chatfield data model API.

### Step 3: Translation (If Needed)

Determine if translation is needed.

#### When Translation is Needed

**Explicit**: User states "I need to fill this Spanish form but I only speak English"

**Implicit**: User request is in language X, but PDF is in language Y
- Example: "Help me complete form.es.pdf" (English request, Spanish form)

**To apply translation, see:** ./references/translating.md

Translation creates `interview_<lang>.py` and **re-defines** the Form Data Model from `interview.py` to the new `interview_<lang>.py` instead. Henceforth, use the translated file as the Form Data Model.

### Step 4: Run Interview Server

Run the Chatfield interview server with the Form Data Model:

```bash
# Using base Form Data Model (same language):
python -m chatfield.server input.chatfield/interview.py

# OR using translated Form Data Model:
python -m chatfield.server input.chatfield/interview_es.py
```

Server will:
1. Start conversational interview
2. Collect data from user
3. Output results to stdout
4. Exit when complete

Capture the stdout output - you'll need it for population.

### Step 5: Populate PDF

Parse server output and populate the PDF.

**See:** ./references/populating.md

**Steps:**
1. Parse server stdout to extract field values
2. Create `.values.json` with proper format
3. Run population script:
   ```bash
   python scripts/fill_fillable_fields.py input.pdf input.values.json input.done.pdf
   ```
4. Verify output PDF exists

**Result**: `input.done.pdf`
