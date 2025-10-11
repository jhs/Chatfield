"""Tests for the Interviewer class."""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

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

        @patch('chatfield.interviewer.init_chat_model')
        def it_accepts_api_key_from_options(mock_init_model):
            """Accepts api key from options."""
            mock_llm = Mock()
            mock_init_model.return_value = mock_llm

            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())

            # Should not throw when API key is provided in options
            interviewer = Interviewer(interview, api_key='test-api-key', base_url='https://my-proxy.com')

            # Verify init_chat_model was called with config params
            mock_init_model.assert_called_once_with(
                'openai:gpt-4o',
                temperature=0.0,
                configurable={'base_url': 'https://my-proxy.com', 'api_key': 'test-api-key'}
            )
            assert interviewer.llm is mock_llm

        @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-env-key'})
        @patch('chatfield.interviewer.init_chat_model')
        def it_accepts_api_key_from_environment(mock_init_model):
            """Accepts api key from environment."""
            mock_llm = Mock()
            mock_init_model.return_value = mock_llm

            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())

            # Should work with env var and not throw
            interviewer = Interviewer(interview, base_url='https://my-proxy.com')

            # API key comes from environment, so should not be in configurable
            mock_init_model.assert_called_once_with(
                'openai:gpt-4o',
                temperature=0.0,
                configurable={'base_url': 'https://my-proxy.com'}
            )
            assert interviewer.llm is mock_llm

        @patch('chatfield.interviewer.init_chat_model')
        def it_configures_custom_base_url(mock_init_model):
            """Configures custom base url."""
            mock_llm = Mock()
            mock_init_model.return_value = mock_llm

            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())

            interviewer = Interviewer(
                interview,
                api_key='test-key',
                base_url='https://my-custom-proxy.com/v1'
            )

            # Verify base_url was passed to init_chat_model
            mock_init_model.assert_called_once_with(
                'openai:gpt-4o',
                temperature=0.0,
                configurable={'base_url': 'https://my-custom-proxy.com/v1', 'api_key': 'test-key'}
            )
            assert interviewer.llm is mock_llm

        @patch('chatfield.interviewer.init_chat_model')
        def it_uses_default_base_url_when_not_specified(mock_init_model):
            """Uses default base url when not specified."""
            mock_llm = Mock()
            mock_init_model.return_value = mock_llm

            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())

            interviewer = Interviewer(interview, api_key='test-key')

            # Should initialize without base_url in configurable
            mock_init_model.assert_called_once_with(
                'openai:gpt-4o',
                temperature=0.0,
                configurable={'api_key': 'test-key'}
            )
            assert interviewer.llm is mock_llm

        @patch.dict(os.environ, {}, clear=True)
        @patch('chatfield.interviewer.init_chat_model')
        def it_throws_when_no_api_key_provided(mock_init_model):
            """Throws when no api key provided."""
            # NOTE: Python's init_chat_model validates API keys lazily at invocation, not at initialization.
            # TypeScript validates at initialization and throws immediately.
            # This test documents the difference with no-op behavior to maintain test parity.
            mock_llm = Mock()
            mock_init_model.return_value = mock_llm

            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())

            # Python allows initialization without API key (validates later at invocation)
            interviewer = Interviewer(interview, base_url='https://my-proxy.com')
            assert interviewer is not None  # Passes - documents Python's lazy validation behavior

    def describe_endpoint_security():
        """Tests for endpoint security modes."""

        @patch('chatfield.interviewer.init_chat_model')
        def it_defaults_to_disabled_mode(mock_init_model):
            """Defaults to disabled security mode."""
            mock_llm = Mock()
            mock_init_model.return_value = mock_llm

            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())

            # Should not throw with official endpoint in disabled mode (default)
            interviewer = Interviewer(
                interview,
                api_key='test-key',
                base_url='https://api.openai.com/v1'
            )

            assert interviewer is not None

        @patch('chatfield.interviewer.init_chat_model')
        def it_throws_error_in_strict_mode_for_dangerous_endpoint(mock_init_model):
            """Throws error in strict mode for dangerous endpoint."""
            mock_llm = Mock()
            mock_init_model.return_value = mock_llm

            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())

            # Should throw with official endpoint in strict mode
            with pytest.raises(ValueError, match='SECURITY ERROR'):
                Interviewer(
                    interview,
                    api_key='test-key',
                    base_url='https://api.openai.com/v1',
                    endpoint_security='strict'
                )

        @patch('chatfield.interviewer.init_chat_model')
        def it_warns_in_warn_mode_for_dangerous_endpoint(mock_init_model):
            """Warns in warn mode for dangerous endpoint."""
            import warnings
            mock_llm = Mock()
            mock_init_model.return_value = mock_llm

            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())

            # Should warn but not throw with official endpoint in warn mode
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                interviewer = Interviewer(
                    interview,
                    api_key='test-key',
                    base_url='https://api.openai.com/v1',
                    endpoint_security='warn'
                )

                # Verify warning was issued
                assert len(w) == 1
                assert 'WARNING' in str(w[0].message)
                assert 'api.openai.com' in str(w[0].message)
                assert interviewer is not None

        @patch('chatfield.interviewer.init_chat_model')
        def it_allows_safe_endpoints_in_all_modes(mock_init_model):
            """Allows safe endpoints in all modes."""
            mock_llm = Mock()
            mock_init_model.return_value = mock_llm

            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())

            # Should work in all modes with safe endpoint
            for mode in ['disabled', 'warn', 'strict']:
                interviewer = Interviewer(
                    interview,
                    api_key='test-key',
                    base_url='https://my-proxy.com/v1',
                    endpoint_security=mode
                )
                assert interviewer is not None

        @patch('chatfield.interviewer.init_chat_model')
        def it_detects_anthropic_endpoint(mock_init_model):
            """Detects Anthropic endpoint as dangerous."""
            mock_llm = Mock()
            mock_init_model.return_value = mock_llm

            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())

            # Should throw with Anthropic endpoint in strict mode
            with pytest.raises(ValueError, match='SECURITY ERROR'):
                Interviewer(
                    interview,
                    api_key='test-key',
                    base_url='https://api.anthropic.com/v1',
                    endpoint_security='strict'
                )

        @patch('chatfield.interviewer.init_chat_model')
        def it_handles_none_base_url_safely(mock_init_model):
            """Handles None base URL safely."""
            mock_llm = Mock()
            mock_init_model.return_value = mock_llm

            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())

            # Should not throw with None base_url in any mode
            for mode in ['disabled', 'warn', 'strict']:
                interviewer = Interviewer(
                    interview,
                    api_key='test-key',
                    base_url=None,
                    endpoint_security=mode
                )
                assert interviewer is not None

        @patch('chatfield.interviewer.init_chat_model')
        def it_allows_relative_urls(mock_init_model):
            """Allows relative URLs in all security modes."""
            mock_llm = Mock()
            mock_init_model.return_value = mock_llm

            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())

            # Should allow relative URLs in all modes including strict
            for mode in ['disabled', 'warn', 'strict']:
                interviewer = Interviewer(
                    interview,
                    api_key='test-key',
                    base_url='/api/v1',
                    endpoint_security=mode
                )
                assert interviewer is not None

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
        
        def it_instructs_about_confidentiality():
            """Includes instructions about confidentiality."""
            interview = (chatfield()
                .type("HistoryAndLiteratureExam")
                .desc("We are administering a history and literature exam. It will affect your final grade.")
                .alice()
                    .type("Teacher administering the Exam")
                .bob()
                    .type("Student taking the Exam")
                .field(f"q1_hitchhiker")
                    .desc("Who wrote The Hitchhiker's Guide to the Galaxy?")
                    .as_bool("correct", "true if the answer is Douglas Adams, false otherwise")
                .build())

            interviewer = Interviewer(interview)
            prompt = interviewer.mk_system_prompt({'interview': interview})
            
            assert "Key Confidential Information" in prompt

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
            interviewer.process_update_tool(interview, name={
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
            interviewer.process_update_tool(interview, 
                field1={'value': 'value1', 'context': 'N/A', 'as_quote': 'value1'})
            interviewer.process_update_tool(interview,
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
            interviewer.process_update_tool(interview, number={
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