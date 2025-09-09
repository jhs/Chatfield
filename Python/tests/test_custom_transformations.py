"""
Test custom transformations demonstrating feature parity.
This test file shows how Python supports dynamic custom transformations.
"""

import pytest
from chatfield import chatfield


def describe_custom_transformations():
    """Tests for custom transformation features."""
    
    def describe_multiple_transformations():
        """Tests for multiple transformations on same field."""
        
        def it_applies_multiple_custom_transformations():
            """Applies multiple custom transformations on same field."""
            
            # Test multiple custom transformations on the same field
            form = (chatfield()
                .field('value')
                    .desc('Enter a value')
                    .as_int()  # Base transformation
                    .as_int('neg1', 'This is always -1')
                    .as_int('doubled', 'Double the integer value')
                    .as_int('squared', 'Square the integer value')
                    .as_bool('even', 'True if the integer is even')
                    .as_lang('fr', 'French translation')
                    .as_str('uppercase', 'Convert to uppercase')
                .build())
            
            # Check that all custom transformations were created
            fields = form._chatfield['fields']
            assert 'value' in fields
            
            casts = fields['value'].get('casts', {})
            
            # Check base transformations
            assert 'as_int' in casts
            
            # Check integer custom transformations
            assert 'as_int_neg1' in casts
            assert casts['as_int_neg1']['prompt'] == 'This is always -1'
            
            assert 'as_int_doubled' in casts
            assert casts['as_int_doubled']['prompt'] == 'Double the integer value'
            
            assert 'as_int_squared' in casts
            assert casts['as_int_squared']['prompt'] == 'Square the integer value'
            
            # Check boolean custom transformation
            assert 'as_bool_even' in casts
            assert casts['as_bool_even']['prompt'] == 'True if the integer is even'
            
            # Check language custom transformation
            assert 'as_lang_fr' in casts
            assert casts['as_lang_fr']['prompt'] == 'French translation'
            
            # Check string custom transformation
            assert 'as_str_uppercase' in casts
            assert casts['as_str_uppercase']['prompt'] == 'Convert to uppercase'
        
        def it_provides_access_to_transformation_values():
            """Provides access to transformation values through field proxy."""
            
            form = (chatfield()
                .field('value')
                    .desc('Enter a value')
                    .as_int()
                    .as_int('neg1', 'This is always -1')
                    .as_int('doubled', 'Double the integer value')
                    .as_int('squared', 'Square the integer value')
                    .as_bool('even', 'True if the integer is even')
                    .as_lang('fr', 'French translation')
                    .as_str('uppercase', 'Convert to uppercase')
                .build())
            
            # Simulate LLM having provided the value with transformations
            form._chatfield['fields']['value']['value'] = {
                'value': 'six',
                'as_int': 6,
                'as_int_neg1': -1,
                'as_int_doubled': 12,
                'as_int_squared': 36,
                'as_bool_even': True,
                'as_lang_fr': 'six',
                'as_str_uppercase': 'SIX',
                'context': 'User said six',
                'as_quote': 'six'
            }
            
            # Access the values through properties (using Python's FieldProxy behavior)
            assert form.value == 'six'
            # FieldProxy provides access to transformations
            assert form.value.as_int == 6
            assert form.value.as_int_neg1 == -1
            assert form.value.as_int_doubled == 12
            assert form.value.as_int_squared == 36
            assert form.value.as_bool_even == True
            assert form.value.as_lang_fr == 'six'
            assert form.value.as_str_uppercase == 'SIX'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])