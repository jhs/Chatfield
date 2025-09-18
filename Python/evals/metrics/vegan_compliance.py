"""Vegan compliance metrics for Chatfield evaluation (GitHub Issue #5)."""

from typing import List
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams


class VeganComplianceMetric(GEval):
    """Custom metric to ensure no animal products mentioned after vegan disclosure."""

    def __init__(self, threshold: float = 1.0):
        super().__init__(
            name="Vegan Compliance",
            criteria="""Evaluate if the conversation in 'actual output' properly respects
            vegan dietary restrictions after disclosure in 'input'. Critical requirements:

            1. ZERO offers of meat (beef, chicken, pork, fish, seafood, etc.)
            2. ZERO offers of dairy (milk, cheese, butter, yogurt, cream, etc.)
            3. ZERO offers of eggs in any form
            4. ZERO offers of honey or other animal-derived ingredients
            5. ZERO suggestions that could contain hidden animal products without clarification
            6. Offers appropriate plant-based alternatives when relevant
            7. Natural acknowledgment of vegan preference without awkwardness
            8. Maintains conversational flow while respecting restrictions

            Score 1.0 only if absolutely NO animal products are mentioned after disclosure.
            Score 0.0 if ANY animal product is suggested, or implied.""",
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT
            ],
            threshold=threshold,
            strict_mode=True
        )


class AnimalProductDetector(GEval):
    """Strict detector for any animal product mentions."""

    # Comprehensive list of animal products to detect
    ANIMAL_PRODUCTS = [
        # Meat
        "beef", "steak", "burger", "chicken", "pork", "bacon", "ham", "sausage",
        "turkey", "lamb", "veal", "duck", "fish", "salmon", "tuna", "shrimp",
        "crab", "lobster", "seafood", "meat", "poultry", "wings", "ribs",
        "brisket", "roast", "chops", "tenderloin", "filet", "sirloin",

        # Dairy
        "milk", "cheese", "butter", "cream", "yogurt", "ice cream", "whey",
        "casein", "lactose", "mozzarella", "cheddar", "parmesan", "dairy",
        "milkshake", "latte", "cappuccino", "sour cream", "cottage cheese",
        "ricotta", "gouda", "brie", "camembert", "feta", "ghee",

        # Eggs
        "egg", "eggs", "mayonnaise", "mayo", "aioli", "omelet", "omelette",
        "scrambled", "poached", "benedict", "frittata", "quiche", "meringue",

        # Other animal products
        "honey", "gelatin", "lard", "tallow", "bone", "stock", "broth",
        "anchovy", "worcestershire", "caesar", "ranch", "oyster", "collagen"
    ]

    def __init__(self, threshold: float = 1.0):
        products_list = ', '.join(self.ANIMAL_PRODUCTS[:30])
        super().__init__(
            name="Animal Product Detection",
            criteria=f"""Scan the 'actual output' for ANY mention of animal products
            after vegan disclosure is indicated in 'context'.

            Animal products include but are not limited to:
            {products_list}... and many more.

            Instructions:
            - If 'context' indicates no vegan disclosure, score 1.0 (not applicable)
            - If 'context' indicates vegan was disclosed:
              * Score 0.0 if ANY animal product is found in output
              * Score 1.0 only if absolutely NO animal products are mentioned

            Be extremely strict - even indirect references, menu items that typically
            contain animal products, or ambiguous items should be flagged unless
            explicitly marked as vegan.""",
            evaluation_params=[
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.CONTEXT
            ],
            threshold=threshold
        )


class NaturalAcknowledgmentMetric(GEval):
    """Evaluates if vegan preference is acknowledged naturally."""

    def __init__(self, threshold: float = 0.7):
        super().__init__(
            name="Natural Vegan Acknowledgment",
            criteria="""Evaluate how naturally the AI acknowledges and adapts to
            the vegan disclosure in the conversation:

            Positive indicators (increase score):
            1. Acknowledges the vegan preference without making it awkward
            2. Smoothly transitions to plant-based options
            3. Provides helpful plant-based suggestions when appropriate
            4. Maintains normal conversation flow
            5. Shows understanding without being patronizing
            6. Uses terms like "plant-based" naturally

            Negative indicators (decrease score):
            1. Over-emphasizing or repeatedly mentioning "vegan"
            2. Making the preference seem unusual or difficult
            3. Apologizing excessively for previous suggestions
            4. Breaking conversation flow with awkward transitions
            5. Being patronizing or preachy about veganism

            Good example: "Great! Let me suggest some delicious plant-based options..."
            Bad example: "OH YOU'RE VEGAN! Let me completely change everything!"

            Score 0.8-1.0 for natural, smooth acknowledgment
            Score 0.6-0.8 for acceptable but slightly awkward
            Score below 0.6 for poor handling""",
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT
            ],
            threshold=threshold
        )


class VeganAlternativeQualityMetric(GEval):
    """Evaluates the quality of vegan alternatives offered."""

    def __init__(self, threshold: float = 0.75):
        super().__init__(
            name="Vegan Alternative Quality",
            criteria="""Evaluate the quality and appropriateness of plant-based
            alternatives offered after vegan disclosure:

            High quality alternatives should be:
            1. Genuinely plant-based (no hidden animal products)
            2. Appealing and well-described
            3. Nutritionally adequate replacements
            4. Diverse in options (not just salads)
            5. Clearly marked or confirmed as vegan
            6. Comparable to non-vegan options in satisfaction

            Poor alternatives include:
            1. Only offering side dishes or salads
            2. Removing items without replacement
            3. Vague items that might contain animal products
            4. Limited or boring options
            5. Treating vegan options as an afterthought

            Score based on the quality, variety, and appeal of alternatives offered.""",
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.CONTEXT
            ],
            threshold=threshold
        )