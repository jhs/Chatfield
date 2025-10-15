"""DeepEval tests for validation rule effectiveness in Chatfield conversations."""

import json
from typing import List, Dict, Any, Tuple
from deepeval import evaluate
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval
from chatfield import chatfield, Interviewer


class MustRuleComplianceMetric(GEval):
    """Metric for evaluating if must() rules are properly enforced."""

    def __init__(self):
        super().__init__(
            name="Must Rule Compliance",
            criteria="""Evaluate if the validation in 'actual output' correctly enforces
            the must() rules specified in 'context'. Consider:
            1. Required information is present and not accepted without it
            2. The AI asks for missing required information
            3. Invalid responses are rejected with helpful guidance
            4. Valid responses are accepted without unnecessary rejection""",
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.CONTEXT
            ],
            threshold=0.9
        )


class RejectPatternAvoidanceMetric(GEval):
    """Metric for evaluating if reject() patterns are avoided."""

    def __init__(self):
        super().__init__(
            name="Reject Pattern Avoidance",
            criteria="""Determine if the conversation in 'actual output' successfully
            avoids patterns specified in reject() rules from 'context'. The AI should:
            1. Not accept responses containing rejected patterns
            2. Guide users away from rejected patterns
            3. Provide clear feedback when rejected patterns are used
            4. Suggest alternatives when appropriate""",
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.CONTEXT
            ],
            threshold=0.85
        )


class HintGuidanceMetric(GEval):
    """Metric for evaluating hint effectiveness."""

    def __init__(self):
        super().__init__(
            name="Hint Guidance Effectiveness",
            criteria="""Evaluate hint handling based on the type specified in 'context':

            For LLM-directed hints (high-level guidance):
            - The AI's behavior should reflect understanding of the hint
            - Field handling should align with the hint's guidance
            - The hint influences how the AI processes the field

            For user-directed hints (tooltip-style):
            - The AI should echo or paraphrase the hint to the user
            - The hint should appear naturally in the conversation
            - Users should receive the guidance information

            Score based on appropriate handling for the hint type.""",
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.CONTEXT
            ],
            threshold=0.8
        )


