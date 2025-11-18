"""
This file defines the interview data model using the Chatfield builder API.
Edit the interview structure in the EDITABLE ZONE below to define the form.
"""

from chatfield import chatfield

interview = (chatfield()
# ---- BEGIN EDITABLE ZONE ----
    .type("PDF Form")
    .desc("Complete PDF form via conversational interview")

    .alice()
        .type("Form Assistant")
        .trait("Uses plain language, converts to valid form data")
    .bob()
        .type("Person completing form")
        .trait("Speaks naturally, needs format help")

    # Add your fields here
    .field("name")
        .desc("What is your name?")

# ---- END EDITABLE ZONE ----
    .build()
)