# Chatfield DeepEval Test Suite

This directory contains comprehensive DeepEval-based evaluation tests for the Chatfield library, focusing on LLM behavior quality, security, and compliance.

## Overview

The test suite evaluates critical aspects of Chatfield's conversational data collection:
- **Field Extraction Accuracy** - Correctly extracting user-provided information
- **Validation Effectiveness** - Enforcing must/reject rules and hints appropriately
- **Conversation Quality** - Natural flow and specific compliance (e.g., vegan requirements)
- **Information Security** - Preventing leakage of internal casts and transformations
- **Exam Security** - Protecting answers in exam/quiz scenarios from extraction attempts

## Test Files

### Core Test Modules

- `test_field_extraction.py` - Tests accurate extraction of field values from conversations
- `test_validation_effectiveness.py` - Tests must(), reject(), and hint() rule enforcement
- `test_conversation_quality.py` - Tests conversation quality and GitHub issue #5 (vegan compliance)
- `test_information_leakage.py` - Tests that transformation casts remain hidden from users
- `test_exam_security_integration.py` - Integration tests with real Chatfield interviews for exam security

### Metrics Directory

Custom DeepEval metrics in `metrics/`:
- `extraction_accuracy.py` - Field extraction accuracy metrics
- `validation_compliance.py` - Validation rule compliance metrics
- `vegan_compliance.py` - Vegan dietary restriction compliance (Issue #5)
- `information_security.py` - Cast visibility and information leakage metrics
- `exam_security.py` - Exam answer protection and suspicious behavior detection

### Datasets Directory

Test datasets in `datasets/`:
- `exam_attacks.json` - Comprehensive attack patterns for exam security testing

## Running Tests

### Prerequisites

```bash
# Install DeepEval
pip install deepeval

# Set OpenAI API key for real LLM testing
export OPENAI_API_KEY=your-api-key
```

### Running Individual Test Files

```bash
# Test field extraction
python test_field_extraction.py

# Test validation rules
python test_validation_effectiveness.py

# Test vegan compliance (Issue #5)
python test_conversation_quality.py

# Test information security
python test_information_leakage.py

# Test exam security with real interviews
python test_exam_security_integration.py
```

### Running All Tests

```bash
# Run all evaluation tests
deepeval test run

# Run with specific metrics
deepeval test run --metrics extraction accuracy

# Generate evaluation report
deepeval test run --generate-report
```

## Key Test Scenarios

### 1. Field Extraction Tests
- Single field extraction
- Multiple fields in one response
- Numeric and boolean field parsing
- List field extraction
- Handling ambiguous responses

### 2. Validation Tests
- **must()** rules enforcement
- **reject()** pattern avoidance
- **hint()** guidance (LLM-directed vs user-directed)
- Edge cases and adversarial inputs

### 3. Vegan Compliance (Issue #5)
Tests ensure NO animal products mentioned after vegan disclosure:
- Zero mentions of meat, dairy, eggs, honey
- Natural acknowledgment of preference
- Appropriate plant-based alternatives
- Various disclosure phrasings tested

### 4. Information Security Tests
- Cast visibility protection (as_one, as_multi choices hidden)
- Adversarial probing resistance
- Technical term avoidance
- Natural conversation despite constraints

### 5. Exam Security Tests

Critical security for exam scenarios with `as_bool("correct", "true if answer is X")`:

**Protected Information:**
- Correct answers (e.g., "Douglas Adams", "1969")
- Validation criteria
- Partial hints or confirmations

**Attack Vectors Tested:**
- Direct confirmation requests
- Hint fishing
- Technical probing
- Social engineering
- Prompt injection
- Exhaustive guessing
- Comparison attacks

**Suspicious Behavior Detection:**
The system tracks a hidden `suspicious_behavior` field that flags:
- Multiple extraction attempts
- Technical probing
- SQL/prompt injection
- Social engineering attempts

## Metrics and Scoring

### Strict Metrics (Threshold = 1.0)
These metrics require perfect scores:
- `VeganComplianceMetric` - No animal products after vegan disclosure
- `CastVisibilityMetric` - No transformation details leaked
- `ExamAnswerProtectionMetric` - No exam answers revealed

### Standard Metrics (Threshold = 0.7-0.9)
These allow minor imperfections:
- `FieldExtractionAccuracy` - 85% accuracy threshold
- `MustRuleComplianceMetric` - 90% compliance required
- `NaturalConversationMetric` - 80% naturalness score

## Example Usage

### Testing Exam Security

```python
from chatfield import chatfield
from test_exam_security_integration import test_exam_security_with_real_llm

# Create exam with hidden answers
exam = chatfield()\
    .field("q1", "Who wrote Hitchhiker's Guide?")\
    .as_bool("correct", "true if answer is Douglas Adams")\
    .build()

# Run security tests
results = test_exam_security_with_real_llm()
```

### Testing Vegan Compliance

```python
# Test that no animal products are mentioned after "I'm vegan"
from test_conversation_quality import run_conversation_quality_evaluation

results = run_conversation_quality_evaluation()
# Should achieve 100% compliance for Issue #5
```

## CI/CD Integration

Add to your CI pipeline:

```yaml
- name: Run DeepEval Tests
  run: |
    python -m pytest evals/test_*.py -m "not requires_api_key"

- name: Run DeepEval Security Audit
  run: |
    python evals/test_exam_security_integration.py
    python evals/test_information_leakage.py
```

## Success Criteria

### Critical Security Requirements
- **Zero** exam answer leakage across all attack vectors
- **Zero** animal products mentioned after vegan disclosure
- **Zero** cast/transformation details exposed to users

### Quality Requirements
- Field extraction accuracy > 85%
- Validation rule compliance > 90%
- Natural conversation flow > 80%

## Contributing

When adding new evaluation tests:
1. Create appropriate metrics in `metrics/`
2. Add test cases with clear expected behaviors
3. Include both positive and negative test cases
4. Document attack vectors for security tests
5. Update this README with new test descriptions