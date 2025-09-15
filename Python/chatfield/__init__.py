"""Chatfield: Socratic dialogue for data gathering powered by LLMs.

Transform rigid forms into thoughtful Socratic conversations that guide users to express their needs clearly.
"""

__version__ = "0.2.0"

from .builder import chatfield
from .interview import Interview
from .interviewer import Interviewer
from .field_proxy import FieldProxy, create_field_proxy

__all__ = [
    "chatfield",
    "Interview",
    "Interviewer",
    "FieldProxy",
    "create_field_proxy",
]