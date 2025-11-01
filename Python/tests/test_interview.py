"""Tests for Interview-specific functionality."""

import pytest
from chatfield import chatfield


def describe_interview():
    """Tests for the Interview class."""
    
    def describe_field_discovery():
        """Tests for field discovery and defaults."""
        
        def it_uses_field_name_when_no_description():
            """Uses field name as description when none provided."""
            instance = (chatfield()
                .type("TestInterview")
                .field("test_field")  # No description
                .build())
            
            # Should use field name as description
            assert instance._chatfield['fields']['test_field']['desc'] == 'test_field'
    
    def describe_field_access():
        """Tests for field access behavior."""
        
        def it_returns_none_for_uncollected_fields():
            """Returns None when accessing fields before collection."""
            instance = (chatfield()
                .type("TestInterview")
                .field("name").desc("Your name")
                .field("age").desc("Your age")
                .build())
            
            assert instance.name is None
            assert instance.age is None
    
    def describe_completion_state():
        """Tests for interview completion tracking."""
        
        def it_starts_with_done_as_false():
            """Starts with _done as False when fields exist."""
            instance = (chatfield()
                .type("TestInterview")
                .field("field1").desc("Field 1")
                .field("field2").desc("Field 2")
                .build())
            
            assert instance._done is False
        
        def it_becomes_done_when_all_fields_collected():
            """Becomes done when all fields are collected."""
            instance = (chatfield()
                .type("TestInterview")
                .field("field1").desc("Field 1")
                .field("field2").desc("Field 2")
                .build())
            
            # Initially not done
            assert instance._done is False
            
            # Set one field - still not done
            instance._chatfield['fields']['field1']['value'] = {
                'value': 'test1'
            }
            assert instance._done is False
            
            # Set both fields - now done
            instance._chatfield['fields']['field2']['value'] = {
                'value': 'test2'
            }
            assert instance._done is True
        
        def it_marks_empty_interview_as_done():
            """Marks empty interview as done by default."""
            empty = chatfield().build()
            assert empty._done is True
    
    def describe_enough_state():
        """Tests for _enough property (non-confidential/conclude fields complete)."""
        
        def it_starts_with_enough_as_false_when_normal_fields_exist():
            """Starts with _enough as False when normal fields exist."""
            instance = (chatfield()
                .type("TestInterview")
                .field("field1").desc("Normal field 1")
                .field("field2").desc("Normal field 2")
                .build())
            
            assert instance._enough is False
        
        def it_becomes_enough_when_normal_fields_collected():
            """Becomes enough when all non-confidential/conclude fields collected."""
            instance = (chatfield()
                .type("TestInterview")
                .field("normal1").desc("Normal field 1")
                .field("normal2").desc("Normal field 2")
                .field("secret").desc("Secret info").confidential()
                .field("rating").desc("Final rating").conclude()
                .build())
            
            # Initially not enough
            assert instance._enough is False
            assert instance._done is False
            
            # Set one normal field - still not enough
            instance._chatfield['fields']['normal1']['value'] = {
                'value': 'test1'
            }
            assert instance._enough is False
            assert instance._done is False
            
            # Set both normal fields - now enough (but not done)
            instance._chatfield['fields']['normal2']['value'] = {
                'value': 'test2'
            }
            assert instance._enough is True
            assert instance._done is False  # Still have confidential/conclude fields
            
            # Set confidential field - still enough, still not done
            instance._chatfield['fields']['secret']['value'] = {
                'value': 'secret info'
            }
            assert instance._enough is True
            assert instance._done is False
            
            # Set conclude field - now done
            instance._chatfield['fields']['rating']['value'] = {
                'value': '5 stars'
            }
            assert instance._enough is True
            assert instance._done is True
        
        def it_is_enough_with_only_confidential_fields():
            """Is enough when only confidential fields exist."""
            instance = (chatfield()
                .type("TestInterview")
                .field("secret1").desc("Secret 1").confidential()
                .field("secret2").desc("Secret 2").confidential()
                .build())
            
            # With only confidential fields, _enough is True
            assert instance._enough is True
            assert instance._done is False
        
        def it_is_enough_with_only_conclude_fields():
            """Is enough when only conclude fields exist."""
            instance = (chatfield()
                .type("TestInterview")
                .field("rating1").desc("Rating 1").conclude()
                .field("rating2").desc("Rating 2").conclude()
                .build())
            
            # With only conclude fields, _enough is True
            assert instance._enough is True
            assert instance._done is False
        
        def it_marks_empty_interview_as_enough():
            """Marks empty interview as enough by default."""
            empty = chatfield().build()
            assert empty._enough is True
            assert empty._done is True
    
    def describe_serialization():
        """Tests for interview serialization."""
        
        def it_serializes_to_dict_with_model_dump():
            """Serializes interview to dictionary with model_dump."""
            instance = (chatfield()
                .type("TestInterview")
                .field("name").desc("Your name")
                .build())
            dump = instance.model_dump()
            
            assert isinstance(dump, dict)
            assert dump['type'] == 'TestInterview'
            assert 'fields' in dump
            assert 'name' in dump['fields']
        
        def it_creates_independent_copy_on_dump():
            """Creates independent copy when dumping."""
            instance = (chatfield()
                .type("TestInterview")
                .field("name").desc("Your name")
                .build())
            dump = instance.model_dump()
            
            # Modify original and ensure dump is independent
            instance._chatfield['fields']['name']['value'] = {'value': 'test'}
            assert dump['fields']['name']['value'] is None  # Should still be None
    
    def describe_display_methods():
        """Tests for display and formatting methods."""
        
        def it_formats_with_pretty_method():
            """Formats interview data with _pretty method."""
            instance = (chatfield()
                .type("TestInterview")
                .field("name").desc("Your name")
                .field("age").desc("Your age")
                .build())
            
            # Set one field
            instance._chatfield['fields']['name']['value'] = {
                'value': 'Alice',
                'context': 'User provided name',
                'as_quote': 'My name is Alice'
            }
            
            pretty = instance._pretty()

            assert 'TestInterview' in pretty
            # Should show field values in pretty format
            assert 'name' in pretty or 'Alice' in pretty

    def describe_special_character_field_names():
        """Field names with special characters accessed via bracket notation."""

        def it_supports_brackets_in_field_names():
            """Supports brackets in field names via bracket notation."""
            instance = (chatfield()
                .type("TestInterview")
                .field("field[0]")
                    .desc("Test field with brackets")
                .build())

            assert instance["field[0]"] is None

        def it_supports_dots_in_field_names():
            """Supports dots in field names via bracket notation."""
            instance = (chatfield()
                .type("TestInterview")
                .field("user.name")
                    .desc("Test field with dots")
                .build())

            assert instance["user.name"] is None

        def it_supports_spaces_in_field_names():
            """Supports spaces in field names via bracket notation."""
            instance = (chatfield()
                .type("TestInterview")
                .field("full name")
                    .desc("Test field with spaces")
                .build())

            assert instance["full name"] is None

        def it_supports_reserved_words():
            """Supports Python reserved words via bracket notation."""
            instance = (chatfield()
                .type("TestInterview")
                .field("class")
                    .desc("Test field with reserved word")
                .build())

            assert instance["class"] is None

        def it_supports_pdf_style_hierarchical_names():
            """Supports PDF-style hierarchical field names via bracket notation."""
            instance = (chatfield()
                .type("PDFForm")
                .field("topmostSubform[0].Page1[0].f1_01[0]")
                    .desc("PDF form field")
                .build())

            assert instance["topmostSubform[0].Page1[0].f1_01[0]"] is None