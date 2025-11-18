# Multilingual Forms

**Use this guide when the PDF form is in a language the user doesn't speak.** For example, English-speaking user, non-English form.

Use this process when the user explicitly asks for it, or when the user asks to complete a form in a different language from that of the form.

## Overview

Whent the form and user's languages differ, take care to ensure these rules:
1. **Chatfield should always reflect the PDF accurately**: Preserve the form's language, instructions, tooltips, etc. when defining traits, fields, descriptions, hints, background, and all LLM guidance.
2. **Use trait() guidance to make Alice translate for Bob**: Indicate that Bob (i.e. the human user) only speaks one language, Alice (i.e. the LLM) will use Bob's language and translate content needed.

## Key Principles

1. **Do not translate form content** - Remember, when building the interview object, the user's language is irrelevant because the job is to produce a faithful data definition of the form.
2. **Configure Alice for translation** - Add `.trait()` calls specifying that Alice speaks Bob's language in conversation but completes the form in the form's language, translating as needed.
3. **Configure Bob's language** - Add a `.trait()` call specifying that Bob prefers the user's language

## Configuration Pattern

### Alice Traits

Configure Alice to handle translation:

```python
.alice()
    # .type() call unrelated .trait() calls as-is
    .trait("Speaks [USER_LANGUAGE] to Bob")
    .trait("Translates Bob's [USER_LANGUAGE] responses into [FORM_LANGUAGE] for the form")
```

### Bob Traits

Configure Bob's language needs:

```python
.bob()
    # .type() call unrelated .trait() calls as-is
    .trait("Speaks [USER_LANGUAGE] only")
    .trait("Needs help completing [FORM_LANGUAGE] form")
```