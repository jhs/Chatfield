# CLAUDE.md

This file provides guidance to Claude Code when working with the Python examples in this directory.

## Overview

This directory contains demonstration examples of the Chatfield Python library, showcasing various use cases and features through practical, runnable scripts. Each example is designed to be self-contained and demonstrates specific capabilities of the conversational data collection framework.

## Project Structure

```
Python/examples/
├── favorite_number.py    # Comprehensive transformation demo (int, float, bool, languages, sets)
├── job_interview.py      # Professional use case with validation and hints
├── restaurant_order.py   # Interactive ordering system with context
├── tech_request.py       # Technical support intake form
└── CLAUDE.md            # This documentation file
```

## Key Files

### favorite_number.py
- **Purpose**: Demonstrates the complete transformation system
- **Features**: All transformation decorators (`@as_int`, `@as_float`, `@as_bool`, `@as_lang.*`, `@as_set`, `@as_percent`)
- **Cardinality**: Shows `@as_one`, `@as_maybe`, `@as_multi`, `@as_any` patterns
- **Usage**: Supports `--auto` flag for automated demo without user input

### job_interview.py
- **Purpose**: Professional HR/recruitment scenario
- **Features**: Complex validation rules, multiple constraints per field
- **Patterns**: Demonstrates `@must`, `@reject`, and `@hint` decorators
- **Use Case**: Shows how to build professional forms with business logic

### restaurant_order.py
- **Purpose**: Interactive food ordering system
- **Features**: Context-aware conversation, menu-based validation
- **Patterns**: Shows how to integrate domain knowledge into conversations
- **Use Case**: E-commerce and ordering systems

### tech_request.py
- **Purpose**: IT support ticket collection
- **Features**: Multi-field form with technical constraints
- **Patterns**: Demonstrates field dependencies and technical validation
- **Use Case**: Help desk and support systems

## Development Commands

### Running Examples

```bash
# Basic execution
python examples/favorite_number.py
python examples/job_interview.py
python examples/restaurant_order.py
python examples/tech_request.py

# Automated demo mode (where supported)
python examples/favorite_number.py --auto

# With custom OpenAI API key
OPENAI_API_KEY=sk-... python examples/job_interview.py

# Debug mode with verbose output
python examples/restaurant_order.py --debug
```

### Environment Setup

```bash
# Ensure you're in the Python directory
cd Python

# Install the package in development mode
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"

# Load environment variables from .env file
# Create a .env file with: OPENAI_API_KEY=your-key-here
```

## Architecture Notes

### Common Patterns

1. **Import Structure**: All examples use similar imports:
   ```python
   from chatfield import chatfield
   from chatfield import Interviewer
   from chatfield import alice, bob, must, hint, reject
   from chatfield import as_int, as_float, as_bool, as_lang
   ```

2. **Builder Pattern**: Examples use the fluent builder API:
   ```python
   interview = (chatfield()
       .type("InterviewType")
       .field("field_name")
       .desc("Field description")
       .must("validation rule")
       .build())
   ```

3. **Interviewer Usage**: Standard pattern for running interviews:
   ```python
   interviewer = Interviewer(interview)
   result = interviewer.run()
   ```

4. **Auto-Mode Support**: Examples may include automated responses:
   ```python
   if args.auto:
       interviewer = Interviewer(interview, mock_responses={
           'field_name': 'automated response'
       })
   ```

## Testing Approach

- Examples serve as integration tests for the library
- Each example tests specific feature combinations
- Run all examples as smoke tests after library changes
- Examples should be runnable without modification

## Important Patterns

### Path Management
- Examples add parent directory to sys.path for imports
- Use `Path(__file__).parent.parent` for reliable paths
- Handle both development and installed package scenarios

### Environment Variables
- Support loading from `.env` file via python-dotenv
- Always check for OPENAI_API_KEY before running
- Provide clear error messages if API key is missing

### Error Handling
- Examples should gracefully handle missing API keys
- Provide informative error messages for common issues
- Include `--help` documentation in argparse

### Demonstration Features
- Each example should focus on specific features
- Include comments explaining what's being demonstrated
- Provide both simple and complex usage patterns
- Support both interactive and automated modes where appropriate

## Known Considerations

1. **API Key Requirements**: All examples require valid OpenAI API key
2. **Rate Limiting**: Be aware of API rate limits when running multiple examples
3. **Mock Mode**: Some examples support `--auto` flag for testing without user input
4. **Import Paths**: Examples manipulate sys.path - this is intentional for development
5. **Async Operations**: Examples use synchronous API but library supports async
6. **Output Formatting**: Examples may include colored output using ANSI codes
7. **Python Version**: Examples require Python 3.8+ (same as library)

## Adding New Examples

When creating new examples:

1. Follow the existing naming pattern (lowercase with underscores)
2. Include comprehensive docstring at the top
3. Add argparse for CLI options (--auto, --debug, etc.)
4. Handle missing API keys gracefully
5. Include path manipulation for imports
6. Demonstrate specific features clearly
7. Add comments explaining non-obvious patterns
8. Test with both interactive and automated modes
9. Update this CLAUDE.md file with the new example

## Common Issues and Solutions

- **ImportError**: Ensure chatfield package is installed: `pip install -e ..`
- **API Key Error**: Set OPENAI_API_KEY environment variable or use .env file
- **Rate Limit**: Add delays between API calls or reduce example complexity
- **Path Issues**: Run examples from the Python directory