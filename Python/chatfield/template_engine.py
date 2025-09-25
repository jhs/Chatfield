"""Handlebars template engine for prompt generation."""

import os
from typing import Dict, Any, Optional
from pathlib import Path
import textwrap
import pybars

class TemplateEngine:
    """Handles loading and rendering of Handlebars templates for prompts."""

    def __init__(self, templates_dir: Optional[Path] = None):
        """Initialize the template engine.

        Args:
            templates_dir: Path to templates directory. Defaults to /Prompts at project root.
        """
        if templates_dir is None:
            # Default to /Prompts directory at project root
            # Path from chatfield/template_engine.py to project root
            project_root = Path(__file__).parent.parent.parent
            templates_dir = project_root / "Prompts"

        self.templates_dir = Path(templates_dir)
        self.compiler = pybars.Compiler()
        self._template_cache = {}
        self._partials_cache = {}

        # Register custom helpers
        self._register_helpers()

        # Load partials
        self._load_partials()

    def _register_helpers(self):
        """Register custom Handlebars helpers."""

        def dedent_helper(this, text: str) -> str:
            """Remove leading indentation from text blocks."""
            return textwrap.dedent(text)

        def indent_helper(this, level: int, text: str) -> str:
            """Add consistent indentation to text blocks."""
            indent = " " * level
            lines = text.split('\n')
            return '\n'.join(indent + line if line else line for line in lines)

        def join_helper(this, items: list, separator: str = ', ') -> str:
            """Join list items with separator."""
            return separator.join(str(item) for item in items)

        # Register helpers with pybars
        self.helpers = {
            'dedent': dedent_helper,
            'indent': indent_helper,
            'join': join_helper
        }

    def _load_partials(self):
        """Load all partial templates from partials directory."""
        partials_dir = self.templates_dir / "partials"

        if not partials_dir.exists():
            return

        for partial_file in partials_dir.glob("*.hbs.txt"):
            # Get partial name without extension
            partial_name = partial_file.stem.replace('.hbs', '')

            with open(partial_file, 'r', encoding='utf-8') as f:
                partial_source = f.read()

            # Compile and cache the partial
            self._partials_cache[partial_name] = self.compiler.compile(partial_source)

    def _load_template(self, template_name: str) -> Any:
        """Load and compile a template file.

        Args:
            template_name: Name of the template file (without extension)

        Returns:
            Compiled template function
        """
        # Check cache first
        if template_name in self._template_cache:
            return self._template_cache[template_name]

        # Load template file
        template_path = self.templates_dir / f"{template_name}.hbs.txt"

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        with open(template_path, 'r', encoding='utf-8') as f:
            template_source = f.read()

        # Compile and cache
        template = self.compiler.compile(template_source)
        self._template_cache[template_name] = template

        return template

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with the given context.

        Args:
            template_name: Name of the template to render
            context: Dictionary of variables to pass to the template

        Returns:
            Rendered template string
        """
        template = self._load_template(template_name)

        # Render with partials and helpers
        result = template(context, partials=self._partials_cache, helpers=self.helpers)

        return result

    def clear_cache(self):
        """Clear the template cache to force reloading on next use."""
        self._template_cache.clear()
        self._partials_cache.clear()
        self._load_partials()