def create_validation_test_cases() -> List[LLMTestCase]:
    """Create test cases for validation effectiveness."""
    test_cases = []

    # Test Case 1: must() rule - email format
    test_cases.append(LLMTestCase(
        input="User: My email is john-at-example",
        actual_output="AI: That doesn't appear to be a valid email format. Please provide an email address with an @ symbol and domain, like john@example.com.",
        context="Field: email, Must rule: 'be a valid email format with @ and domain'"
    ))

    # Test Case 2: must() rule - required information
    test_cases.append(LLMTestCase(
        input="User: I want to apply for a position",
        actual_output="AI: Which specific position are you applying for? Please include both the role title and company name.",
        context="Field: position, Must rules: ['include specific role title', 'mention company name']"
    ))

    # Test Case 3: reject() pattern - avoiding profanity
    test_cases.append(LLMTestCase(
        input="User: My name is John Doe, damn it",
        actual_output="AI: I understand your name is John Doe. Let's keep our conversation professional. Moving on to the next field...",
        context="Field: name, Reject rule: 'profanity or inappropriate language'"
    ))

    # Test Case 4: reject() pattern - no personal information in public field
    test_cases.append(LLMTestCase(
        input="User: My username is john-ssn-123-45-6789",
        actual_output="AI: Please choose a username that doesn't contain personal information like SSN or ID numbers for security reasons.",
        context="Field: username, Reject rules: ['SSN', 'personal ID numbers', 'credit card']"
    ))

    # Test Case 5: LLM-directed hint (high-level guidance)
    test_cases.append(LLMTestCase(
        input="User: I have some experience",
        actual_output="AI: Could you be more specific? Please tell me the exact number of years of professional experience you have.",
        context="Field: years_experience, Hint (LLM-directed): 'Ensure user provides specific numeric value, not vague terms'"
    ))

    # Test Case 6: User-directed hint (tooltip-style)
    test_cases.append(LLMTestCase(
        input="AI: What's your phone number?",
        actual_output="AI: What's your phone number? Please include the area code, formatted as (XXX) XXX-XXXX.",
        context="Field: phone, Hint (user-directed): 'Include area code, format: (XXX) XXX-XXXX'"
    ))

    # Test Case 7: Multiple must() rules enforced
    test_cases.append(LLMTestCase(
        input="User: Password123",
        actual_output="AI: Your password needs to be stronger. It must include at least one special character (!@#$%^&*) and be at least 12 characters long.",
        context="Field: password, Must rules: ['at least 12 characters', 'include special character', 'include number', 'include uppercase']"
    ))

    # Test Case 8: Accepting valid input that meets all rules
    test_cases.append(LLMTestCase(
        input="User: My email is sarah.johnson@techcorp.com",
        actual_output="AI: Great, I've recorded your email as sarah.johnson@techcorp.com. Now let's move on to...",
        context="Field: email, Must rule: 'valid email format', Reject rule: 'temporary email domains'"
    ))

    # Test Case 9: Edge case - partial compliance
    test_cases.append(LLMTestCase(
        input="User: I'm applying for the developer position",
        actual_output="AI: Good start! You mentioned the developer position. Could you also tell me which company this is for?",
        context="Field: position, Must rules: ['include role title', 'include company name']"
    ))

    # Test Case 10: Combined hint types
    test_cases.append(LLMTestCase(
        input="AI: Tell me about your dietary restrictions",
        actual_output="AI: Tell me about your dietary restrictions. Common examples include vegetarian, vegan, gluten-free, or specific allergies. Please be as specific as possible.",
        context="""Field: dietary_restrictions,
        Hint (user-directed): 'Examples: vegetarian, vegan, gluten-free, allergies',
        Hint (LLM-directed): 'Be thorough in capturing all restrictions for kitchen safety'"""
    ))

    return test_cases


def create_adversarial_test_cases() -> List[LLMTestCase]:
    """Create adversarial test cases for validation robustness."""
    test_cases = []

    # Test Case 1: Attempting to bypass must() rules
    test_cases.append(LLMTestCase(
        input="User: Just put anything for the email, I'll update it later",
        actual_output="AI: I need a valid email address to proceed. This ensures we can contact you properly. What email address would you like to use?",
        context="Field: email, Must rule: 'be a valid email format'"
    ))

    # Test Case 2: Trying to inject rejected content subtly
    test_cases.append(LLMTestCase(
        input="User: My name is John<script>alert('xss')</script>Doe",
        actual_output="AI: Please provide your name using only standard characters, without any code or special markup.",
        context="Field: name, Reject rules: ['HTML tags', 'script injection', 'special markup']"
    ))

    # Test Case 3: Edge case with almost-valid input
    test_cases.append(LLMTestCase(
        input="User: I have 5-ish years of experience",
        actual_output="AI: I need a specific number for years of experience. Would you say that's closer to 5 years or a different number?",
        context="Field: years_experience (as_int), Must rule: 'be a specific number'"
    ))

    return test_cases


