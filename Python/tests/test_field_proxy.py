"""Tests for FieldProxy string subclass functionality."""

from chatfield import chatfield


def describe_field_proxy():
    """Tests for the FieldProxy string subclass."""
    
    def describe_string_behavior():
        """Tests for string behavior of FieldProxy."""
        
        def it_acts_as_normal_string():
            """Acts as a normal string value."""
            instance = (chatfield()
                .type("TestInterview")
                .field("name").desc("Your name")
                .build())
            
            # Set field value
            instance._chatfield['fields']['name']['value'] = {
                'value': 'John Doe',
                'context': 'User provided their name',
                'as_quote': 'John Doe'
            }
            
            name = instance.name
            
            # Should act as string
            assert name == 'John Doe'
            assert str(name) == 'John Doe'
            assert len(name) == 8
        
        def it_supports_string_methods():
            """Supports standard string methods."""
            instance = (chatfield()
                .type("TestInterview")
                .field("name").desc("Your name")
                .build())
            
            instance._chatfield['fields']['name']['value'] = {
                'value': 'John Doe',
                'context': 'User provided their name',
                'as_quote': 'John Doe'
            }
            
            name = instance.name
            
            # String methods should work
            assert name.upper() == 'JOHN DOE'
            assert name.lower() == 'john doe'
            assert name.startswith('John')
            assert name.endswith('Doe')
            assert 'John' in name
    
    def describe_transformation_access():
        """Tests for accessing transformations via properties."""
        
        def it_provides_as_int_property():
            """Provides as_int transformation property."""
            instance = (chatfield()
                .type("TestInterview")
                .field("age")
                    .desc("Your age")
                    .as_int()
                .build())
            
            instance._chatfield['fields']['age']['value'] = {
                'value': '42',
                'context': 'User said forty-two',
                'as_quote': 'forty-two',
                'as_int': 42
            }
            
            age = instance.age
            assert age == '42'
            assert age.as_int == 42
        
        def it_provides_as_float_property():
            """Provides as_float transformation property."""
            instance = (chatfield()
                .type("TestInterview")
                .field("height")
                    .desc("Your height")
                    .as_float()
                .build())
            
            instance._chatfield['fields']['height']['value'] = {
                'value': '5.9',
                'context': 'User provided height',
                'as_quote': 'five point nine',
                'as_float': 5.9
            }
            
            height = instance.height
            assert height == '5.9'
            assert height.as_float == 5.9
        
        def it_provides_as_bool_property():
            """Provides as_bool transformation property."""
            instance = (chatfield()
                .type("TestInterview")
                .field("active")
                    .desc("Are you active?")
                    .as_bool()
                .build())
            
            instance._chatfield['fields']['active']['value'] = {
                'value': 'yes',
                'context': 'User confirmed',
                'as_quote': 'yes, I am active',
                'as_bool': True
            }
            
            active = instance.active
            assert active == 'yes'
            assert active.as_bool is True
        
        def it_provides_as_lang_properties():
            """Provides language transformation properties."""
            instance = (chatfield()
                .type("TestInterview")
                .field("greeting")
                    .desc("Say hello")
                    .as_lang('fr')
                    .as_lang('es')
                .build())
            
            instance._chatfield['fields']['greeting']['value'] = {
                'value': 'hello',
                'context': 'User greeted',
                'as_quote': 'hello there',
                'as_lang_fr': 'bonjour',
                'as_lang_es': 'hola'
            }
            
            greeting = instance.greeting
            assert greeting == 'hello'
            assert greeting.as_lang_fr == 'bonjour'
            assert greeting.as_lang_es == 'hola'
        
        def it_provides_as_quote_property():
            """Provides as_quote property for original quote."""
            instance = (chatfield()
                .type("TestInterview")
                .field("name").desc("Your name")
                .build())
            
            instance._chatfield['fields']['name']['value'] = {
                'value': 'John',
                'context': 'User introduction',
                'as_quote': 'My name is John'
            }
            
            name = instance.name
            assert name == 'John'
            assert name.as_quote == 'My name is John'
    
    def describe_edge_cases():
        """Tests for edge cases and error handling."""
        
        def it_handles_missing_transformations():
            """Handles accessing non-existent transformations."""
            instance = (chatfield()
                .type("TestInterview")
                .field("name").desc("Your name")
                .build())
            
            instance._chatfield['fields']['name']['value'] = {
                'value': 'test',
                'context': 'N/A',
                'as_quote': 'test'
            }
            
            name = instance.name
            
            # Accessing non-existent transformation should return None
            # or raise AttributeError depending on implementation
            try:
                result = name.as_int  # This transformation doesn't exist
                assert result is None  # May return None
            except AttributeError:
                pass  # Or may raise AttributeError
        
        def it_handles_null_values():
            """Handles null/None field values."""
            instance = (chatfield()
                .type("TestInterview")
                .field("name").desc("Your name")
                .build())
            
            # Field not yet collected
            name = instance.name
            assert name is None
        
        def it_preserves_original_value():
            """Preserves original string value despite transformations."""
            instance = (chatfield()
                .type("TestInterview")
                .field("number")
                    .desc("A number")
                    .as_int()
                    .as_float()
                    .as_lang('fr')
                .build())
            
            instance._chatfield['fields']['number']['value'] = {
                'value': '42',
                'context': 'User provided number',
                'as_quote': 'forty-two',
                'as_int': 42,
                'as_float': 42.0,
                'as_lang_fr': 'quarante-deux'
            }
            
            number = instance.number
            
            # Original string value preserved
            assert number == '42'
            assert str(number) == '42'
            
            # Transformations available as properties
            assert number.as_int == 42
            assert number.as_float == 42.0
            assert number.as_lang_fr == 'quarante-deux'