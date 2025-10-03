# Getting Started with Chatfield (Python)

This guide walks you through creating your first Chatfield project in Python.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- OpenAI API key (see [Mandatory_Environment_File.md](Mandatory_Environment_File.md))

## Quick Start

### 1. Clone the Chatfield Repository

```bash
git clone https://github.com/jhs/Chatfield.git
cd Chatfield/Python
```

### 2. Set Up Virtual Environment

Note, **Ubuntu uses `python3`** instead of `python`. Other platforms typically use `python`. *Feedback welcome about success or failure on other platforms, thanks!*

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Chatfield in Editable Mode

```bash
# For basic usage
pip install --editable .

# For development (includes testing tools)
pip install --editable .[dev]
```

### 4. Configure API Key

Create a `.env.secret` file **in the Chatfield root folder**:

```bash
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

### 5. Create Your First Script

Create a file named `my_first_form.py`:

```python
import os
from chatfield import chatfield, Interviewer

# Load API key from environment
os.environ['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY', '')

# Define your form using the fluent builder API
form = (chatfield()
    .type('Example Form')
    .field('name')
        .desc('Your Name')
    .field('age')
        .desc('Your Age')
        .as_int()
    .build())

# Create the interviewer
interviewer = Interviewer(form)

# Start the conversation
if os.environ.get('OPENAI_API_KEY'):
    first_message = interviewer.go()
else:
    first_message = 'No OPENAI_API_KEY set yet'

# Display the results
print('-------------')
print(first_message)
print('-------------')
print(form._pretty())
```

### 6. Run Your Script

```bash
python my_first_form.py
```

## What's Happening?

1. **Form Definition**: The `chatfield()` builder creates a conversational form with two fields:
   - `name`: A text field for the user's name
   - `age`: A number field that will be validated and converted to an integer

2. **Interviewer**: The `Interviewer` class orchestrates the conversation using LangGraph

3. **Conversation Flow**: The `go()` method starts the conversation and returns the first message

4. **Pretty Print**: The `_pretty()` method displays the form structure and collected values

## Next Steps

### Add Validation

```python
form = (chatfield()
    .field('email')
        .desc('Your email address')
        .must('be a valid email format')
    .field('age')
        .desc('Your age')
        .as_int()
        .must('be between 18 and 120')
    .build())
```

### Add Transformation

```python
form = (chatfield()
    .field('languages')
        .desc('Programming languages you know')
        .as_list()
    .field('confirm')
        .desc('Do you agree to the terms?')
        .as_bool()
    .build())
```

### Add Multiple Choice

```python
form = (chatfield()
    .field('favorite_color')
        .desc('What is your favorite color?')
        .as_one(['Red', 'Blue', 'Green', 'Yellow'])
    .field('skills')
        .desc('What skills do you have?')
        .as_multi(['Python', 'JavaScript', 'Go', 'Rust'])
    .build())
```

### Customize the Conversation

```python
form = (chatfield()
    .type('Job Application')
    .desc('Collect information about job candidates')
    .alice('Hiring Manager')
    .alice_trait('professional and friendly')
    .bob('Job Candidate')
    .field('position')
        .desc('What position are you applying for?')
        .must('include the specific role and department')
    .build())
```

## Complete Example

Here's a more comprehensive example:

```python
import os
from chatfield import chatfield, Interviewer

os.environ['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY', '')

# Create a restaurant order form
form = (chatfield()
    .type('Restaurant Order')
    .desc('Take a customer order at a restaurant')
    .alice('Server')
    .alice_trait('friendly and attentive')
    .bob('Customer')

    .field('table_number')
        .desc('Table number')
        .as_int()
        .must('be between 1 and 50')

    .field('main_course')
        .desc('Main course selection')
        .as_one(['Steak', 'Salmon', 'Pasta', 'Salad'])

    .field('sides')
        .desc('Side dishes')
        .as_multi(['Fries', 'Rice', 'Vegetables', 'Soup'])

    .field('special_requests')
        .desc('Any special requests or dietary restrictions?')
        .hint('Allergies, preferences, etc.')

    .build())

interviewer = Interviewer(form)

# Start conversation
print(interviewer.go())

# In a real application, you would continue the conversation loop
# by collecting user responses and calling interviewer.respond(user_message)
```

## Running Tests

If you're developing with Chatfield, you can run the test suite:

```bash
# From the Chatfield/Python directory
cd Python
pip install -e ".[dev]"
python -m pytest
```

## Troubleshooting

### API Key Issues

If you see "No OPENAI_API_KEY set yet":
1. Verify your `.env.secret` file exists and contains the key
2. Make sure you've activated your virtual environment
3. Try setting the key directly: `export OPENAI_API_KEY=your-key-here`

### Import Errors

If you see `ModuleNotFoundError: No module named 'chatfield'`:
1. Ensure you've activated your virtual environment
2. Reinstall in editable mode: `pip install --editable .`

### Dependency Issues

If you encounter dependency conflicts:
```bash
pip install --editable . --upgrade
```

## Resources

- [Full Python Documentation](../Python/CLAUDE.md)
- [Python Examples](../Python/examples/)
- [Environment Setup](Mandatory_Environment_File.md)
- [Test Harmonization Guide](Test_Harmonization.md)

## Development Mode

To work on Chatfield itself:

```bash
cd Chatfield/Python
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

This installs Chatfield in editable mode, allowing you to modify the source code and see changes immediately.
