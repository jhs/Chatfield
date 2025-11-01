"""Interview definition for the Chatfield server.

This file defines the interview structure using the Chatfield builder API.
The server runs this interview and provides a chat UI for completion.

IMPORTANT: When using the PDF skill, Claude Code will edit this file to define
the interview structure for the PDF form being filled. The builder pattern below
is replaced with field definitions matching the PDF's form fields.
"""

from ..builder import chatfield


# Define the interview structure
# NOTE: This interview definition will be automatically replaced by Claude Code
# when filling PDF forms via the PDF skill
interview = (
    chatfield()
    .type("Contact Form")
    .desc("Basic contact information")
    .field("name")
        .desc("Your name")
        .must("include first and last name")
    .field("email")
        .desc("Your email address")
        .must("be a valid email")
    .build()
)
