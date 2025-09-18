"""Field extraction accuracy metrics for Chatfield evaluation."""

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams


class FieldExtractionAccuracy(GEval):
    """Custom metric for evaluating field extraction accuracy."""

    def __init__(self, threshold: float = 0.85):
        super().__init__(
            name="Field Extraction Accuracy",
            criteria="""Evaluate if the extracted field values in 'actual output' correctly
            capture the information provided in the 'input' conversation. Consider:
            1. The extracted value accurately represents what the user said
            2. No information is fabricated or assumed
            3. The value is properly formatted for the field type
            4. Multiple field values are extracted when provided in one response

            Scoring guidelines:
            - 1.0: Perfect extraction, all values correct
            - 0.8-0.9: Minor formatting differences but semantically correct
            - 0.6-0.8: Most values correct, some minor issues
            - 0.4-0.6: Some values correct but significant issues
            - Below 0.4: Major extraction failures""",
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.EXPECTED_OUTPUT
            ],
            threshold=threshold
        )


class ExtractionCompletenessMetric(GEval):
    """Metric for evaluating if all required fields were extracted."""

    def __init__(self, threshold: float = 0.9):
        super().__init__(
            name="Extraction Completeness",
            criteria="""Determine if ALL fields mentioned in the 'expected output' are
            present and correctly extracted in the 'actual output'. Missing fields or
            null values where data was provided should be penalized.

            Scoring:
            - 1.0: All expected fields present with correct values
            - 0.8-0.9: All fields present, minor value discrepancies
            - 0.6-0.8: Most fields present, some missing or incorrect
            - 0.4-0.6: Many fields missing
            - Below 0.4: Majority of fields missing or wrong""",
            evaluation_params=[
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.EXPECTED_OUTPUT
            ],
            threshold=threshold
        )


class MultiFieldExtractionMetric(GEval):
    """Metric for evaluating extraction when multiple fields are mentioned in one response."""

    def __init__(self, threshold: float = 0.85):
        super().__init__(
            name="Multi-Field Extraction",
            criteria="""Evaluate the system's ability to extract multiple field values
            from a single user response. The system should:

            1. Identify all fields mentioned in the response
            2. Correctly associate values with their respective fields
            3. Not mix up values between fields
            4. Handle various formats (lists, sentences, structured data)

            Example: "I'm John Smith, my email is john@example.com and I have 5 years experience"
            Should extract: name="John Smith", email="john@example.com", years_experience="5"

            Score based on percentage of correctly extracted field-value pairs.""",
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.EXPECTED_OUTPUT
            ],
            threshold=threshold
        )