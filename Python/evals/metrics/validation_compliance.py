"""Validation compliance metrics for Chatfield evaluation."""

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams


class MustRuleComplianceMetric(GEval):
    """Metric for evaluating if must() rules are properly enforced."""

    def __init__(self, threshold: float = 0.9):
        super().__init__(
            name="Must Rule Compliance",
            criteria="""Evaluate if the validation in 'actual output' correctly enforces
            the must() rules specified in 'context'. Consider:

            1. Required information is present and not accepted without it
            2. The AI asks for missing required information
            3. Invalid responses are rejected with helpful guidance
            4. Valid responses are accepted without unnecessary rejection
            5. Error messages clearly explain what's needed

            Scoring:
            - 1.0: All must() rules perfectly enforced
            - 0.8-0.9: Rules enforced with minor communication issues
            - 0.6-0.8: Most rules enforced but some gaps
            - Below 0.6: Significant validation failures""",
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.CONTEXT
            ],
            threshold=threshold
        )


class RejectPatternAvoidanceMetric(GEval):
    """Metric for evaluating if reject() patterns are avoided."""

    def __init__(self, threshold: float = 0.85):
        super().__init__(
            name="Reject Pattern Avoidance",
            criteria="""Determine if the conversation in 'actual output' successfully
            avoids patterns specified in reject() rules from 'context'. The AI should:

            1. Not accept responses containing rejected patterns
            2. Guide users away from rejected patterns
            3. Provide clear feedback when rejected patterns are used
            4. Suggest alternatives when appropriate
            5. Maintain helpful tone while rejecting

            Scoring:
            - 1.0: All reject patterns properly avoided
            - 0.8-0.9: Patterns avoided with minor communication issues
            - 0.6-0.8: Most patterns avoided but some slip through
            - Below 0.6: Reject patterns not properly enforced""",
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.CONTEXT
            ],
            threshold=threshold
        )


class HintGuidanceMetric(GEval):
    """Metric for evaluating hint effectiveness."""

    def __init__(self, threshold: float = 0.8):
        super().__init__(
            name="Hint Guidance Effectiveness",
            criteria="""Evaluate hint handling based on the type specified in 'context':

            For LLM-directed hints (high-level guidance):
            - The AI's behavior should reflect understanding of the hint
            - Field handling should align with the hint's guidance
            - The hint influences how the AI processes the field
            - AI adapts its validation and prompting accordingly

            For user-directed hints (tooltip-style):
            - The AI should echo or paraphrase the hint to the user
            - The hint should appear naturally in the conversation
            - Users should receive the guidance information
            - Hints are presented at appropriate times

            Scoring:
            - 1.0: Perfect hint handling for the type
            - 0.8-0.9: Good hint usage with minor issues
            - 0.6-0.8: Hints partially utilized
            - Below 0.6: Hints ignored or mishandled""",
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.CONTEXT
            ],
            threshold=threshold
        )


class ValidationStrictnessMetric(GEval):
    """Metric for evaluating appropriate validation strictness."""

    def __init__(self, threshold: float = 0.85):
        super().__init__(
            name="Validation Strictness Balance",
            criteria="""Evaluate if validation is appropriately strict - not too lenient
            (accepting invalid data) nor too harsh (rejecting valid variations).

            The system should:
            1. Accept reasonable variations of valid input
            2. Reject clearly invalid input
            3. Handle edge cases appropriately
            4. Not be overly pedantic about format
            5. Focus on semantic correctness over syntactic perfection

            Example: Email validation should accept "john@example.com" and "John.Doe@Example.COM"
            but reject "john@" or "not-an-email"

            Score based on balance between false positives and false negatives.""",
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.CONTEXT
            ],
            threshold=threshold
        )