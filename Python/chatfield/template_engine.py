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

        # ===== Text Processing Helpers =====

        def dedent_helper(this, text: str) -> str:
            """Remove leading indentation from text blocks."""
            return textwrap.dedent(text)

        def indent_helper(this, level: int, text: str) -> str:
            """Add consistent indentation to text blocks."""
            indent = " " * level
            lines = text.split('\n')
            return '\n'.join(indent + line if line else line for line in lines)

        # def trim_helper(this, options):
        #     """Clean whitespace - removes excess whitespace while preserving structure."""
        #     context = (args, kwargs)
        #     content = options['fn'](context)
        #     # Trim start and end, collapse multiple blank lines to max 2
        #     return content.strip().replace('\n\n\n', '\n\n')

        # ===== Markdown Formatting Helpers =====

        def section_helper(this, title: str, level: int = 1) -> str:
            """Section header helper."""
            return '#' * min(level, 6) + ' ' + title

        def bullet_helper(this, text: str, indent: int = 0) -> str:
            """Bullet point helper with optional indentation."""
            return ' ' * (indent * 2) + '- ' + text

        # ===== List Helpers =====

        def join_helper(this, items: list, separator: str = ', ') -> str:
            """Join list items with separator."""
            if not items:
                return ''
            return separator.join(str(item) for item in items)

        def list_join_helper(this, items: list, separator: str = ', ', last_separator: str = ' and ') -> str:
            """List join with proper English grammar (commas and 'and')."""
            if not items or len(items) == 0:
                return ''
            if len(items) == 1:
                return str(items[0])
            if len(items) == 2:
                return str(items[0]) + last_separator + str(items[1])
            return separator.join(str(item) for item in items[:-1]) + last_separator + str(items[-1])

        # ===== Conditional Logic Helpers =====

        def any_helper(_this, *args) -> bool:
            """Return true if any argument is truthy."""
            result = any(args)
            return result
        
        def all_helper(_this, *args) -> bool:
            """Return true if all arguments are truthy."""
            result = all(args)
            return result
        
        def tidy_helper(this, options, at:int=0, pre:int=0, suf:int=0) -> str:
            """Trim and dedent block content, then re-indent."""
            content = options['fn'](this)
            content = str(content)
            content = textwrap.dedent(content).strip('\n')

            # Next, un-word-wrap, i.e. join lines that are not separated by blank lines.
            paragraphs = content.split('\n\n')
            paragraphs = [' '.join(p.splitlines()) for p in paragraphs]
            content = '\n\n'.join(paragraphs)

            indent_level = at
            if indent_level > 0:
                indent = '    ' * indent_level
                lines = content.split('\n')
                content = '\n'.join(indent + line if line else line for line in lines)
            return (' ' * pre) + content + (' ' * suf) if content else ''

        def when_helper(this, condition: bool, content: str) -> str:
            """Simple conditional content helper."""
            return content if condition else ''

        def if_any_helper(this, options, *conditions):
            """Check if any of the conditions are true."""
            if any(conditions):
                return options['fn'](this)
            elif 'inverse' in options:
                return options['inverse'](this)
            return ''

        def if_all_helper(this, options, *conditions):
            """Check if all conditions are true."""
            if all(conditions):
                return options['fn'](this)
            elif 'inverse' in options:
                return options['inverse'](this)
            return ''

        # ===== Field Specification Helpers =====

        def field_spec_helper(this, field: dict, spec_type: str, bob_role_name: str = 'user') -> str:
            """Format field specifications (must, reject, hint)."""
            specs = field.get('specs', {}).get(spec_type, [])

            # Special handling for confidential
            if spec_type == 'confidential' and field.get('specs', {}).get('confidential'):
                return f"    - **Confidential**: Do not inquire about this explicitly nor bring it up yourself. Continue your normal behavior. However, if the {bob_role_name} ever volunteers or implies it, you must record this information."

            if not specs or not isinstance(specs, list) or len(specs) == 0:
                return ''

            label = spec_type.capitalize()
            return '\n'.join(f"    - {label}: {rule}" for rule in specs)

        def all_field_specs_helper(this, field: dict, bob_role_name: str = 'user') -> str:
            """Format all field specs for a field."""
            if not field.get('specs'):
                return ''

            specs = []

            # Handle confidential first (special case)
            if field.get('specs', {}).get('confidential'):
                specs.append(f"    - **Confidential**: Do not inquire about this explicitly nor bring it up yourself. Continue your normal behavior. However, if the {bob_role_name} ever volunteers or implies it, you must record this information.")

            # Handle regular specs
            for spec_type in ['must', 'reject', 'hint']:
                spec_rules = field.get('specs', {}).get(spec_type, [])
                if spec_rules and isinstance(spec_rules, list):
                    label = spec_type.capitalize()
                    for rule in spec_rules:
                        specs.append(f"    - {label}: {rule}")

            return '\n'.join(specs)

        # ===== Block Helpers =====

        def conditional_section_helper(this, title: str, level: int, options, context):
            """Conditional section - only renders if content is non-empty."""
            content = options['fn'](context).strip()
            if not content:
                return ''
            header = '#' * min(level, 6) + ' ' + title
            return f"{header}\n\n{content}\n"

        # ===== String Helpers =====

        def concat_helper(this, *args) -> str:
            """Concatenate strings."""
            return ''.join(str(arg) for arg in args)

        # ===== Debug Helper (for development) =====

        def debug_helper(this, value, label: str = '') -> str:
            """Debug helper for development."""
            prefix = f"Debug [{label}]:" if label else "Debug:"
            import json
            print(prefix, json.dumps(value, indent=2))
            return ''

        # Register helpers with pybars
        self.helpers = {
            'all': all_helper,
            'any': any_helper,
            'tidy': tidy_helper,

            # 'dedent': dedent_helper,
            # 'indent': indent_helper,
            # 'trim': trim_helper,
            'section': section_helper,
            'bullet': bullet_helper,
            # 'join': join_helper,
            # 'listJoin': list_join_helper,
            # 'when': when_helper,
            # 'ifAny': if_any_helper,
            # 'ifAll': if_all_helper,
            # 'fieldSpec': field_spec_helper,
            # 'allFieldSpecs': all_field_specs_helper,
            # 'conditionalSection': conditional_section_helper,
            'concat': concat_helper,
            'debug': debug_helper
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