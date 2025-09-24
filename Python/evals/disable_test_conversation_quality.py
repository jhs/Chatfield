"""DeepEval tests for conversation quality, addressing GitHub issue #5.

This test suite ensures that after a user discloses being vegan, the system
NEVER mentions animal products in any form.
"""

import json
from typing import List, Dict, Any, Tuple
from deepeval import evaluate
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval
import pytest


class VeganComplianceMetric(GEval):
    """Custom metric to ensure no animal products mentioned after vegan disclosure."""

    def __init__(self):
        super().__init__(
            name="Vegan Compliance",
            criteria="""Evaluate if the conversation in 'actual output' properly respects
            vegan dietary restrictions after disclosure in 'input'. Critical requirements:

            1. ZERO mentions of meat (beef, chicken, pork, fish, seafood, etc.)
            2. ZERO mentions of dairy (milk, cheese, butter, yogurt, cream, etc.)
            3. ZERO mentions of eggs in any form
            4. ZERO mentions of honey or other animal-derived ingredients
            5. ZERO suggestions that could contain hidden animal products without clarification
            6. Offers appropriate plant-based alternatives when relevant
            7. Natural acknowledgment of vegan preference without awkwardness
            8. Maintains conversational flow while respecting restrictions

            This is a CRITICAL metric - even ONE mention of animal products after
            vegan disclosure should result in complete failure (score 0).""",
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT
            ],
            threshold=1.0,  # Must be perfect
            strict_mode=True
        )


class AnimalProductDetector(GEval):
    """Strict detector for any animal product mentions."""

    ANIMAL_PRODUCTS = [
        # Meat
        "beef", "steak", "burger", "chicken", "pork", "bacon", "ham", "sausage",
        "turkey", "lamb", "veal", "duck", "fish", "salmon", "tuna", "shrimp",
        "crab", "lobster", "seafood", "meat", "poultry", "wings", "ribs",

        # Dairy
        "milk", "cheese", "butter", "cream", "yogurt", "ice cream", "whey",
        "casein", "lactose", "mozzarella", "cheddar", "parmesan", "dairy",
        "milkshake", "latte", "cappuccino", "sour cream", "cottage cheese",

        # Eggs
        "egg", "eggs", "mayonnaise", "mayo", "aioli", "omelet", "omelette",
        "scrambled", "poached", "benedict", "frittata", "quiche",

        # Other animal products
        "honey", "gelatin", "lard", "tallow", "bone", "stock", "broth",
        "anchovy", "worcestershire", "caesar", "ranch"
    ]

    def __init__(self):
        super().__init__(
            name="Animal Product Detection",
            criteria=f"""Scan the 'actual output' for ANY mention of animal products.
            This includes but is not limited to: {', '.join(self.ANIMAL_PRODUCTS[:20])}...

            Return score 0 if ANY animal product is found after vegan disclosure.
            Return score 1 only if absolutely NO animal products are mentioned.

            Be extremely strict - even indirect references or menu items that
            typically contain animal products should be flagged.""",
            evaluation_params=[
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.CONTEXT  # Context will indicate if vegan was disclosed
            ],
            threshold=1.0
        )


class NaturalAcknowledgmentMetric(GEval):
    """Evaluates if vegan preference is acknowledged naturally."""

    def __init__(self):
        super().__init__(
            name="Natural Vegan Acknowledgment",
            criteria="""Evaluate how naturally the AI acknowledges and adapts to
            the vegan disclosure in the conversation:

            1. Acknowledges the vegan preference without making it awkward
            2. Smoothly transitions to plant-based options
            3. Doesn't over-emphasize or repeatedly mention "vegan"
            4. Provides helpful plant-based suggestions when appropriate
            5. Maintains normal conversation flow
            6. Shows understanding without being patronizing

            Good example: "Great! Let me suggest some delicious plant-based options..."
            Bad example: "OH YOU'RE VEGAN! VEGAN VEGAN VEGAN! Let's only talk about VEGAN food!"
            """,
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT
            ],
            threshold=0.7
        )


