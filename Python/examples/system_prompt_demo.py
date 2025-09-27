#!/usr/bin/env python
"""
Demo script that creates a chatfield interview, generates the system prompt,
and prints it to stdout with colored debug visualization.
"""

from chatfield import chatfield
from chatfield.interviewer import Interviewer

# Define a simple chatfield object with a few fields
interview = (chatfield()
        .type("NumberInterview")
        .desc("Let's explore your relationship with numbers")
        
        .alice()
            .type("Mathematician")
            .trait("Enthusiastic about number properties")
        
        .bob()
            .type("Number Enthusiast")
            .trait('Bob trait goes here')
        
        .field("favorite")
            .desc("What is your favorite number?")
            .must("a number between 1 and 100")
            .reject("Obscure like 73 or 88")
            .reject("Too common like 7 or 10")
            .must("A whole number")
            .reject("Cliche like 42")
            .hint("Do not cite the validation rules unless asked or an invalid answer is given")
            
            # Basic transformations
            .as_int()
            .as_float("The number as a floating point value")
            .as_percent("The number as a real 0.0-1.0")
            
            # Language transformations
            .as_lang('fr', "French translation")
            .as_lang('de', "German translation")
            .as_lang('es', "Spanish translation")
            .as_lang('ja', "Japanese translation")
            .as_lang('th', "Thai translation")
            
            # Boolean transformations with sub-attributes
            .as_bool('even', "True if even, False if odd")
            .as_bool('prime', "True if prime number")
            .as_bool('perfect_square', "True if perfect square")
            .as_bool('power_of_two', "True if power of two")
            
            # # String transformation
            .as_str('longhand', "Written out in English words")
            
            # # Set transformation
            .as_set('factors', "All factors of the number not counting 1")
            
            # # Cardinality decorators for properties
            .as_one('size_category', "tiny (1-10)", "small (11-25)", "medium (26-50)", "large (51-75)", "huge (76-100)")
            .as_maybe('special_property', "fibonacci", "perfect number", "triangular number")
            .as_multi('math_properties', "even", "odd", "prime", "composite", "square", "cubic")
            .as_any('cultural_significance', "lucky", "unlucky", "sacred", "mystical")
        
        .field("reason")
            .desc("Why is this your favorite number?")
            .hint("Perhaps from a well-known reference or personal experience")
        
        .build())

# Create an interviewer instance
interviewer = Interviewer(interview)

# Create initial state to generate system prompt
initial_state = {
    'messages': [],
    'interview': interview
}

# Generate the system prompt
system_prompt = interviewer.mk_system_prompt(initial_state)
debug_view = Interviewer.debug_prompt(system_prompt)
print(debug_view)