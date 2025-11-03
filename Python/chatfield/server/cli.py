"""CLI entry point for Chatfield FastAPI server."""

import os
import sys
import signal
import socket
import logging
import uvicorn
import argparse

from . import app

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


def main():
    """Run the Chatfield FastAPI server."""
    # Configure logging to show DEBUG and greater for chatfield.* only
    logging.basicConfig(
        level=logging.WARNING,  # Set root logger to WARNING to silence other libraries
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )
    # Enable DEBUG logging only for chatfield modules
    logging.getLogger('chatfield').setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(description='Chatfield FastAPI Server')
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

    # Run server with minimal logging
    # All logs go to stderr, stdout is reserved for interview results
    uvicorn.run(
        app.app,
        host=args.host,
        port=port,
        log_level="warning",  # Minimal logging
        access_log=False       # Disable access logs
    )


if __name__ == '__main__':
    main()
