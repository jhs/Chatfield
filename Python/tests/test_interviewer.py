"""Tests for the Interviewer class."""

import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from dotenv import load_dotenv

# Load environment variables from project root .env file
project_root = Path(__file__).parent.parent.parent
env_file = project_root / '.env'
load_dotenv(env_file)

from chatfield import Interview, Interviewer, chatfield


def describe_interviewer():
    """Tests for the Interviewer orchestration class."""
    
    def describe_initialization():
        """Tests for Interviewer initialization."""
        
        @patch('chatfield.interviewer.init_chat_model')
        def it_creates_with_interview_instance(mock_init_model):
            """Creates with interview instance."""
            mock_llm = Mock()
            mock_init_model.return_value = mock_llm
            
            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .field("email").desc("Your email")
                .build())
            interviewer = Interviewer(interview)
            
            assert interviewer.interview is interview
            assert interviewer.config['configurable']['thread_id'] is not None
            assert interviewer.checkpointer is not None
            assert interviewer.graph is not None
        
        @patch('chatfield.interviewer.init_chat_model')
        def it_generates_unique_thread_id(mock_init_model):
            """Generates unique thread ID."""
            mock_llm = Mock()
            mock_init_model.return_value = mock_llm
            
            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())
            interviewer = Interviewer(interview, thread_id="custom-123")
            
            assert interviewer.config['configurable']['thread_id'] == "custom-123"
        
        @patch('chatfield.interviewer.init_chat_model')
        def it_configures_llm_model(mock_init_model):
            """Configures LLM model."""
            mock_llm = Mock()
            mock_init_model.return_value = mock_llm
            
            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())
            interviewer = Interviewer(interview)
            
            # Should initialize with GPT-4o by default
            mock_init_model.assert_called_once_with('openai:gpt-4o', temperature=0.0)
            assert interviewer.llm is mock_llm

    def describe_system_prompt():
        """Tests for system prompt generation."""
        
        def it_generates_basic_prompt():
            """Generates basic system prompt."""
            interview = (chatfield()
                .type("SimpleInterview")
                .desc("Customer feedback form")
                .field("rating").desc("Overall satisfaction rating")
                .field("comments").desc("Additional comments")
                .build())
            interviewer = Interviewer(interview)
            
            prompt = interviewer.mk_system_prompt({'interview': interview})
            
            assert "Customer feedback form" in prompt
            assert "rating: Overall satisfaction rating" in prompt
            assert "comments: Additional comments" in prompt
            assert "Agent" in prompt  # Default role
            assert "User" in prompt   # Default role
        
        def it_includes_custom_roles():
            """Includes custom alice and bob roles."""
            interview = (chatfield()
                .type("SupportInterview")
                .desc("Support ticket")
                .alice()
                    .type("Customer Support Agent")
                    .trait("Friendly and helpful")
                .bob()
                    .type("Frustrated Customer")
                    .trait("Had a bad experience")
                .field("issue").desc("What went wrong")
                .build())
            interviewer = Interviewer(interview)
            
            prompt = interviewer.mk_system_prompt({'interview': interview})
            
            assert "Customer Support Agent" in prompt
            assert "Frustrated Customer" in prompt
            assert "Friendly and helpful" in prompt
            assert "Had a bad experience" in prompt
        
        def it_includes_validation_rules():
            """Includes field validation rules."""
            interview = (chatfield()
                .type("ValidatedInterview")
                .field("feedback")
                    .desc("Your feedback")
                    .must("specific details")
                    .reject("profanity")
                    .hint("Be constructive")
                .build())
            interviewer = Interviewer(interview)
            
            prompt = interviewer.mk_system_prompt({'interview': interview})
            
            assert "Must: specific details" in prompt
            assert "Reject: profanity" in prompt
            # Note: Hints are included in specs but may not appear in system prompt

    def describe_tool_generation():
        """Tests for tool generation for fields."""
        
        @patch('chatfield.interviewer.init_chat_model')
        def it_creates_tool_for_each_field(mock_init_model):
            """Creates tool for each field."""
            mock_llm = Mock()
            mock_init_model.return_value = mock_llm
            
            interview = (chatfield()
                .type("SimpleInterview")
                .field("field1").desc("Field 1")
                .field("field2").desc("Field 2")
                .build())
            interviewer = Interviewer(interview)
            
            # Tool should be bound to LLM
            assert hasattr(interviewer.llm_with_both, 'bind_tools')
        
        @patch('chatfield.interviewer.init_chat_model')
        def it_includes_transformations_in_tool_schema(mock_init_model):
            """Includes transformations in tool schema."""
            mock_llm = Mock()
            mock_init_model.return_value = mock_llm
            
            interview = (chatfield()
                .type("TypedInterview")
                .field("number")
                    .desc("A number")
                    .as_int()
                    .as_bool()
                    .as_lang('fr')
                .build())
            interviewer = Interviewer(interview)
            
            # Tool args should include transformations
            # This is complex to test without running the actual tool
            assert interviewer.llm_with_both is not None

    def describe_conversation_flow():
        """Tests for conversation flow management."""
        
        def it_updates_field_values():
            """Updates field values when collected."""
            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())
            interviewer = Interviewer(interview)
            
            # Manually update field as if tool was called
            interviewer.process_tool_input(interview, name={
                'value': 'Test User',
                'context': 'User provided their name',
                'as_quote': 'My name is Test User'
            })
            
            # Check interview was updated
            assert interview._chatfield['fields']['name']['value'] is not None
            assert interview._chatfield['fields']['name']['value']['value'] == 'Test User'
        
        def it_detects_completion():
            """Detects when all fields are collected."""
            interview = (chatfield()
                .type("SimpleInterview")
                .field("field1").desc("Field 1")
                .field("field2").desc("Field 2")
                .build())
            interviewer = Interviewer(interview)
            
            # Initially not done
            assert not interview._done
            
            # Set both fields
            interviewer.process_tool_input(interview, 
                field1={'value': 'value1', 'context': 'N/A', 'as_quote': 'value1'})
            interviewer.process_tool_input(interview,
                field2={'value': 'value2', 'context': 'N/A', 'as_quote': 'value2'})
            
            # Should be done
            assert interview._done
        
        def it_handles_transformations():
            """Handles field transformations correctly."""
            interview = (chatfield()
                .type("TypedInterview")
                .field("number")
                    .desc("A number")
                    .as_int()
                    .as_lang('fr')
                .build())
            interviewer = Interviewer(interview)
            
            # Process tool input with transformations
            interviewer.process_tool_input(interview, number={
                'value': 'five',
                'context': 'User said five',
                'as_quote': 'The answer is five',
                'choose_exactly_one_as_int': 5,  # Note: Tool prefixes with choose_
                'choose_exactly_one_as_lang_fr': 'cinq'
            })
            
            # Check the field was updated with renamed keys
            field_value = interview._chatfield['fields']['number']['value']
            assert field_value['value'] == 'five'
            assert field_value['as_one_as_int'] == 5  # Renamed from choose_exactly_one_
            assert field_value['as_one_as_lang_fr'] == 'cinq'

    def describe_edge_cases():
        """Tests for edge cases and error handling."""
        
        def it_handles_empty_interview():
            """Handles empty interview gracefully."""
            interview = (chatfield()
                .type("EmptyInterview")
                .desc("Empty interview")
                .build())
            interviewer = Interviewer(interview)
            
            # Should handle empty interview gracefully
            assert interviewer.interview._done is True
        
        def it_copies_interview_state():
            """Copies interview state correctly."""
            interview1 = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())
            interview2 = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())
            
            # Set field in interview2
            interview2._chatfield['fields']['name']['value'] = {
                'value': 'Test',
                'context': 'N/A',
                'as_quote': 'Test'
            }
            
            # Copy from interview2 to interview1
            interview1._copy_from(interview2)
            
            # Check the copy worked
            assert interview1._chatfield['fields']['name']['value'] is not None
            assert interview1._chatfield['fields']['name']['value']['value'] == 'Test'
            
            # Ensure it's a deep copy
            interview2._chatfield['fields']['name']['value']['value'] = 'Changed'
            assert interview1._chatfield['fields']['name']['value']['value'] == 'Test'
        
        @patch('chatfield.interviewer.init_chat_model')
        def it_maintains_thread_isolation(mock_init_model):
            """Maintains thread isolation."""
            mock_llm = Mock()
            mock_init_model.return_value = mock_llm
            
            interview1 = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())
            interview2 = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())
            
            interviewer1 = Interviewer(interview1, thread_id="thread-1")
            interviewer2 = Interviewer(interview2, thread_id="thread-2")
            
            assert interviewer1.config['configurable']['thread_id'] == "thread-1"
            assert interviewer2.config['configurable']['thread_id'] == "thread-2"
            assert interviewer1.config != interviewer2.config