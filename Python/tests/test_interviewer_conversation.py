"""Tests for the Interviewer class conversation functionality.
Mirrors TypeScript's interviewer_conversation.test.ts with identical test descriptions.
"""

import os
import pytest
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root .env file
project_root = Path(__file__).parent.parent.parent
env_file = project_root / '.env'
load_dotenv(env_file)

from chatfield import Interview, Interviewer, chatfield


def describe_interviewer_conversation():
    """Tests for Interviewer conversation flow."""
    
    def describe_go_method():
        """Tests for the go method conversation handling."""
        
        @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="Requires OpenAI API key")
        def it_starts_conversation_with_greeting():
            """Starts conversation with greeting message."""
            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())
            interviewer = Interviewer(interview)
            
            # Start conversation
            ai_message = interviewer.go(None)
            
            print(f"---------------\nAI Message:\n{ai_message}\n---------------")
            assert ai_message is not None
            assert isinstance(ai_message, str)
            assert len(ai_message) > 0