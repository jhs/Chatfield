#!/usr/bin/env python
"""Run Chatfield server with interview from chatfield_interview.py

This script runs the Chatfield FastAPI server using the interview definition
from chatfield_interview.py in the same directory.
"""

import sys
from pathlib import Path

# Add scripts directory to path so we can import chatfield_interview
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

# Import the interview definition from this directory
from chatfield_interview import interview

# Import and patch the server app to use our interview
from chatfield.server import app
app.interview = interview  # Replace the default interview

# Run the server CLI (handles PID printing, signals, uvicorn, etc.)
from chatfield.server.cli import main

if __name__ == "__main__":
    main()
