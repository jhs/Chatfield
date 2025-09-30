#!/usr/bin/env python
"""
LiteLLM Proxy Launcher for Chatfield Development

This script launches a LiteLLM proxy server for secure API key handling
in browser-based development. The proxy:
- Routes requests to OpenAI (or other providers)
- Provides rate limiting and usage tracking
- Keeps API keys server-side (not in browser)
- Enables CORS for local development

Usage:
    python litellm_proxy.py [--port PORT] [--host HOST]

Environment Variables:
    OPENAI_API_KEY - Required for OpenAI models
    LITELLM_PROXY_PORT - Port for proxy (default: 4000)
    LITELLM_PROXY_HOST - Host for proxy (default: 0.0.0.0)
"""

import argparse
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Launch LiteLLM proxy for Chatfield development"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=os.environ.get("LITELLM_PROXY_PORT", 4000),
        help="Port to run proxy on (default: 4000)",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("LITELLM_PROXY_HOST", "0.0.0.0"),
        help="Host to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--config",
        default="litellm_config.yaml",
        help="Path to LiteLLM config file (default: litellm_config.yaml)",
    )

    args = parser.parse_args()

    # Check if config file exists
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}", file=sys.stderr)
        print(f"Current directory: {Path.cwd()}", file=sys.stderr)
        sys.exit(1)

    # Check if OPENAI_API_KEY is set
    if not os.environ.get("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not set. Proxy may not work correctly.", file=sys.stderr)
        print("Set it with: export OPENAI_API_KEY=your-key", file=sys.stderr)

    print(f"Starting LiteLLM proxy on {args.host}:{args.port}")
    print(f"Config file: {config_path.absolute()}")
    print(f"Access the proxy at: http://localhost:{args.port}")
    print("\nPress Ctrl+C to stop the proxy\n")

    # Launch LiteLLM proxy using subprocess
    import subprocess

    cmd = [
        "litellm",
        "--config", str(config_path),
        "--port", str(args.port),
        "--host", args.host,
    ]

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nShutting down proxy...")
    except FileNotFoundError:
        print("\nError: litellm command not found.", file=sys.stderr)
        print("Install it with: pip install litellm", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\nError: Proxy exited with code {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()