"""Interview definition for the Chatfield server.

This file defines the interview structure using the Chatfield builder API.
The server runs this interview and provides a chat UI for completion.
"""

from ..builder import chatfield


# Define the interview structure
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
