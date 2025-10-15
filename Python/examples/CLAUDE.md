# Python Examples - CLAUDE.md

This file provides guidance for working with the Python examples.

## Overview

This directory contains demonstration examples showcasing various Chatfield features through practical, runnable scripts. Each example is self-contained and demonstrates specific capabilities.

## Examples

```
examples/
├── favorite_number.py    # Comprehensive transformation demo (int, float, bool, languages)
├── job_interview.py      # Professional use case with validation and hints
├── restaurant_order.py   # Interactive ordering system
├── tech_request.py       # Technical support intake form
└── CLAUDE.md             # This file
```

### Key Examples

- **favorite_number.py**: Complete transformation system demo (as_int(), as_float(), as_bool(), as_lang(), as_set(), as_percent(), cardinality methods). Supports `--auto` flag for automated demo.
- **job_interview.py**: Professional HR/recruitment scenario with complex validation rules (must(), reject(), hint()).
- **restaurant_order.py**: Interactive food ordering with context-aware conversation and menu-based validation.
- **tech_request.py**: IT support ticket collection with multi-field form and technical constraints.

## Running Examples

```bash
# Basic execution
cd Python
python examples/favorite_number.py
python examples/job_interview.py

# Automated demo mode (where supported)
python examples/favorite_number.py --auto

# With custom API key
OPENAI_API_KEY=sk-... python examples/job_interview.py
```

**See**: [../../Documentation/Commands.md](../../Documentation/Commands.md) for complete command reference.

## Setup

```bash
cd Python
pip install -e .                          # Install package
export OPENAI_API_KEY=your-key-here       # Set API key
# Or create .env.secret file with: OPENAI_API_KEY=your-key-here
```

## Common Patterns

All examples use similar structure:

```python
from chatfield import chatfield, Interviewer

# Build interview
interview = chatfield()\
    .type("InterviewType")\
    .field("field_name", "Field description")\
    .must("validation rule")\
    .build()

# Run interview
interviewer = Interviewer(interview)
result = interviewer.go()

# Access collected data
print(result.field_name)
```

## Key Considerations

1. **API Key Required**: All examples require valid OpenAI API key
2. **Rate Limiting**: Be aware of API rate limits when running multiple examples
3. **Auto Mode**: Some examples support `--auto` flag for testing without user input
4. **Import Paths**: Examples may manipulate sys.path for development
5. **Python Version**: Requires Python 3.8+

## Adding New Examples

When creating new examples:

1. Follow naming pattern (lowercase with underscores)
2. Include comprehensive docstring at the top
3. Add argparse for CLI options (--auto, --debug, etc.)
4. Handle missing API keys gracefully
5. Demonstrate specific features clearly with comments
6. Test with both interactive and automated modes
7. Update this CLAUDE.md file

## Common Issues

- **ImportError**: Run `pip install -e ..` from Python directory
- **API Key Error**: Set OPENAI_API_KEY environment variable or use .env.secret file
- **Rate Limit**: Add delays between API calls or reduce example complexity

## Additional Resources

- **Python Implementation**: [../CLAUDE.md](../CLAUDE.md)
- **Builder API**: [../../Documentation/Builder_Api.md](../../Documentation/Builder_Api.md)
- **API Configuration**: [../../Documentation/Api_Configuration.md](../../Documentation/Api_Configuration.md)
- **TypeScript Examples**: [../../TypeScript/examples/CLAUDE.md](../../TypeScript/examples/CLAUDE.md) for comparison
