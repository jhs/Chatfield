"""CLI entry point for Chatfield FastAPI server."""

import sys
import argparse
import socket


def find_free_port():
    """Find a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


def main():
    """Run the Chatfield FastAPI server."""
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
    print(f"SERVER_READY:{server_url}", file=sys.stderr, flush=True)

    # Import here to avoid loading FastAPI/uvicorn if --help is used
    import uvicorn
    from .app import app

    # Run server with minimal logging
    # All logs go to stderr, stdout is reserved for interview results
    uvicorn.run(
        app,
        host=args.host,
        port=port,
        log_level="warning",  # Minimal logging
        access_log=False       # Disable access logs
    )


if __name__ == '__main__':
    main()