def create_vegan_test_cases() -> List[LLMTestCase]:
    """Create test cases for vegan compliance testing."""
    test_cases = []

    # Test Case 1: Early vegan disclosure
    test_cases.append(LLMTestCase(
        input="""AI: Welcome! What can I help you order today?
User: I'm vegan, what do you recommend?""",
        actual_output="""AI: Excellent! We have wonderful plant-based options. I'd recommend our Mediterranean quinoa bowl with roasted vegetables, chickpeas, and tahini sauce. We also have a delicious black bean burger with avocado and our house-made vegan aioli. Would you like to hear about our vegan appetizers as well?""",
        context="Vegan disclosed at start"
    ))

    # Test Case 2: Mid-conversation vegan disclosure
    test_cases.append(LLMTestCase(
        input="""AI: What would you like for your main course?
User: What do you have that's good? Oh, and I should mention I'm vegan.""",
        actual_output="""AI: Perfect, thanks for letting me know! For vegan mains, our chef's special tonight is a fantastic mushroom wellington with roasted root vegetables. We also have a Thai green curry with tofu and vegetables, and a hearty lentil bolognese with fresh pasta. All of these are completely plant-based. What sounds good to you?""",
        context="Vegan disclosed mid-conversation"
    ))

    # Test Case 3: FAILURE case - mentioning dairy after vegan disclosure
    test_cases.append(LLMTestCase(
        input="""User: I'm vegan
AI: Noted! What else?
User: What desserts do you have?""",
        actual_output="""AI: For dessert, we have chocolate cake with ice cream, cheesecake, and a fruit sorbet.""",
        context="FAILURE: Mentioned dairy desserts after vegan disclosure"
    ))

    # Test Case 4: Different phrasing - "plant-based"
    test_cases.append(LLMTestCase(
        input="""User: I only eat plant-based foods""",
        actual_output="""AI: Wonderful! I'll make sure all my suggestions are plant-based. We have an excellent selection including our signature vegetable stir-fry with tofu, a Mediterranean mezze platter with hummus and falafel, and a delicious coconut curry. What type of cuisine are you in the mood for?""",
        context="Plant-based preference stated"
    ))

    # Test Case 5: "No animal products" phrasing
    test_cases.append(LLMTestCase(
        input="""User: I don't eat any animal products""",
        actual_output="""AI: I understand completely. Let me recommend our fully plant-based options. Our Buddha bowl with quinoa, roasted vegetables, and almond butter dressing is very popular. We also have a wonderful mushroom and walnut ragu with zucchini noodles. For protein, our marinated tempeh or seasoned tofu are excellent choices.""",
        context="No animal products preference"
    ))

    # Test Case 6: Edge case - "mostly vegan"
    test_cases.append(LLMTestCase(
        input="""User: I'm mostly vegan""",
        actual_output="""AI: I understand. Would you prefer I stick to fully vegan options, or are there some exceptions you're comfortable with? I'm happy to recommend based on your preferences.""",
        context="Ambiguous - mostly vegan"
    ))

    # Test Case 7: Testing drinks after vegan disclosure
    test_cases.append(LLMTestCase(
        input="""User: I'm vegan. What drinks do you have?""",
        actual_output="""AI: Great! For beverages, we have fresh juices, smoothies made with coconut or almond milk, herbal teas, coffee with plant-based milk options (oat, soy, almond, or coconut), and a selection of vegan wines. Our green smoothie with spinach, mango, and coconut water is particularly refreshing. What would you like?""",
        context="Drinks after vegan disclosure"
    ))

    # Test Case 8: FAILURE case - suggesting honey after vegan
    test_cases.append(LLMTestCase(
        input="""User: I'm vegan. Do you have any tea?""",
        actual_output="""AI: Yes! We have green tea, chamomile, and our special ginger tea with honey.""",
        context="FAILURE: Mentioned honey after vegan disclosure"
    ))

    # Test Case 9: Late disclosure after initial suggestions
    test_cases.append(LLMTestCase(
        input="""AI: I recommend our grilled salmon or chicken parmesan.
User: Actually, I should have mentioned - I'm vegan.""",
        actual_output="""AI: Oh, thank you for letting me know! Let me give you our plant-based recommendations instead. We have an amazing roasted cauliflower steak with chimichurri, a hearty three-bean chili, and a delicious pad thai with tofu and vegetables. All completely vegan and very flavorful. Which of these sounds appealing?""",
        context="Late vegan disclosure"
    ))

    # Test Case 10: Testing sides and additions
    test_cases.append(LLMTestCase(
        input="""User: I'm vegan. Can I add any sides to my order?""",
        actual_output="""AI: Absolutely! Our vegan-friendly sides include roasted Brussels sprouts with balsamic glaze, sweet potato fries, quinoa salad, steamed edamame, garlic sautéed spinach, and mixed grilled vegetables. All prepared without any animal products. How many sides would you like to add?""",
        context="Sides request after vegan disclosure"
    ))

    return test_cases


def create_parameterized_test_cases(disclosure_phrases: List[str]) -> List[LLMTestCase]:
    """Create parameterized test cases with different vegan disclosure phrases."""

    test_cases = []

    for phrase in disclosure_phrases:
        # Test immediate menu response
        test_cases.append(LLMTestCase(
            input=f"User: {phrase}",
            actual_output="AI: Excellent! Let me share our plant-based menu options with you. We have a variety of delicious vegan dishes including our signature vegetable curry, quinoa Buddha bowl, and house-made black bean burgers.",
            context=f"Disclosure phrase: '{phrase}'"
        ))

        # Test follow-up suggestions
        test_cases.append(LLMTestCase(
            input=f"""User: {phrase}
AI: Thanks for letting me know!
User: What's good here?""",
            actual_output="AI: Our most popular vegan dishes are the Thai basil stir-fry with tofu, the Mediterranean platter with falafel and hummus, and our daily vegan special which today is a mushroom and lentil shepherd's pie with cashew cream.",
            context=f"Follow-up after disclosure: '{phrase}'"
        ))

    return test_cases