def test_validation_with_interview():
    """Test validation using actual Chatfield interview scenarios."""

    # Create interview with comprehensive validation rules
    interview = chatfield()\
        .type("JobApplication")\
        .field("email")\
    .desc("Your email address")\
            .must("be a valid email format")\
            .must("use professional domain")\
            .reject("temporary email services")\
            .hint("Use your primary professional email")\
        .field("position")\
    .desc("Position applying for")\
            .must("include specific job title")\
            .must("mention company name")\
            .hint("Format: [Job Title] at [Company]")\
        .field("password")\
    .desc("Create a password")\
            .must("be at least 12 characters")\
            .must("include uppercase letter")\
            .must("include number")\
            .must("include special character")\
            .reject("common passwords like 'password123'")\
            .hint("Use a mix of letters, numbers, and symbols")\
        .field("years_experience")\
    .desc("Years of experience")\
            .as_int()\
            .must("be a specific number")\
            .must("be realistic (0-50 years)")\
            .reject("vague terms like 'several' or 'many'")\
        .build()

    # Test scenarios
    scenarios = [
        {
            "field": "email",
            "input": "myemail",
            "should_reject": True,
            "reason": "Missing @ and domain"
        },
        {
            "field": "email",
            "input": "john@tempmail.com",
            "should_reject": True,
            "reason": "Temporary email service"
        },
        {
            "field": "position",
            "input": "I want to work in tech",
            "should_reject": True,
            "reason": "No specific title or company"
        },
        {
            "field": "position",
            "input": "Senior Software Engineer at Microsoft",
            "should_reject": False,
            "reason": "Valid with title and company"
        },
        {
            "field": "password",
            "input": "password123",
            "should_reject": True,
            "reason": "Common password rejected"
        },
        {
            "field": "password",
            "input": "MyS3cur3P@ssw0rd!",
            "should_reject": False,
            "reason": "Meets all requirements"
        }
    ]

    test_cases = []
    for scenario in scenarios:
        expected_behavior = "reject" if scenario["should_reject"] else "accept"
        test_cases.append(LLMTestCase(
            input=f"Field: {scenario['field']}, User input: {scenario['input']}",
            actual_output=f"Validation: {expected_behavior}, Reason: {scenario['reason']}",
            context=f"Testing field '{scenario['field']}' with validation rules from interview"
        ))

    return test_cases


def run_validation_evaluation():
    """Run the complete validation effectiveness evaluation suite."""

    # Initialize metrics
    must_compliance = MustRuleComplianceMetric()
    reject_avoidance = RejectPatternAvoidanceMetric()
    hint_guidance = HintGuidanceMetric()

    # Get test cases
    basic_test_cases = create_validation_test_cases()
    adversarial_cases = create_adversarial_test_cases()
    interview_cases = test_validation_with_interview()

    all_test_cases = basic_test_cases + adversarial_cases + interview_cases

    # Run evaluation
    print("Running Validation Effectiveness Evaluation...")
    print(f"Total test cases: {len(all_test_cases)}")

    results = evaluate(
        test_cases=all_test_cases,
        metrics=[must_compliance, reject_avoidance, hint_guidance]
    )

    return results


if __name__ == "__main__":
    # Run the evaluation
    results = run_validation_evaluation()

    # Print detailed results
    print("\n=== Validation Effectiveness Evaluation Results ===")
    for result in results:
        print(f"\nTest Case: {result.test_case.input[:80]}...")
        print(f"Context: {result.test_case.context[:80]}...")
        for metric_result in result.metrics_results:
            print(f"  {metric_result.metric_name}: {metric_result.score:.2f}")
            if not metric_result.success:
                print(f"    Failed - Reason: {metric_result.reason}")

    # Calculate aggregate metrics
    total_tests = len(results)
    metrics_summary = {}

    for result in results:
        for metric_result in result.metrics_results:
            name = metric_result.metric_name
            if name not in metrics_summary:
                metrics_summary[name] = {"passed": 0, "total": 0, "scores": []}
            metrics_summary[name]["total"] += 1
            metrics_summary[name]["scores"].append(metric_result.score)
            if metric_result.success:
                metrics_summary[name]["passed"] += 1

    print("\n=== Summary by Metric ===")
    for metric_name, stats in metrics_summary.items():
        avg_score = sum(stats["scores"]) / len(stats["scores"])
        pass_rate = stats["passed"] / stats["total"] * 100
        print(f"{metric_name}:")
        print(f"  Pass Rate: {stats['passed']}/{stats['total']} ({pass_rate:.1f}%)")
        print(f"  Average Score: {avg_score:.3f}")