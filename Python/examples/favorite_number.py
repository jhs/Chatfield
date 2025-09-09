#!/usr/bin/env python3
"""
Favorite Number Example
=======================

This example demonstrates the extensive transformation system:
- Basic transformations (@as_int, @as_float, @as_bool)
- Language transformations (@as_lang.fr, @as_lang.th, etc.)
- Set and list transformations (@as_set, @as_list)
- Cardinality decorators (@as_one, @as_maybe, @as_multi, @as_any)
- Complex sub-attribute transformations

Run with:
    python examples/favorite_number.py

For automated demo:
    python examples/favorite_number.py --auto
"""

import os
import sys
import argparse
from pathlib import Path
import dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from chatfield import chatfield
from chatfield import Interviewer
from chatfield import alice, bob, must, hint
from chatfield import as_int, as_float, as_bool, as_str, as_set, as_percent
from chatfield import as_lang
from chatfield import as_one, as_maybe, as_multi, as_any


def create_number_interview():
    """Create an interview about favorite numbers with many transformations."""
    return (chatfield()
        .type("NumberInterview")
        .desc("Let's explore your relationship with numbers")
        
        .alice()
            .type("Mathematician")
            .trait("Enthusiastic about number properties")
        
        .bob()
            .type("Number Enthusiast")
        
        .field("favorite")
            .desc("What is your favorite number?")
            .must("a number between 1 and 100")
            .hint("Think about a number that has special meaning to you")
            
            # Basic transformations
            .as_int()
            .as_float("The number as a floating point value")
            .as_percent("The number as a percentage of 100")
            
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
            
            # String transformation
            .as_str('longhand', "Written out in English words")
            
            # Set transformation
            .as_set('factors', "All factors of the number")
            
            # Cardinality decorators for properties
            .as_one('size_category', "tiny (1-10)", "small (11-25)", "medium (26-50)", "large (51-75)", "huge (76-100)")
            .as_maybe('special_property', "fibonacci", "perfect number", "triangular number")
            .as_multi('math_properties', "even", "odd", "prime", "composite", "square", "cubic")
            .as_any('cultural_significance', "lucky", "unlucky", "sacred", "mystical")
        
        .field("reason")
            .desc("Why is this your favorite number?")
            .hint("Share what makes this number special to you")
        
        .field("least_favorite")
            .desc("What number do you like the least? (1-100)")
            .must("a number between 1 and 100")
            .as_int()
            .as_str('longhand', "Written out in English words")
            .as_bool('unlucky', "True if commonly considered unlucky")
        
        .build())


def run_interactive(interview):
    """Run the interview interactively."""
    thread_id = f"numbers-{os.getpid()}"
    print(f'Starting number interview (thread: {thread_id})')
    print("=" * 60)
    
    interviewer = Interviewer(interview, thread_id=thread_id)
    
    user_input = None
    while not interview._done:
        message = interviewer.go(user_input)
        
        if message:
            print(f"\nMathematician: {message}")
        
        if not interview._done:
            try:
                user_input = input("\nYou: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n[Interview ended]")
                break
    
    return interview._done


def run_automated(interview):
    """Run with prefab inputs for demonstration."""
    prefab_inputs = [
        "My favorite number is 42",
        "It's the answer to life, the universe, and everything according to Douglas Adams!",
        "I really don't like 13, it feels unlucky"
    ]
    
    thread_id = f"numbers-demo-{os.getpid()}"
    print(f'Running automated demo (thread: {thread_id})')
    print("=" * 60)
    
    interviewer = Interviewer(interview, thread_id=thread_id)
    
    input_iter = iter(prefab_inputs)
    user_input = None
    
    while not interview._done:
        message = interviewer.go(user_input)
        
        if message:
            print(f"\nMathematician: {message}")
        
        if not interview._done:
            try:
                user_input = next(input_iter)
                print(f"\nYou: {user_input}")
            except StopIteration:
                print("\n[Demo inputs exhausted]")
                break
    
    return interview._done


def display_results(interview):
    """Display the collected number information with transformations."""
    print("\n" + "=" * 60)
    print("NUMBER ANALYSIS")
    print("-" * 60)
    print(interview._pretty())
    print("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Favorite Number Example')
    parser.add_argument('--auto', action='store_true',
                        help='Run with automated demo inputs')
    args = parser.parse_args()
    
    # Load environment variables
    dotenv.load_dotenv(override=True)
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY not found in environment")
        print("Please set your OpenAI API key in .env file")
        sys.exit(1)
    
    # Create and run the interview
    interview = create_number_interview()
    
    if args.auto:
        completed = run_automated(interview)
    else:
        completed = run_interactive(interview)
    
    # Display results if completed
    if completed:
        display_results(interview)
    else:
        print("\n[Interview not completed]")


if __name__ == "__main__":
    main()