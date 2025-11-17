# Multilingual Forms

**Use this guide when the PDF form is in a language the user doesn't speak.**

## Overview

When the PDF form is in a language different from the user's preferred language (e.g., Spanish form, English-speaking user), the interview object should preserve the original form's language structure while using Alice and Bob traits to handle translation during the conversation.

## Key Principles

1. **Preserve original field structure** - Keep field_id names exactly as they appear in the PDF/fields.json
2. **Questions in user's language** - Write `.desc()` questions in the user's language for natural conversation
3. **Configure Alice for translation** - Add traits specifying Alice speaks the user's language but completes the form in the original language
4. **Configure Bob's language** - Specify the user's preferred language in traits
5. **Use `.as_lang()` for form output** - Use language transformations to get responses in the form's language

## Configuration Pattern

### Alice Traits

Configure Alice to handle translation:

```python
.alice()
    .type("Form Assistant")
    .trait("Speaks [USER_LANGUAGE] to Bob")
    .trait("Translates Bob's [USER_LANGUAGE] responses into [FORM_LANGUAGE] for the form")
    .trait("Uses plain language, converts to valid form data")
    .trait("Background: This is a [FORM_LANGUAGE] language form")
```

### Bob Traits

Configure Bob's language needs:

```python
.bob()
    .type("Person completing form")
    .trait("Speaks [USER_LANGUAGE] only")
    .trait("Needs help completing [FORM_LANGUAGE] form")
```

## Complete Example: Spanish Form, English User

```python
from chatfield import chatfield

interview = (chatfield()
    .type("Employment Application")  # Type in user's language
    .desc("Spanish employment application form")  # Description in user's language

    .alice()
        .type("Form Assistant")
        .trait("Speaks English to Bob")
        .trait("Translates Bob's English responses into Spanish for the form")
        .trait("Uses plain language, converts to valid form data")
        .trait("Background: This is a Spanish language form")
    .bob()
        .type("Person completing form")
        .trait("Speaks English only")
        .trait("Needs help completing Spanish form")

    # Text field: Keep Spanish field_id, ask in English, output in Spanish
    .field("nombre_completo")
        .desc("What is your full name?")  # Ask in English
        .as_lang("es", "Full name translated to Spanish")  # Output in Spanish
        .hint("Background: Form expects Spanish text")

    # Number field: Language-neutral
    .field("edad")
        .desc("What is your age in years?")  # Ask in English
        .as_int()  # Numbers are language-neutral

    # Boolean field: Language-neutral
    .field("tiene_licencia")
        .desc("Do you have a driver's license?")  # Ask in English
        .as_bool()  # Booleans are language-neutral

    # Choice field: Options in form's language
    .field("estado_civil")
        .desc("What is your marital status?")  # Ask in English
        .as_one("Soltero", "Casado", "Divorciado", "Viudo")  # Options in Spanish
        .hint("Background: Single, Married, Divorced, Widowed")

    .build())
```

## Field Type Guidelines

### Text Fields

Use `.as_lang()` to translate text responses:

```python
.field("direccion")
    .desc("What is your street address?")
    .as_lang("es", "Address translated to Spanish")
    .hint("Background: Form expects Spanish text")
```

### Numeric Fields

Numbers are language-neutral - no translation needed:

```python
.field("codigo_postal")
    .desc("What is your postal code?")
    .as_int()  # No language cast needed
```

### Boolean Fields

Booleans are language-neutral - no translation needed:

```python
.field("acepta_terminos")
    .desc("Do you accept the terms and conditions?")
    .as_bool()  # No language cast needed
```

### Choice Fields

Provide options in the form's language, use hint for user reference:

```python
.field("nivel_educacion")
    .desc("What is your highest level of education?")
    .as_one("Primaria", "Secundaria", "Universitaria", "Posgrado")
    .hint("Background: Elementary, High School, University, Graduate")
```

Alice will present these options in the user's language during conversation but record them in the form's language.

## How It Works

1. **Conversation**: Alice speaks the user's language (e.g., English) when asking questions
2. **User responses**: Bob responds naturally in their language (e.g., English)
3. **Translation**: Alice translates responses to the form's language (e.g., Spanish) using `.as_lang()` transformations
4. **Form population**: The form is filled out in its original language (e.g., Spanish)

## When to Use This Approach

Use this multilingual approach when:

- User explicitly states they don't speak the form's language
- PDF contains non-English text and user's preferred language is English
- User asks for translation help with a foreign language form

**If the form and user speak the same language, follow the standard workflow in fillable-forms.md or nonfillable-forms.md.**

## Additional Resources

- **API Reference**: api-reference.md - See `.as_lang()` transformation documentation
- **Fillable Forms**: fillable-forms.md - Standard workflow for fillable PDFs
- **Non-fillable Forms**: nonfillable-forms.md - Standard workflow for non-fillable PDFs
