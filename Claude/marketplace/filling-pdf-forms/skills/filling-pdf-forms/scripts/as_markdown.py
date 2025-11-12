#!/usr/bin/env python
"""
Convert a file (typically PDF) to Markdown using Microsoft's MarkItDown library.
Outputs the markdown content to stdout for consumption by other tools.

Usage:
    python <script_name> <file_path>

Example:
    python scripts/as_markdown.py input.pdf > output.md
"""

import sys
from pathlib import Path

try:
    from markitdown import MarkItDown
except ImportError:
    print("Error: markitdown package is not installed.", file=sys.stderr)
    print("Install it with: pip install 'markitdown[all]'", file=sys.stderr)
    sys.exit(1)


def main():
    if len(sys.argv) != 2:
        script_name = sys.argv[0]
        print(f"Usage: python {script_name} <file_path>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]

    # Convert file to markdown
    try:
        md = MarkItDown()
        result = md.convert(file_path)
    except Exception as e:
        print(f"Error converting file: {e}", file=sys.stderr)
        sys.exit(1)
    else:
        print(result.text_content)


if __name__ == "__main__":
    main()
