"""Interview definition for the Chatfield server.

This file defines the interview structure using the Chatfield builder API.
The server runs this interview and provides a chat UI for completion.

IMPORTANT: When using the PDF skill, Claude Code will edit this file in the
allowed EDITABLE ZONE below, to define the interview structure for its PDF form.
"""

from ..builder import chatfield

# Define the interview structure.
interview = (chatfield()
# ---- BEGIN PDF SKILL EDITABLE ZONE ----
    .type("This will be replaced")
    .desc("This form description will be replaced")

    .alice()
        .type("This Alice type will be replaced")
    .bob()
        .type("This Bob type will be replaced")

    .field("These fields will be replaced")
        .desc("This field description will be replaced")

# ---- END PDF SKILL EDITABLE ZONE ----
    .build()
)
