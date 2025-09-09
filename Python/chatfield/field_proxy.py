"""
FieldProxy - A string-like object with transformation properties

This provides similar ergonomics to TypeScript's FieldProxy by subclassing
Python's str type, allowing natural string operations while also
providing transformation access via properties.
"""

from typing import Dict, Any


class FieldProxy(str):
    """Proxy object that provides transformation attribute access to field values.
    
    This proxy allows field values to:
    1. Behave as a normal string with all string methods
    2. Access boolean evaluations via as_bool.* attributes (e.g., field.as_bool_is_personal)
    3. Access type transformations via as_* attributes (e.g., field.as_int)
    
    Example:
        field = FieldProxy("100 dollars", chatfield)
        field == "100 dollars"  # Direct string comparison
        field.upper() == "100 DOLLARS"  # String methods work
        field.as_bool_is_large == True  # Boolean evaluation
        field.as_int == 100  # Type transformation
    """
    
    def __new__(cls, value: str, chatfield: Dict[str, Any]):
        """Create a new string-based proxy instance.
        
        Args:
            value: The actual string value of the field
            chatfield: Metadata about the field including transformations
        """
        # Create the string instance with the value
        instance = str.__new__(cls, value)
        return instance
    
    def __init__(self, value: str, chatfield: Dict[str, Any]):
        """Initialize the field value proxy metadata.
        
        Note: The string value is already set in __new__, this just stores metadata.
        
        Args:
            value: The actual string value of the field (for compatibility)
            chatfield: Metadata about the field including transformations
        """
        # Don't call str.__init__ as it doesn't take arguments
        # Store metadata for the proxy functionality
        self._chatfield = chatfield
    
    def _pretty(self) -> str:
        """Return a pretty-printed representation of transformations."""
        lines = []
        llm_value = self._chatfield.get('value')
        if llm_value and isinstance(llm_value, dict):
            for key, val in llm_value.items():
                if key != 'value':
                    lines.append(f'    {key:<25}: {val!r}')
        return '\n'.join(lines)
    
    def __getattr__(self, attr_name: str):
        """Provide access to type transformations and boolean evaluations.
        
        Args:
            attr_name: The name of the transformation (e.g., 'as_int', 'as_bool_is_personal')
            
        Returns:
            The evaluation/transformation result, or None if not evaluated
            
        Raises:
            AttributeError: If the attribute doesn't exist
        """
        llm_value = self._chatfield.get('value')
        if not llm_value or not isinstance(llm_value, dict):
            raise AttributeError(f"Field {attr_name} has no value set. Cannot access attributes.")

        if attr_name in llm_value:
            # Return the transformation or evaluation result
            cast_value = llm_value[attr_name]
            return cast_value

        raise AttributeError(f"Field {attr_name} has no value set")


def create_field_proxy(value: str, metadata: Dict[str, Any]) -> FieldProxy:
    """Create a FieldProxy that acts like a string but has transformation properties.
    
    This factory function mirrors the TypeScript implementation for consistency,
    even though Python could directly instantiate the class.
    
    Args:
        value: The string value
        metadata: Field metadata including transformations
        
    Returns:
        A FieldProxy instance
    """
    return FieldProxy(value, metadata)


