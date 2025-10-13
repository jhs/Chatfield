"""Tests for complete conversation flows with prefab user messages."""

import os
import json
import pytest
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel

from chatfield import Interviewer, chatfield

class FauxModel(FakeMessagesListChatModel):
    """A faux model that always returns the same response."""
    def bind_tools(self, *args, **kwargs):
        return self

    @property
    def openai_api_base(self):
        return 'https://api.openai.com/v1'

def tool_call(tool_name, **kwargs):
    """Helper to create a tool call message."""
    return AIMessage(content='', additional_kwargs={
        'tool_calls': [
            {
                'id': 'call_id_goes_here',
                'function': {
                    'type': 'function',
                    'name': tool_name,
                    'arguments': json.dumps(kwargs),
                },
            }
        ],
    })

def describe_conversations():
    """Tests for full conversation flows."""
    
    # TODO: Add tests for as_context and as_quote decorators
    # These tests should verify that:
    # 1. Fields decorated with @as_context capture conversational context
    # 2. Fields decorated with @as_quote capture direct quotes from users
    # 3. Both decorators work together on the same field
    # 4. The LLM properly populates these casts in the tool calls
    # Example test cases:
    # - Test that as_context returns "N/A" when no context is relevant
    # - Test that as_quote preserves exact wording with proper formatting
    # - Test that multiple paragraphs, elipses, and [sic] are handled correctly
    
    def describe_restaurant_order():
        """Tests for restaurant order conversation flow."""
        
        def _create_restaurant_order():
            """Create restaurant order interview."""
            return (chatfield()
                .type("Restaurant Order")
                .desc("Taking your order for tonight")
                
                .alice()
                    .type("Server")
                    .trait("Friendly and attentive")
                
                .bob()
                    .type("Diner")
                    .trait("First-time visitor")
                    .trait.possible("Vegan", "needs vegan, plant-based, non animal product")
                
                .field("starter")
                    .desc("starter or appetizer")
                    .as_one('selection', "Sir Digby Chicken Caesar", "Shrimp cocktail", "Garden salad")
                
                .field("main_course")
                    .desc("Main course")
                    .hint("Choose from: Grilled salmon, Veggie pasta, Beef tenderloin, Chicken parmesan")
                    .as_one('selection', "Grilled salmon", "Veggie pasta", "Beef tenderloin", "Chicken parmesan")
                
                .field("dessert")
                    .desc("Mandatory dessert; choices: Cheesecake, Chocolate mousse, Fruit sorbet")
                    .as_one('selection', "Cheesecake", "Chocolate mousse", "Fruit sorbet")
                
                .build())
        
        def it_adapts_to_vegan_preferences():
            """Adapts conversation when vegan preference detected."""
            # User messages are strings, everything else is from the model.
            all_messages =[
                None,
                AIMessage(content='Welcome to the restaurant'),

                'I am vegan, so I need plant-based options only.',
                tool_call(
                    'update_Restaurant_Order',
                    starter={
                        'value': 'Garden salad',
                        'as_one_selection': 'Garden salad',
                    },
                    main_course={
                        'value': 'Veggie pasta',
                        'as_one_selection': 'Veggie pasta',
                    },
                    dessert={
                        'value': 'Fruit sorbet',
                        'as_one_selection': 'Fruit sorbet',
                    },
                ),
                AIMessage(content='OK I submitted your order for all vegan stuff'),
            ]

            # From the list above, the AI will return all langchain messages. The user will send either None or a string.
            prefab_inputs = [msg for msg in all_messages if not isinstance(msg, AIMessage)]
            llm_responses = [msg for msg in all_messages if     isinstance(msg, AIMessage)]

            llm = FauxModel(responses=llm_responses)

            order = _create_restaurant_order()
            interviewer = Interviewer(order, thread_id="test-vegan-order", llm=llm)
            
            # Process each input
            for user_input in prefab_inputs:
                ai_message = interviewer.go(user_input)
                if order._done:
                    break
                assert ai_message is not None
            
            # Verify the order was completed correctly
            assert order._done, "Order should be complete"
            assert order.starter == "Garden salad", f"Expected 'Garden salad', got {order.starter}"
            assert order.main_course == "Veggie pasta", f"Expected 'Veggie pasta', got {order.main_course}"
            assert order.dessert == "Fruit sorbet", f"Expected 'Fruit sorbet', got {order.dessert}"
            
            # Check that vegan trait was activated
            traits = order._chatfield['roles']['bob'].get('possible_traits', {})
            assert 'Vegan' in traits, "Vegan trait should be tracked"
            
            # TODO: Activating traits is not implemented yet, I don't think.
            # assert traits.get('Vegan', {}).get('active') == True, "Vegan trait should be active"
        
        def it_handles_regular_order():
            """Handles regular order without dietary restrictions."""
            # User messages are strings, everything else is from the model.
            all_messages = [
                None,
                AIMessage(content='Welcome to the restaurant! What can I get you started with?'),
                
                'The Sir Digby Chicken Caesar sounds good',
                AIMessage(content='Great choice! And for your main course?'),
                
                'I\'ll have the grilled salmon',
                AIMessage(content='Excellent! And what would you like for dessert?'),
                
                'Chocolate mousse for dessert',
                tool_call(
                    'update_Restaurant_Order',
                    starter={
                        'value': 'Sir Digby Chicken Caesar',
                        'as_one_selection': 'Sir Digby Chicken Caesar',
                    },
                    main_course={
                        'value': 'Grilled salmon',
                        'as_one_selection': 'Grilled salmon',
                    },
                    dessert={
                        'value': 'Chocolate mousse',
                        'as_one_selection': 'Chocolate mousse',
                    },
                ),
                AIMessage(content='Perfect! Your order is complete.'),
            ]
            
            # From the list above, the AI will return all langchain messages. The user will send either None or a string.
            prefab_inputs = [msg for msg in all_messages if not isinstance(msg, AIMessage)]
            llm_responses = [msg for msg in all_messages if isinstance(msg, AIMessage)]
            
            llm = FauxModel(responses=llm_responses)
            
            order = _create_restaurant_order()
            interviewer = Interviewer(order, thread_id="test-regular-order", llm=llm)
            
            # Process each input
            for user_input in prefab_inputs:
                ai_message = interviewer.go(user_input)
                if order._done:
                    break
                assert ai_message is not None
            
            # Verify completion
            assert order._done, "Order should be complete"
            assert order.starter == "Sir Digby Chicken Caesar", f"Expected 'Sir Digby Chicken Caesar', got {order.starter}"
            assert order.main_course == "Grilled salmon", f"Expected 'Grilled salmon', got {order.main_course}"
            assert order.dessert == "Chocolate mousse", f"Expected 'Chocolate mousse', got {order.dessert}"

    def describe_job_interview():
        """Tests for job interview conversation flow."""
        
        def _create_job_interview():
            """Create job interview."""
            return (chatfield()
                .type("JobInterview")
                .desc("Software Engineer position interview")
                
                .alice()
                    .type("Hiring Manager")
                
                .bob()
                    .type("Candidate")
                    .trait.possible("career-changer", "mentions different industry or transferable skills")
                
                .field("experience")
                    .desc("Tell me about your relevant experience")
                    .must("specific examples")
                
                .field("has_mentored")
                    .desc("Gives specific evidence of professionally mentoring junior colleagues")
                    .confidential()
                    .as_bool()
                
                .build())
        
        def it_detects_career_changer():
            """Detects career change from conversation."""
            interview = _create_job_interview()
            
            # User messages are strings, everything else is from the model.
            all_messages = [
                None,
                AIMessage(content='Hello! Let\'s start with your experience. Can you tell me about your relevant experience?'),
                
                "I spent 5 years in finance but taught myself programming. "
                "I built a trading algorithm in Python that automated our daily reports, "
                "saving the team 20 hours per week. I also created a dashboard using React.",
                AIMessage(content='That\'s great experience! Have you mentored any junior colleagues?'),
                
                "In my finance role, I regularly mentored junior analysts on Python programming "
                "and helped them understand data structures and algorithms.",
                tool_call(
                    'update_JobInterview',
                    experience={
                        'value': 'I spent 5 years in finance but taught myself programming. I built a trading algorithm in Python that automated our daily reports, saving the team 20 hours per week. I also created a dashboard using React.',
                    },
                    has_mentored={
                        'value': 'Yes, mentored junior analysts on Python programming',
                        'as_bool': True,
                    },
                ),
                AIMessage(content='Thank you for sharing your experience!'),
            ]
            
            # From the list above, the AI will return all langchain messages. The user will send either None or a string.
            prefab_inputs = [msg for msg in all_messages if not isinstance(msg, AIMessage)]
            llm_responses = [msg for msg in all_messages if isinstance(msg, AIMessage)]
            
            llm = FauxModel(responses=llm_responses)
            interviewer = Interviewer(interview, thread_id="test-career-change", llm=llm)
            
            # Process inputs
            for user_input in prefab_inputs:
                ai_message = interviewer.go(user_input)
                if interview._done:
                    break
                assert ai_message is not None
            
            # Verify data collection
            assert interview.experience is not None, "Experience should be collected"
            assert "finance" in interview.experience.lower(), "Should capture finance background"
            assert "python" in interview.experience.lower(), "Should capture Python experience"
            
            # Check confidential field
            assert interview.has_mentored is not None, "Mentoring should be detected"
            assert interview.has_mentored.as_bool == True, "Should detect mentoring activity"
            
            # Check career-changer trait
            traits = interview._chatfield['roles']['bob'].get('possible_traits', {})
            assert 'career-changer' in traits, "Career-changer trait should be tracked"
            # TODO: Trait activation not yet implemented
            # if 'career-changer' in traits:
            #     assert traits['career-changer'].get('active') == True, "Career changer trait should be active"
        
        def it_handles_technical_interview():
            """Handles standard technical interview flow."""
            interview = _create_job_interview()
            
            # User messages are strings, everything else is from the model.
            all_messages = [
                None,
                AIMessage(content='Welcome! Please tell me about your relevant experience.'),
                
                "I have 8 years of experience as a full-stack developer. "
                "Most recently, I led the redesign of our e-commerce platform, "
                "improving load times by 40% and increasing conversion rates.",
                AIMessage(content='Impressive! Have you mentored other developers?'),
                
                "I've been a tech lead for 3 years, mentoring a team of 5 developers "
                "through code reviews, pair programming, and weekly learning sessions.",
                tool_call(
                    'update_JobInterview',
                    experience={
                        'value': 'I have 8 years of experience as a full-stack developer. Most recently, I led the redesign of our e-commerce platform, improving load times by 40% and increasing conversion rates.',
                    },
                    has_mentored={
                        'value': 'Yes, been a tech lead mentoring 5 developers',
                        'as_bool': True,
                    },
                ),
                AIMessage(content='Thank you for your time!'),
            ]
            
            # From the list above, the AI will return all langchain messages. The user will send either None or a string.
            prefab_inputs = [msg for msg in all_messages if not isinstance(msg, AIMessage)]
            llm_responses = [msg for msg in all_messages if isinstance(msg, AIMessage)]
            
            llm = FauxModel(responses=llm_responses)
            interviewer = Interviewer(interview, thread_id="test-technical", llm=llm)
            
            # Process inputs
            for user_input in prefab_inputs:
                ai_message = interviewer.go(user_input)
                if interview._done:
                    break
                assert ai_message is not None
            
            # Verify experience was captured
            assert interview.experience is not None, "Experience should be collected"
            assert "e-commerce" in interview.experience or "platform" in interview.experience, "Should capture project details"
            
            # Check mentoring detection
            assert interview.has_mentored is not None, "Mentoring should be detected"
            assert interview.has_mentored.as_bool == True, "Should detect mentoring activity"

    def describe_number_conversation():
        """Tests for number conversation with transformations."""
        
        def _create_number_interview():
            """Create number interview with transformations."""
            return (chatfield()
                .type("FavoriteNumber")
                .desc("Let's talk about your favorite number")
                
                .alice()
                    .type("Mathematician")
                
                .bob()
                    .type("Number Enthusiast")
                
                .field("number")
                    .desc("Your favorite number between 1 and 100")
                    .must("a number between 1 and 100")
                    .as_int()
                    .as_bool('even', "True if even, False if odd")
                    .as_one('parity', "even", "odd")
                
                .build())
        
        def it_collects_number_with_transformations():
            """Collects number with proper transformations."""
            # User messages are strings, everything else is from the model.
            all_messages = [
                None,
                AIMessage(content='Hello! What is your favorite number between 1 and 100?'),
                
                "My favorite number is 42",
                tool_call(
                    'update_FavoriteNumber',
                    number={
                        'value': '42',
                        'as_int': 42,
                        'as_bool_even': True,
                        'as_one_parity': 'even',
                    },
                ),
                AIMessage(content='Great choice! 42 is a wonderful number.'),
            ]
            
            # From the list above, the AI will return all langchain messages. The user will send either None or a string.
            prefab_inputs = [msg for msg in all_messages if not isinstance(msg, AIMessage)]
            llm_responses = [msg for msg in all_messages if isinstance(msg, AIMessage)]
            
            llm = FauxModel(responses=llm_responses)
            
            interview = _create_number_interview()
            interviewer = Interviewer(interview, thread_id="test-number", llm=llm)
            
            # Process input
            for user_input in prefab_inputs:
                ai_message = interviewer.go(user_input)
                if interview._done:
                    break
                assert ai_message is not None
            
            # Verify number was collected with transformations
            assert interview._done, "Interview should be complete"
            assert interview.number == "42", f"Expected '42', got {interview.number}"
            assert interview.number.as_int == 42, f"Integer transformation should be 42, got {interview.number.as_int}"
            assert interview.number.as_bool_even == True, "42 should be detected as even"
            assert interview.number.as_one_parity == "even", "Parity should be 'even'"
        
        def it_handles_odd_number_transformations():
            """Handles odd number with transformations."""
            # User messages are strings, everything else is from the model.
            all_messages = [
                None,
                AIMessage(content='What is your favorite number between 1 and 100?'),
                
                "I like the number 17",
                tool_call(
                    'update_FavoriteNumber',
                    number={
                        'value': '17',
                        'as_int': 17,
                        'as_bool_even': False,
                        'as_one_parity': 'odd',
                    },
                ),
                AIMessage(content='17 is a great prime number!'),
            ]
            
            # From the list above, the AI will return all langchain messages. The user will send either None or a string.
            prefab_inputs = [msg for msg in all_messages if not isinstance(msg, AIMessage)]
            llm_responses = [msg for msg in all_messages if isinstance(msg, AIMessage)]
            
            llm = FauxModel(responses=llm_responses)
            
            interview = _create_number_interview()
            interviewer = Interviewer(interview, thread_id="test-odd-number", llm=llm)
            
            # Process input
            for user_input in prefab_inputs:
                ai_message = interviewer.go(user_input)
                if interview._done:
                    break
                assert ai_message is not None
            
            # Verify odd number transformations
            assert interview._done, "Interview should be complete"
            assert interview.number == "17", f"Expected '17', got {interview.number}"
            assert interview.number.as_int == 17, f"Integer transformation should be 17, got {interview.number.as_int}"
            assert interview.number.as_bool_even == False, "17 should be detected as odd"
            assert interview.number.as_one_parity == "odd", "Parity should be 'odd'"

    def describe_simple_conversations():
        """Tests for simple conversation patterns."""
        
        def it_collects_name_and_email():
            """Collects simple name and email fields."""
            # User messages are strings, everything else is from the model.
            all_messages = [
                None,
                AIMessage(content='Hello! Let me collect your contact information. What is your full name?'),
                
                "John Doe",
                AIMessage(content='Thank you, John. What is your email address?'),
                
                "john.doe@example.com",
                tool_call(
                    'update_ContactInfo',
                    name={
                        'value': 'John Doe',
                    },
                    email={
                        'value': 'john.doe@example.com',
                    },
                ),
                AIMessage(content='Thank you! I have your contact information.'),
            ]
            
            # From the list above, the AI will return all langchain messages. The user will send either None or a string.
            prefab_inputs = [msg for msg in all_messages if not isinstance(msg, AIMessage)]
            llm_responses = [msg for msg in all_messages if isinstance(msg, AIMessage)]
            
            llm = FauxModel(responses=llm_responses)
            
            interview = (chatfield()
                .type("ContactInfo")
                .desc("Collecting contact information")
                
                .field("name")
                    .desc("Your full name")
                
                .field("email")
                    .desc("Your email address")
                    .must("valid email format")
                
                .build())
            
            interviewer = Interviewer(interview, thread_id="test-contact", llm=llm)
            
            # Process inputs
            for user_input in prefab_inputs:
                ai_message = interviewer.go(user_input)
                if interview._done:
                    break
                assert ai_message is not None
            
            # Verify completion
            assert interview._done, "Interview should be complete"
            assert interview.name == "John Doe", f"Expected 'John Doe', got {interview.name}"
            assert interview.email == "john.doe@example.com", f"Expected 'john.doe@example.com', got {interview.email}"
        
        def it_collects_boolean_field():
            """Collects boolean preference field."""
            # User messages are strings, everything else is from the model.
            all_messages = [
                None,
                AIMessage(content='Let me learn about your preferences. Do you like coffee?'),
                
                "Yes, I love coffee!",
                tool_call(
                    'update_Preferences',
                    likes_coffee={
                        'value': 'Yes, I love coffee!',
                        'as_bool': True,
                    },
                ),
                AIMessage(content='Great! Coffee lovers unite!'),
            ]
            
            # From the list above, the AI will return all langchain messages. The user will send either None or a string.
            prefab_inputs = [msg for msg in all_messages if not isinstance(msg, AIMessage)]
            llm_responses = [msg for msg in all_messages if isinstance(msg, AIMessage)]
            
            llm = FauxModel(responses=llm_responses)
            
            interview = (chatfield()
                .type("Preferences")
                .desc("Learning about your preferences")
                
                .field("likes_coffee")
                    .desc("Do you like coffee?")
                    .as_bool()
                
                .build())
            
            interviewer = Interviewer(interview, thread_id="test-bool", llm=llm)
            
            # Process input
            for user_input in prefab_inputs:
                ai_message = interviewer.go(user_input)
                if interview._done:
                    break
                assert ai_message is not None
            
            # Verify boolean was collected
            assert interview._done, "Interview should be complete"
            assert interview.likes_coffee.as_bool == True, "Should detect positive response"