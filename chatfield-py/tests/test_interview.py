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