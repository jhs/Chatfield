#!/usr/bin/env python3
"""
Step-by-step CLI for running Chatfield interviews one turn at a time.

Optimized for agent/automation use with SQLite state persistence.

Installation:
    pip install chatfield[agent]

Usage:
    # First run (initialize interview)
    python -m chatfield.cli --state=state.db --interview=example.py

    # Follow-up runs (continue conversation)
    python -m chatfield.cli --state=state.db --interview=example.py "My response"

    # Inspect collected data
    python -m chatfield.cli --state=state.db --interview=example.py --inspect
"""

import sys
import sqlite3
import hashlib
import argparse
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver

from . import Interviewer
from .server.cli import load_interview_from_file


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Run one step of a Chatfield interview',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # First run (initialize)
  python -m chatfield.cli --state=state.db --interview=example.py

  # Follow-up run
  python -m chatfield.cli --state=state.db --interview=example.py "My name is Alice"

  # Inspect current state at any time
  python -m chatfield.cli --state=state.db --interview=example.py --inspect
        """
    )

    parser.add_argument('--state', required=True, help='Path to SQLite state database file')
    parser.add_argument('--interview', required=True, help='Path to interview Python file')
    parser.add_argument('--inspect', action='store_true', help='Pretty-print interview results and exit')
    parser.add_argument('message', nargs='?', help='User message for this step')

    args = parser.parse_args()

    state_path = Path(args.state)
    interview_path = args.interview

    # Load the interview definition from file
    try:
        interview = load_interview_from_file(interview_path)
    except Exception as e:
        print(f"Error loading interview: {e}", file=sys.stderr)
        sys.exit(1)

    # Determine thread_id from state file or generate new one
    # For simplicity, we use a fixed thread_id per state file
    # Hash the state file path to get a consistent thread_id
    thread_id = hashlib.md5(str(state_path.absolute()).encode()).hexdigest()

    # Create SqliteSaver checkpointer
    # Note: check_same_thread=False is OK as SqliteSaver uses a lock for thread safety
    conn = sqlite3.connect(str(state_path), check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    # Create interviewer with the checkpointer
    interviewer = Interviewer(interview, thread_id=thread_id, checkpointer=checkpointer)

    # Handle inspect mode
    if args.inspect:
        if not state_path.exists():
            print(f"Error: State file not found: {args.state}", file=sys.stderr)
            print("Cannot inspect - no interview state exists yet.", file=sys.stderr)
            sys.exit(1)

        # Get the interview object from the graph state
        state_snapshot = interviewer.graph.get_state(interviewer.config)
        if state_snapshot and state_snapshot.values.get('interview'):
            interview_with_data = state_snapshot.values['interview']
            results = interview_with_data._pretty()
        else:
            results = interviewer.interview._pretty()

        print(results)
        sys.exit(0)

    # Determine if this is first run or follow-up based on whether we have a checkpoint
    state_snapshot = interviewer.graph.get_state(interviewer.config)
    is_first_run = not state_snapshot or not state_snapshot.values.get('messages')
    has_message = args.message is not None

    # Validate state
    if is_first_run and has_message:
        print("Error: First run detected (no checkpoint), but message provided.", file=sys.stderr)
        print("For first run, omit the message argument.", file=sys.stderr)
        sys.exit(1)

    if not is_first_run and not has_message:
        print("Error: Follow-up run detected (checkpoint exists), but no message provided.", file=sys.stderr)
        print("For follow-up runs, provide a message argument.", file=sys.stderr)
        sys.exit(1)

    if is_first_run:
        response = interviewer.go()
    else:
        response = interviewer.go(args.message)
    print(response, file=sys.stdout, flush=True)


if __name__ == '__main__':
    main()
