"""CLI entry point for Chatfield FastAPI server."""

import os
import sys
import signal
import socket
import logging
import uvicorn
import argparse
import threading
import time
import importlib.util
from pathlib import Path

from . import app

def load_interview_from_file(file_path: str):
    """
    Load an interview object from a Python file.

    Args:
        file_path: Path to a Python file that defines an 'interview' variable

    Returns:
        The Interview object from the file

    Raises:
        FileNotFoundError: If the file doesn't exist
        AttributeError: If the file doesn't contain an 'interview' variable
    """
    path = Path(file_path).resolve()

    if not path.exists():
        raise FileNotFoundError(f"Interview file not found: {file_path}")

    # Load the module dynamically
    spec = importlib.util.spec_from_file_location("custom_interview", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load module from: {file_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules["custom_interview"] = module
    spec.loader.exec_module(module)

    # Extract the interview object
    if not hasattr(module, 'interview'):
        raise AttributeError(
            f"File {file_path} must define an 'interview' variable.\n"
            "Example:\n"
            "  from chatfield import chatfield\n"
            "  interview = chatfield().field('name').build()"
        )

    return module.interview


def find_free_port():
    """Find a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


def print_interview_results():
    """Print interview results with consistent formatting."""
    # Access the server's global session
    if app.current_session:
        try:
            results = app.current_session.get_results()
            print(f'------------ Pretty Print Output ---------------', flush=True)
            print(results, flush=True)
            print(f'------------------------------------------------', flush=True)
        except Exception as e:
            print(f"Error printing results: {e}", file=sys.stderr, flush=True)
    else:
        print(f"No active interview session", file=sys.stderr, flush=True)


def monitor_interview_completion(server):
    """Background thread that monitors interview completion and shuts down server."""
    while True:
        time.sleep(0.5)  # Check every 500ms

        if app.current_session and app.current_session.interview._done:
            print("\n\nInterview complete, shutting down server...", file=sys.stderr, flush=True)
            print_interview_results()

            # Gracefully shut down the uvicorn server
            server.should_exit = True
            break


def main():
    """Run the Chatfield FastAPI server."""
    logging.basicConfig(
        level=logging.WARNING,  # Set root logger to WARNING to silence other libraries
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )
    logging.getLogger('chatfield').setLevel(logging.INFO)

    parser = argparse.ArgumentParser(
        description='Chatfield FastAPI Server',
        epilog='Example: python -m chatfield.server my_interview.py'
    )
    parser.add_argument(
        'interview_file',
        help='Path to Python file defining an interview'
    )
    parser.add_argument(
        '--port',
        type=int,
        # default=0,
        default=37067,
        help='Port to run server on (0 for auto-assign, default: 0)'
    )
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Host to bind to (default: 127.0.0.1)'
    )
    args = parser.parse_args()

    # Load the interview
    print(f"Loading interview from: {args.interview_file}", file=sys.stderr, flush=True)
    try:
        interview = load_interview_from_file(args.interview_file)
    except Exception as e:
        print(f"ERROR: Failed to load interview: {e}", file=sys.stderr, flush=True)
        sys.exit(1)

    # Set the interview in the app
    app.set_interview(interview)

    # Determine port
    if args.port == 0:
        port = find_free_port()
    else:
        port = args.port

    # Print server ready message to stderr for subprocess detection
    server_url = f"http://{args.host}:{port}"
    pid = os.getpid()
    print(f"SERVER_READY with PID {pid}: {server_url}", file=sys.stderr, flush=True)

    # Set up signal handlers for graceful shutdown
    def handle_shutdown_signal(signum, frame):
        """Handle shutdown signals (SIGINT/SIGTERM) gracefully."""
        signal_name = signal.Signals(signum).name
        print(f"\n\nReceived {signal_name}, shutting down...", file=sys.stderr, flush=True)
        print_interview_results()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_shutdown_signal)
    signal.signal(signal.SIGTERM, handle_shutdown_signal)

    # Create uvicorn server config
    config = uvicorn.Config(
        app.app,
        host=args.host,
        port=port,
        log_level="warning",  # Minimal logging
        access_log=False       # Disable access logs
    )
    server = uvicorn.Server(config)

    # Start monitoring thread
    monitor_thread = threading.Thread(
        target=monitor_interview_completion,
        args=(server,),
        daemon=True
    )
    monitor_thread.start()

    # Run server (blocks until should_exit is True)
    server.run()


if __name__ == '__main__':
    main()
