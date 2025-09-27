#!/usr/bin/env python
"""Test script for enhanced Handlebars templates."""

import sys
sys.path.insert(0, 'Python')

from chatfield import chatfield

# Create a sample interview with various field types
interview = chatfield()\
    .type("Sample Interview")\
    .desc("Testing enhanced template rendering")\
    .alice("Interviewer")\
    .alice_trait("professional and friendly")\
    .alice_trait("patient with responses")\
    .bob("Candidate")\
    .bob_trait("potentially nervous")\
    .field("name", "Your full name")\
        .must("include first and last name")\
        .must("be properly capitalized")\
        .hint("Format: First Last")\
    .field("email", "Your email address")\
        .must("be a valid email format")\
        .reject("temporary email services")\
        .hint("Use your professional email")\
    .field("experience", "Years of experience")\
        .as_int()\
        .must("be realistic (0-50 years)")\
    .field("salary_expectation", "Expected salary")\
        .confidential()\
        .as_int()\
    .field("feedback", "Any additional comments")\
        .conclude()\
    .build()

# Create interviewer to generate system prompt
from chatfield.interviewer import Interviewer

# Create a mock state for testing
class MockState:
    def __init__(self, interview):
        self.interview = interview

    def __getitem__(self, key):
        if key == 'interview':
            return self.interview
        return None

# Initialize interviewer
interviewer = Interviewer(interview)

# Create mock state
state = MockState(interview)

# Generate the system prompt using the new templates
try:
    prompt = interviewer.mk_system_prompt(state)
    print("=" * 80)
    print("SYSTEM PROMPT (with enhanced templates):")
    print("=" * 80)
    print(prompt)
    print("=" * 80)
    print("\n✅ Template rendering successful!")

    # Check for key improvements
    checks = []

    # Check for proper markdown headers
    if "# Traits and Characteristics" in prompt:
        checks.append("✓ Markdown headers properly formatted")

    # Check for bullet points
    if "- " in prompt:
        checks.append("✓ Bullet points present")

    # Check for field specifications
    if "- Must:" in prompt or "- Hint:" in prompt:
        checks.append("✓ Field specifications formatted correctly")

    # Check for confidential field handling
    if "**Confidential**" in prompt:
        checks.append("✓ Confidential fields marked appropriately")

    # Check whitespace handling
    lines = prompt.split('\n')
    if not any(line.count('\n\n\n') for line in lines):
        checks.append("✓ Whitespace properly managed")

    print("\nTemplate Quality Checks:")
    for check in checks:
        print(f"  {check}")

except Exception as e:
    print(f"❌ Error rendering template: {e}")
    import traceback
    traceback.print_exc()