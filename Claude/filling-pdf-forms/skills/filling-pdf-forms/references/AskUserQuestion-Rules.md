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
            {"label": "Skip", "description": "Skip (N/A, blank, negative, etc)"},
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
| Types via "Other" | If starts with `'`: strip prefix and pass verbatim to chatfield.cli. Otherwise: judge if it's a direct answer or instruction to Claude. Direct answer → pass to chatfield.cli; Request for Claude → research/process, then respond to chatfield.cli |
| "Skip" | Context-aware response: Yes/No questions → "No"; Optional/nullable fields → "N/A"; Other fields → "Skip" |
| "Delegate" | Research & provide answer |
| Option 3-4 | Pass selection to CLI |
| Multi-select | Join: "Email, Phone" to chatfield.cli next iteration |

## Distinguishing Direct Answers from Claude Requests

**When user types via "Other", judge intent:**

**Direct answers** (pass to chatfield.cli):
- "Find new customers in new markets" ← answer to "What is your business strategy?"
- "123 Main St, Boston MA" ← answer to "What is your address?"
- "Python and TypeScript" ← answer to "What programming languages?"

**Requests for Claude** (research first):
- "look up my SSN" ← asking Claude to find something
- "research the population" ← asking Claude to look something up
- "what's today's date" ← asking Claude a question

**Edge case:** `'` prefix forces verbatim pass-through regardless of content

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

**Note:** Skip handling is context-aware per "Handle Responses" table above.

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