# DO NOT add a docstring

from chatfield import chatfield

# The chatfield.server module will import this `interview` object.
# **CRITICAL** - Replace the commented examples below with the real data definition.
interview = (chatfield()
    # .type(<form id, official name, or filename>)
    # .desc(<human-friendly form description>)

    # Define Alice's type plus at least one trait.
    # .alice()
    #     .type(<primary role for the AI agent>)
    #     .trait(<characteristic or behavior hint for the AI agent>)
    #     # Optional additional .trait() calls

    # Define Bob's type plus at least one trait.
    # .bob()
    #     .type(<primary role for the human user>)
    #     .trait(<characteristic or guidance about conversing with the user>)
    #     # Optional additional .trait() calls

    # Define one or more fields.
    # .field(<field id>)
    #     .desc(<human-friendly field description>)

    .build()
)
