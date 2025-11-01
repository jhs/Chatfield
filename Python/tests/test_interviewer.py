"""Tests for the Interviewer class."""

import os
import pytest
import warnings
from unittest.mock import Mock, patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

from chatfield import Interview, Interviewer, chatfield
from chatfield.interviewer import encode_field_name, decode_field_name


def describe_interviewer():
    """Tests for the Interviewer orchestration class."""
    
    def describe_initialization():
        """Tests for Interviewer initialization."""
        
        def it_creates_with_interview_instance():
            """Creates with interview instance."""
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
        
        def it_generates_unique_thread_id():
            """Generates unique thread ID."""
            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())
            interviewer = Interviewer(interview, thread_id="custom-123")

            assert interviewer.config['configurable']['thread_id'] == "custom-123"
        
        def it_configures_llm_model():
            """Configures LLM model."""
            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())
            interviewer = Interviewer(interview)

            # Should initialize with GPT-4o by default
            assert interviewer.llm is not None
            assert interviewer.llm.model_name == 'gpt-4o'

        def it_accepts_api_key_from_options():
            """Accepts api key from options."""
            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())

            # Should not throw when API key is provided in options
            interviewer = Interviewer(interview, api_key='test-api-key', base_url='https://my-proxy.com')

            # Verify LLM was configured correctly
            assert interviewer.llm is not None
            assert interviewer.llm.openai_api_key.get_secret_value() == 'test-api-key'
            assert interviewer.llm.openai_api_base == 'https://my-proxy.com'

        def it_configures_custom_base_url():
            """Configures custom base url."""
            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())

            interviewer = Interviewer(
                interview,
                api_key='test-key',
                base_url='https://my-custom-proxy.com/v1'
            )

            # Verify base_url was configured correctly
            assert interviewer.llm is not None
            assert interviewer.llm.openai_api_base == 'https://my-custom-proxy.com/v1'
            assert interviewer.llm.openai_api_key.get_secret_value() == 'test-key'

        def it_uses_default_base_url_when_not_specified():
            """Uses default base url when not specified."""
            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())

            interviewer = Interviewer(interview, api_key='test-key')

            # Should initialize without custom base_url (uses OpenAI default)
            assert interviewer.llm is not None
            assert interviewer.llm.openai_api_key.get_secret_value() == 'test-key'

    def describe_endpoint_security():
        """Tests for endpoint security modes."""

        def it_defaults_to_disabled_mode():
            """Defaults to disabled security mode."""
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

        def it_defaults_to_strict_mode_in_browser_environment():
            """Defaults to strict mode in browser environment."""
            # Isomorphic: Python runs server-side only and has no browser/Node.js
            # environment distinction. TypeScript tests browser environment detection
            # by mocking window object. This test documents the difference with no-op
            # behavior that passes to maintain identical test counts across languages.
            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())

            # Python is always server-side, so this test is N/A
            assert interview is not None

        def it_throws_error_in_strict_mode_for_dangerous_endpoint():
            """Throws error in strict mode for dangerous endpoint."""
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

        def it_warns_in_warn_mode_for_dangerous_endpoint():
            """Warns in warn mode for dangerous endpoint."""

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

        def it_allows_safe_endpoints_in_all_modes():
            """Allows safe endpoints in all modes."""
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

        def it_detects_anthropic_endpoint():
            """Detects Anthropic endpoint as dangerous."""
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

        def it_handles_none_base_url_safely():
            """Handles None base URL safely."""
            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())

            with pytest.raises(ValueError, match='SECURITY ERROR'):
                Interviewer(interview, base_url=None, endpoint_security='strict')

            i = Interviewer(interview, base_url=None, endpoint_security='disabled')
            assert i is not None

            i = None
            with warnings.catch_warnings(record=True) as w:
                i = Interviewer(interview, base_url=None, endpoint_security='warn')
            assert i is not None

        def it_cannot_disable_security_in_browser():
            """Cannot disable security in browser."""
            # Isomorphic: Python runs server-side only and has no browser environment.
            # TypeScript tests that disabling security in a browser throws an error by
            # mocking window object. This test documents the difference with no-op
            # behavior that passes to maintain identical test counts across languages.
            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())

            # Python is always server-side, so this test is N/A
            assert interview is not None

        def it_handles_relative_base_url_safely():
            """Allows relative URLs in all security modes."""
            interview = (chatfield()
                .type("SimpleInterview")
                .field("name").desc("Your name")
                .build())

            i = Interviewer(interview, base_url='/v1', endpoint_security='disabled')
            assert i is not None
            i = Interviewer(interview, base_url='/v1', endpoint_security='warn')
            assert i is not None
            i = Interviewer(interview, base_url='/v1', endpoint_security='strict')
            assert i is not None

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

            # Manually update field as if tool was called (using encoded field name)
            encoded_name = encode_field_name("name")
            interviewer.process_update_tool(interview, **{
                encoded_name: {
                    'value': 'Test User',
                    'context': 'User provided their name',
                    'as_quote': 'My name is Test User'
                }
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

            # Set both fields (using encoded field names)
            encoded_field1 = encode_field_name("field1")
            encoded_field2 = encode_field_name("field2")
            interviewer.process_update_tool(interview, **{
                encoded_field1: {'value': 'value1', 'context': 'N/A', 'as_quote': 'value1'}
            })
            interviewer.process_update_tool(interview, **{
                encoded_field2: {'value': 'value2', 'context': 'N/A', 'as_quote': 'value2'}
            })

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

            # Process tool input with transformations (using encoded field name)
            encoded_number = encode_field_name("number")
            interviewer.process_update_tool(interview, **{
                encoded_number: {
                    'value': 'five',
                    'context': 'User said five',
                    'as_quote': 'The answer is five',
                    'choose_exactly_one_as_int': 5,  # Note: Tool prefixes with choose_
                    'choose_exactly_one_as_lang_fr': 'cinq'
                }
            })

            # Check the field was updated with renamed keys
            field_value = interview._chatfield['fields']['number']['value']
            assert field_value['value'] == 'five'
            assert field_value['as_one_as_int'] == 5  # Renamed from choose_exactly_one_
            assert field_value['as_one_as_lang_fr'] == 'cinq'

    def describe_non_identifier_field_names():
        """Tests for field names that are not valid Python identifiers."""

        def it_handles_pdf_form_field_names():
            """Handles PDF form field names with brackets and dots."""
            # PDF forms often have field names like "topmostSubform[0].Page1[0].f1_01[0]"
            # These are not valid Python identifiers but should work with Chatfield
            interview = (chatfield()
                .type("PDFForm")
                .desc("W-9 tax form")
                .field("topmostSubform[0].Page1[0].f1_01[0]")
                    .desc("Full legal name")
                .field("topmostSubform[0].Page1[0].f1_02[0]")
                    .desc("Business name")
                .build())
            interviewer = Interviewer(interview)

            # Should be able to create update tool without errors
            from chatfield.interviewer import State
            state = State(
                messages=[],
                interview=interview,
                has_digested_confidentials=False,
                has_digested_concludes=False
            )
            update_tool = interviewer.llm_update_tool(state)

            # Verify the tool was created
            assert update_tool is not None

            # Get the tool's schema to verify encoded field names
            schema = update_tool.args_schema.model_json_schema()

            # The schema should use encoded field names (valid Python identifiers)
            properties = schema.get('properties', {})
            encoded_name1 = encode_field_name("topmostSubform[0].Page1[0].f1_01[0]")
            encoded_name2 = encode_field_name("topmostSubform[0].Page1[0].f1_02[0]")
            assert encoded_name1 in properties
            assert encoded_name2 in properties

            # Verify the encoded names are valid identifiers
            assert encoded_name1.isidentifier()
            assert encoded_name2.isidentifier()

        def it_processes_tool_calls_with_non_identifier_field_names():
            """Processes tool calls with non-identifier field names."""
            interview = (chatfield()
                .type("PDFForm")
                .field("user.name")
                    .desc("User name with dot")
                .field("field[0]")
                    .desc("Field with brackets")
                .build())
            interviewer = Interviewer(interview)

            # Simulate tool call with encoded field names
            encoded_user_name = encode_field_name("user.name")
            encoded_field_0 = encode_field_name("field[0]")
            interviewer.process_update_tool(interview, **{
                encoded_user_name: {
                    'value': 'John Doe',
                    'context': 'User provided name',
                    'as_quote': 'My name is John Doe'
                },
                encoded_field_0: {
                    'value': 'test value',
                    'context': 'User provided value',
                    'as_quote': 'The value is test value'
                }
            })

            # Verify the fields were updated
            assert interview['user.name'] is not None
            assert interview['user.name'] == 'John Doe'
            assert interview['field[0]'] is not None
            assert interview['field[0]'] == 'test value'

        def it_handles_field_names_with_spaces():
            """Handles field names with spaces."""
            interview = (chatfield()
                .type("SimpleForm")
                .field("full name")
                    .desc("Full name with space")
                .field("email address")
                    .desc("Email address with space")
                .build())
            interviewer = Interviewer(interview)

            # Should create tool without errors
            from chatfield.interviewer import State
            state = State(
                messages=[],
                interview=interview,
                has_digested_confidentials=False,
                has_digested_concludes=False
            )
            update_tool = interviewer.llm_update_tool(state)
            assert update_tool is not None

            # Verify schema shows encoded field names
            schema = update_tool.args_schema.model_json_schema()
            properties = schema.get('properties', {})
            encoded_full_name = encode_field_name("full name")
            encoded_email = encode_field_name("email address")
            assert encoded_full_name in properties
            assert encoded_email in properties

        def it_handles_python_reserved_keywords_as_field_names():
            """Handles Python reserved keywords as field names."""
            interview = (chatfield()
                .type("ReservedKeywordsForm")
                .field("class")
                    .desc("Class field")
                .field("def")
                    .desc("Def field")
                .field("import")
                    .desc("Import field")
                .build())
            interviewer = Interviewer(interview)

            # Should create tool without errors
            from chatfield.interviewer import State
            state = State(
                messages=[],
                interview=interview,
                has_digested_confidentials=False,
                has_digested_concludes=False
            )
            update_tool = interviewer.llm_update_tool(state)
            assert update_tool is not None

            # Verify schema shows encoded field names
            schema = update_tool.args_schema.model_json_schema()
            properties = schema.get('properties', {})
            encoded_class = encode_field_name("class")
            encoded_def = encode_field_name("def")
            encoded_import = encode_field_name("import")
            assert encoded_class in properties
            assert encoded_def in properties
            assert encoded_import in properties

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
        
        def it_maintains_thread_isolation():
            """Maintains thread isolation."""
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


def describe_field_name_encoding():
    """Tests for field name encoding and decoding."""

    def describe_encode_field_name():
        """Tests for encode_field_name function."""

        def it_does_not_encode_simple_valid_identifiers():
            """Does not encode simple valid identifiers (returns as-is)."""
            # Simple names that are valid identifiers should not be encoded
            assert encode_field_name("name") == "name"
            assert encode_field_name("age") == "age"
            assert encode_field_name("email_address") == "email_address"
            assert encode_field_name("firstName") == "firstName"
            assert encode_field_name("_private") == "_private"
            assert encode_field_name("field123") == "field123"

        def it_encodes_names_with_dots():
            """Encodes field names containing dots."""
            assert encode_field_name("user.name") == "field_user_PCT2E_name"
            assert encode_field_name("a.b.c") == "field_a_PCT2E_b_PCT2E_c"

        def it_encodes_names_with_brackets():
            """Encodes field names containing brackets."""
            assert encode_field_name("field[0]") == "field_field_PCT5B_0_PCT5D_"
            assert encode_field_name("arr[5]") == "field_arr_PCT5B_5_PCT5D_"

        def it_encodes_pdf_form_field_names():
            """Encodes complex PDF form field names."""
            result = encode_field_name("topmostSubform[0].Page1[0].f1_01[0]")
            assert result == "field_topmostSubform_PCT5B_0_PCT5D__PCT2E_Page1_PCT5B_0_PCT5D__PCT2E_f1_01_PCT5B_0_PCT5D_"
            assert result.isidentifier()  # Must be valid Python identifier

        def it_encodes_names_with_spaces():
            """Encodes field names containing spaces."""
            assert encode_field_name("full name") == "field_full_PCT20_name"
            assert encode_field_name("first name") == "field_first_PCT20_name"

        def it_encodes_python_reserved_keywords():
            """Encodes Python reserved keywords."""
            assert encode_field_name("class") == "field_class"
            assert encode_field_name("def") == "field_def"
            assert encode_field_name("import") == "field_import"
            assert encode_field_name("for") == "field_for"

        def it_encodes_names_starting_with_digits():
            """Encodes field names starting with digits."""
            assert encode_field_name("9field") == "field_9field"
            assert encode_field_name("123") == "field_123"

        def it_encodes_special_characters():
            """Encodes field names with special characters."""
            assert encode_field_name("user@domain") == "field_user_PCT40_domain"
            assert encode_field_name("price$") == "field_price_PCT24_"
            assert encode_field_name("a+b") == "field_a_PCT2B_b"
            assert encode_field_name("a-b") == "field_a_PCT2D_b"

        def it_encodes_unicode_characters():
            """Encodes field names with unicode characters."""
            # French accented characters (Latin-1 range)
            result = encode_field_name("café")
            assert result == "field_caf_PCTE9_"
            assert result.isidentifier()

            # Spanish
            result = encode_field_name("año")
            assert result.startswith("field_a")
            assert result.isidentifier()

            # Emoji (multi-byte unicode)
            result = encode_field_name("rating😊")
            assert result == "field_rating_PCT1F60A_"
            assert result.isidentifier()

            # Japanese characters
            result = encode_field_name("名前")
            assert result.startswith("field_")
            assert result.isidentifier()

            # Cyrillic
            result = encode_field_name("имя")
            assert result.startswith("field_")
            assert result.isidentifier()

        def it_encodes_empty_string():
            """Encodes empty string."""
            assert encode_field_name("") == "field_"

        def it_always_produces_valid_identifiers():
            """Always produces valid Python identifiers."""
            test_cases = [
                "simple",
                "with.dots",
                "with[brackets]",
                "with spaces",
                "class",
                "9starts_with_digit",
                "special!@#$%chars",
                "topmostSubform[0].Page1[0].f1_01[0]"
            ]
            for field_name in test_cases:
                encoded = encode_field_name(field_name)
                assert encoded.isidentifier(), f"Encoded '{field_name}' to '{encoded}' which is not a valid identifier"

    def describe_decode_field_name():
        """Tests for decode_field_name function."""

        def it_decodes_simple_names():
            """Decodes simple field names (or returns as-is if not encoded)."""
            # Simple unencoded names return as-is
            assert decode_field_name("name") == "name"
            assert decode_field_name("age") == "age"
            assert decode_field_name("email_address") == "email_address"

        def it_decodes_names_with_dots():
            """Decodes field names with dots."""
            assert decode_field_name("field_user_PCT2E_name") == "user.name"
            assert decode_field_name("field_a_PCT2E_b_PCT2E_c") == "a.b.c"

        def it_decodes_names_with_brackets():
            """Decodes field names with brackets."""
            assert decode_field_name("field_field_PCT5B_0_PCT5D_") == "field[0]"
            assert decode_field_name("field_arr_PCT5B_5_PCT5D_") == "arr[5]"

        def it_decodes_pdf_form_field_names():
            """Decodes PDF form field names."""
            encoded = "field_topmostSubform_PCT5B_0_PCT5D__PCT2E_Page1_PCT5B_0_PCT5D__PCT2E_f1_01_PCT5B_0_PCT5D_"
            assert decode_field_name(encoded) == "topmostSubform[0].Page1[0].f1_01[0]"

        def it_decodes_names_with_spaces():
            """Decodes field names with spaces."""
            assert decode_field_name("field_full_PCT20_name") == "full name"

        def it_decodes_special_characters():
            """Decodes special characters."""
            assert decode_field_name("field_user_PCT40_domain") == "user@domain"
            assert decode_field_name("field_price_PCT24_") == "price$"

        def it_handles_unencoded_names():
            """Returns unencoded names as-is."""
            # Names without field_ prefix are assumed to be valid identifiers
            assert decode_field_name("simple_name") == "simple_name"
            assert decode_field_name("valid_identifier") == "valid_identifier"

    def describe_round_trip_encoding():
        """Tests for round-trip encoding/decoding."""

        def it_round_trips_simple_names():
            """Round-trips simple field names."""
            test_cases = ["name", "age", "email", "field123", "my_field"]
            for original in test_cases:
                encoded = encode_field_name(original)
                decoded = decode_field_name(encoded)
                assert decoded == original, f"Round-trip failed for '{original}': got '{decoded}'"

        def it_round_trips_pdf_form_names():
            """Round-trips PDF form field names."""
            test_cases = [
                "topmostSubform[0].Page1[0].f1_01[0]",
                "form[0].section[1].field[2]",
                "Page1[0].Text1[0]"
            ]
            for original in test_cases:
                encoded = encode_field_name(original)
                decoded = decode_field_name(encoded)
                assert decoded == original, f"Round-trip failed for '{original}': got '{decoded}'"

        def it_round_trips_special_characters():
            """Round-trips field names with special characters."""
            test_cases = [
                "user.name",
                "field[0]",
                "full name",
                "price$",
                "user@domain",
                "a+b",
                "a-b",
                "a/b",
                "a\\b",
                "a:b",
                "a;b",
                "a=b",
                "a?b",
                "a&b",
                "a|b",
                "a<b>c",
                "a{b}c",
                "(field)"
            ]
            for original in test_cases:
                encoded = encode_field_name(original)
                decoded = decode_field_name(encoded)
                assert decoded == original, f"Round-trip failed for '{original}': encoded='{encoded}', decoded='{decoded}'"

        def it_round_trips_python_keywords():
            """Round-trips Python reserved keywords."""
            import keyword
            for kw in keyword.kwlist[:10]:  # Test first 10 keywords
                encoded = encode_field_name(kw)
                decoded = decode_field_name(encoded)
                assert decoded == kw, f"Round-trip failed for keyword '{kw}': got '{decoded}'"

        def it_round_trips_names_with_leading_digits():
            """Round-trips names starting with digits."""
            test_cases = ["9field", "123", "0index", "999name"]
            for original in test_cases:
                encoded = encode_field_name(original)
                decoded = decode_field_name(encoded)
                assert decoded == original, f"Round-trip failed for '{original}': got '{decoded}'"

        def it_round_trips_unicode_characters():
            """Round-trips field names with unicode characters."""
            test_cases = [
                "prénom",
                "año",
                "名前",
                "имя",
                "rating😊",
                "café"
            ]
            for original in test_cases:
                encoded = encode_field_name(original)
                decoded = decode_field_name(encoded)
                assert decoded == original, f"Round-trip failed for '{original}': got '{decoded}'"

        def it_round_trips_empty_string():
            """Round-trips empty string."""
            original = ""
            encoded = encode_field_name(original)
            decoded = decode_field_name(encoded)
            assert decoded == original

        def it_round_trips_edge_cases():
            """Round-trips edge case field names."""
            test_cases = [
                "_",
                "__",
                "___",
                "_field",
                "field_",
                "_field_",
                "a_b_c",
                "............",
                "[[[[]]]]",
                "        ",  # Multiple spaces
                "\t\n",  # Whitespace
                "a.b[0].c[1].d[2]"
            ]
            for original in test_cases:
                encoded = encode_field_name(original)
                decoded = decode_field_name(encoded)
                assert decoded == original, f"Round-trip failed for '{original}': encoded='{encoded}', decoded='{decoded}'"

        def it_ensures_no_collisions():
            """Ensures different field names produce different encodings."""
            # These should all encode differently
            unique_names = [
                "field",
                "field.",
                "field[",
                "field]",
                "field.name",
                "fieldname",
                "field_name",
                "field name"
            ]
            encoded_names = [encode_field_name(name) for name in unique_names]

            # Check all encodings are unique
            assert len(encoded_names) == len(set(encoded_names)), "Collision detected: some field names encoded to the same value"

            # Verify round-trip for all
            for original in unique_names:
                encoded = encode_field_name(original)
                decoded = decode_field_name(encoded)
                assert decoded == original

        def it_handles_consecutive_special_characters():
            """Handles consecutive special characters correctly."""
            test_cases = [
                "a..b",
                "a[[b",
                "a]]b",
                "a..b..c",
                "[[[]]]"
            ]
            for original in test_cases:
                encoded = encode_field_name(original)
                decoded = decode_field_name(encoded)
                assert decoded == original, f"Round-trip failed for '{original}': got '{decoded}'"