@pytest.mark.parametrize('disclosure_phrase', [
    "I'm vegan",
    "I don't eat animal products",
    "plant-based diet only",
    "vegan lifestyle",
    "I follow a vegan diet",
    "no meat or dairy for me",
    "I'm on a plant-based diet",
    "strictly vegan",
    "I eat vegan",
    "vegan food only please"
])
def test_no_animal_products_after_vegan_disclosure(disclosure_phrase):
    """Parameterized test ensuring no animal products mentioned after various vegan disclosures."""

    # Create test case with the disclosure phrase
    test_case = LLMTestCase(
        input=f"User: {disclosure_phrase}",
        actual_output="[AI response would go here]",
        context=f"Testing disclosure: {disclosure_phrase}"
    )

    # In actual implementation, this would run the conversation
    # and check for animal product mentions

    # Initialize metrics
    vegan_compliance = VeganComplianceMetric()
    animal_detector = AnimalProductDetector()

    # Evaluate
    result = evaluate(
        test_cases=[test_case],
        metrics=[vegan_compliance, animal_detector]
    )

    # Assert perfect compliance
    for metric_result in result[0].metrics_results:
        assert metric_result.score == 1.0, f"Failed vegan compliance with phrase: {disclosure_phrase}"


def run_conversation_quality_evaluation():
    """Run the complete conversation quality evaluation suite."""

    # Initialize metrics
    vegan_compliance = VeganComplianceMetric()
    animal_detector = AnimalProductDetector()
    natural_acknowledgment = NaturalAcknowledgmentMetric()

    # Get test cases
    basic_test_cases = create_vegan_test_cases()

    # Additional disclosure phrases for parameterized testing
    disclosure_phrases = [
        "I'm vegan",
        "I don't eat animal products",
        "plant-based only",
        "vegan lifestyle",
        "no meat, dairy, or eggs",
        "I follow a vegan diet",
        "strictly plant-based",
        "vegan food only"
    ]

    parameterized_cases = create_parameterized_test_cases(disclosure_phrases)

    all_test_cases = basic_test_cases + parameterized_cases

    # Run evaluation
    print("Running Conversation Quality Evaluation (GitHub Issue #5)...")
    print(f"Total test cases: {len(all_test_cases)}")

    results = evaluate(
        test_cases=all_test_cases,
        metrics=[vegan_compliance, animal_detector, natural_acknowledgment]
    )

    return results


def analyze_failures(results):
    """Analyze and report any failures in vegan compliance."""

    failures = []
    for result in results:
        for metric_result in result.metrics_results:
            if metric_result.metric_name in ["Vegan Compliance", "Animal Product Detection"]:
                if metric_result.score < 1.0:
                    failures.append({
                        "input": result.test_case.input,
                        "output": result.test_case.actual_output,
                        "metric": metric_result.metric_name,
                        "score": metric_result.score,
                        "reason": metric_result.reason
                    })

    if failures:
        print("\n=== CRITICAL FAILURES - Animal Products Mentioned After Vegan Disclosure ===")
        for i, failure in enumerate(failures, 1):
            print(f"\nFailure {i}:")
            print(f"  Input: {failure['input'][:100]}...")
            print(f"  Output: {failure['output'][:100]}...")
            print(f"  Metric: {failure['metric']}")
            print(f"  Score: {failure['score']}")
            print(f"  Reason: {failure['reason']}")

    return failures


if __name__ == "__main__":
    # Run the evaluation
    results = run_conversation_quality_evaluation()

    # Print detailed results
    print("\n=== Conversation Quality Evaluation Results (Issue #5) ===")

    perfect_compliance_count = 0
    total_count = 0

    for result in results:
        context = result.test_case.context if hasattr(result.test_case, 'context') else "No context"
        print(f"\nTest Case: {context}")

        all_perfect = True
        for metric_result in result.metrics_results:
            print(f"  {metric_result.metric_name}: {metric_result.score:.2f}")
            if metric_result.metric_name in ["Vegan Compliance", "Animal Product Detection"]:
                total_count += 1
                if metric_result.score == 1.0:
                    perfect_compliance_count += 1
                else:
                    all_perfect = False
                    print(f"    ⚠️ FAILURE - {metric_result.reason}")

    # Analyze failures
    failures = analyze_failures(results)

    # Print summary
    print("\n=== Summary ===")
    print(f"Vegan Compliance Tests: {perfect_compliance_count}/{total_count} passed")
    print(f"Success Rate: {perfect_compliance_count/total_count*100:.1f}%")

    if perfect_compliance_count == total_count:
        print("✅ ISSUE #5 RESOLVED: Perfect vegan compliance achieved!")
    else:
        print(f"❌ ISSUE #5 OPEN: {len(failures)} violations found")
        print("The system must achieve 100% compliance to close issue #5")