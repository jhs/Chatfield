"""
Tests for validation functionality (must, reject, hint).
Uses real LLM to test validation behavior.
"""

import os
import pytest
from chatfield import chatfield
from chatfield.interviewer import Interviewer


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="Requires OpenAI API key")
def describe_validation():
    """A few unit tests for validation. Small and simple, because testing the prompts is out of scope."""

    def it_passes_must():
        """A 'must' validation should pass when requirement is met."""
        interview = (chatfield()
            .field("favorite_color")
            .desc("What's your favorite color?")
            .must("be a primary color name")
            .build())

        interviewer = Interviewer(interview)
        interviewer.go("My favorite color is blue")
        assert interview.favorite_color == "blue"

    def it_fails_must():
        """A 'must' validation should fail when requirement is not met."""
        interview = (chatfield()
            .field("favorite_color")
            .desc("What's your favorite color?")
            .must("be a primary color name")
            .build())

        interviewer = Interviewer(interview)
        interviewer.go("My favorite color is the planet Saturn")
        assert interview.favorite_color is None

    def it_passes_reject():
        """A 'reject' validation should pass when pattern is avoided."""
        interview = (chatfield()
            .field("first_name")
            .desc("What is your name? (No spaces or special characters allowed.)")
            .reject("contain spaces or special characters")\
            .build())

        interviewer = Interviewer(interview)
        interviewer.go("My name is Sam")
        assert interview.first_name == "Sam"

    def it_fails_reject():
        """A 'reject' validation should fail when pattern is present."""
        interview = (chatfield()
            .field("first_name")
            .desc("What is your name? (No spaces or special characters allowed.)")
            .reject("contain spaces or special characters")\
            .build())

        interviewer = Interviewer(interview)
        interviewer.go("My name is @l!ce")
        assert interview.first_name is None

    def it_must_and_reject_both_pass():
        """Both 'must' and 'reject' validations should work together."""
        # Create an interview with both must and reject requirements
        interview = chatfield()\
            .field("age")\
            .desc("How old are you?")\
            .must("be a number between 1 and 120")\
            .reject("negative numbers or text")\
            .build()

        interviewer = Interviewer(interview)
        interviewer.go("I am 25 years old")
        assert interview.age == "25"

    def it_hint_appears_in_system_prompt():
        """A 'hint' should appear in the system prompt."""
        form_no_hint = chatfield()\
            .field("email")\
            .desc("What's your email?")\
            .build()
        form_with_hint = chatfield()\
            .field("email")\
            .desc("What's your email?")\
            .hint("Format: name@example.com")\
            .build()

        interviewer = Interviewer(form_no_hint)
        prompt = interviewer.mk_system_prompt({'interview': form_no_hint})
        assert "Hint" not in prompt

        interviewer = Interviewer(form_with_hint)
        prompt = interviewer.mk_system_prompt({'interview': form_with_hint})
        assert "Hint" in prompt
    
    # TODO: There is some more logic to test, e.g. hints override validation.