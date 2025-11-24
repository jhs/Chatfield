# AskUserQuestion using chatfield.cli strategy

**CRITICAL: Strict adherence required. No deviations permitted.**

This document defines MANDATORY patterns for using `AskUserQuestion` with `chatfield.cli` interviews. Assumes you already know the AskUserQuestion tool signature.

---

## MANDATORY Pattern for EVERY Question

**REQUIRED - EXACT structure:**

```python
AskUserQuestion(
    questions=[{
        "question": "<chatfield.cli's exact question>",  # No paraphrasing
        "header": "<12 chars max>",
        "multiSelect": <True/False>,  # Based on data model
        "options": [
            # POSITION 1: REQUIRED
            {"label": "Skip", "description": "Leave this field blank and continue"},
            # POSITION 2: REQUIRED
            {"label": "Delegate", "description": "Ask Claude to look up the needed information using all available resources"},
            # POSITION 3: First option from chatfield.cli (if present)
            {"label": "<First from chatfield.cli>", "description": "..."},
            # POSITION 4: Second option from chatfield.cli (if present)
            {"label": "<Second from chatfield.cli>", "description": "..."}
        ]
    }]
)
# POSITION 5 (implicit): "Other" - auto-added for free text
```

---

## Determine multiSelect

**Check `interview.py` Form Data Model (Chatfield builder API):**

| Data Model | multiSelect |
|------------|-------------|
| `.as_multi()` or `.one_or_more()` | `True` |
| `.as_one()` or `.as_nullable_one()` | `False` |
| Plain `.field()` (no cardinality) | `False` |

---

## Parse chatfield.cli Options

**If chatfield.cli output contains options, extract and prioritize:**

**Recognize patterns:**
- `"Status? (Single, Married, Divorced)"`
- `"Choose: A, B, C, D"`
- `"Preference: Red | Blue | Green"`

Add **first TWO** as positions 3-4

**Example:**
```
chatfield.cli: "Status? (Single, Married, Divorced, Widowed)"
Options:
1. Skip
2. Delegate
3. Single    ← First from chatfield.cli
4. Married   ← Second from chatfield.cli
"Other": User can type "Divorced" or "Widowed"
```

---

## Handle Responses

| Selection | Action |
|-----------|--------|
| Types via "Other" | Pass text to chatfield.cli next iteration |
| "Skip" | Pass "skip" or paraphrase as needed to chatfield.cli next iteration |
| "Delegate" | Research & provide answer |
| Option 3-4 | Pass selection to CLI |
| Multi-select | Join: "Email, Phone" to chatfield.cli next iteration |

---

## Delegation Pattern

**When user selects "Delegate":**
1. Parse question to understand needed info
2. Treat this as if the user directly asked, "Help me find out ..."
2. Use ALL tools available to you,
4. Pass the result to chatfield.cli as if user typed it
5. If not found, ask user

---

## Quick Examples (RULES 1-7)

### RULE 1: Free Text
```
# chatfield.cli: "What is your name?"
# multiSelect: False
# Options: Skip, Delegate
```

### RULE 2: Yes/No
```
# chatfield.cli: "Are you employed?"
# multiSelect: False
# Options: Skip, Delegate, Yes, No
```

### RULE 3: Single-Select Choice
```
# chatfield.cli: "Status? (Single, Married, Divorced, Widowed)"
# multiSelect: False
# Extract: ["Single", "Married", "Divorced", "Widowed"]
# Options: Skip, Delegate, Single, Married
# Via Other: "Divorced", "Widowed"
```

### RULE 4: Multi-Select Choice
```
# chatfield.cli: "Contact? (Email, Phone, Text, Mail)"
# Data model: .as_multi(...)
# multiSelect: True
# Extract: ["Email", "Phone", "Text", "Mail"]
# Options: Skip, Delegate, Email, Phone
# Via Other: "Text", "Mail"
```

### RULE 5: Numeric
```
# chatfield.cli: "How many dependents?"
# multiSelect: False
# Options: Skip, Delegate (optionally: "0", "1-2")
# Via Other: Exact number
```

### RULE 6: Complex/Address
```
# chatfield.cli: "Mailing address?"
# multiSelect: False
# Options: Skip, Delegate
# Via Other: Full address
```

### RULE 7: Date
```
# chatfield.cli: "Date of birth?"
# multiSelect: False
# Options: Skip, Delegate (optionally: "Today", "Tomorrow")
# Via Other: Specific date
```

---

## MANDATORY Checklist

**EVERY question MUST:**
- [ ] Be based on chatfield.cli's stdout message
- [ ] Include "Skip" as option 1
- [ ] Include "Delegate" as option 2
- [ ] Check Form Data Model for multiSelect
- [ ] Add first TWO chatfield.cli options as 3-4 (if present)