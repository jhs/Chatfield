/**
 * Tests for complete conversation flows with prefab user messages.
 * Mirrors Python's test_conversations.py with identical test descriptions.
 */

import { describe, test, expect } from '@jest/globals';
import { AIMessage, HumanMessage, SystemMessage, ToolMessage } from '@langchain/core/messages';
import { chatfield } from '../src/builder';
import { Interviewer } from '../src/interviewer';

/**
 * Helper class that simulates LLM responses with tool calls.
 */
class FauxModel {
  responses: AIMessage[];
  tools: any[] = [];
  currentIndex = 0;
  
  constructor(responses: AIMessage[]) {
    this.responses = responses;
  }
  
  async invoke(messages: any[]): Promise<AIMessage> {
    if (this.currentIndex >= this.responses.length) {
      throw new Error('No more responses left in FauxModel');
    }
    const response = this.responses[this.currentIndex];
    if (!response) {
      throw new Error('FauxModel response is null or undefined');
    }

    this.currentIndex++;
    console.log(`Return response: ${response.content}`);
    return response
  }
  
  bindTools(tools: any[]) {
    // console.log('Bind tools:', tools);
    return this;
  }
  
  // withStructuredOutput(schema: any) {
  //   return this;
  // }
}

/**
 * Helper to create a tool call message.
 */
function toolCall(toolName: string, args: Record<string, any>) {
  return new AIMessage({
    content: '',
    additional_kwargs: {
      tool_calls: [
        {
          id: 'call_id_goes_here',
          type: 'function' as const,
          function: {
            name: toolName,
            arguments: JSON.stringify(args),
          },
        },
      ],
    },
  });
}

describe('Conversations', () => {
  describe('restaurant order', () => {
    const createRestaurantOrder = () => {
      return chatfield()
        .type('Restaurant Order')
        .desc('Taking your order for tonight')
        
        .alice()
          .type('Server')
          .trait('Friendly and attentive')
        
        .bob()
          .type('Diner')
          .trait('First-time visitor')
          .trait.possible('Vegan', 'needs vegan, plant-based, non animal product')
        
        .field('starter')
          .desc('starter or appetizer')
          .as_one('selection','Sir Digby Chicken Caesar', 'Shrimp cocktail', 'Garden salad')
        
        .field('main_course')
          .desc('Main course')
          .hint('Choose from: Grilled salmon, Veggie pasta, Beef tenderloin, Chicken parmesan')
          .as_one('selection','Grilled salmon', 'Veggie pasta', 'Beef tenderloin', 'Chicken parmesan')
        
        .field('dessert')
          .desc('Mandatory dessert; choices: Cheesecake, Chocolate mousse, Fruit sorbet')
          .as_one('selection','Cheesecake', 'Chocolate mousse', 'Fruit sorbet')
        
        .build();
    };
    
    test('adapts to vegan preferences', async () => {
      // User messages are strings, everything else is from the model.
      const allMessages = [
        null,
        new AIMessage('Welcome to the restaurant'),
        
        'I am vegan, so I need plant-based options only.',
        toolCall(
          'update_Restaurant_Order',
          {
            starter: {
              value: 'Garden salad',
              as_one_selection: 'Garden salad',
            },
            main_course: {
              value: 'Veggie pasta',
              as_one_selection: 'Veggie pasta',
            },
            dessert: {
              value: 'Fruit sorbet',
              as_one_selection: 'Fruit sorbet',
            },
          },
        ),
        new AIMessage('OK I submitted your order for all vegan stuff'),
      ];
      
      // From the list above, the AI will return all langchain messages. The user will send either None or a string.
      const prefabInputs = allMessages.filter(msg => !(msg instanceof AIMessage));
      const llmResponses = allMessages.filter(msg => msg instanceof AIMessage);
      
      const llm = new FauxModel(llmResponses);
      
      const order = createRestaurantOrder();
      const interviewer = new Interviewer(order, { threadId: 'test-vegan-order', llm: llm });
      
      // Process each input
      for (const userInput of prefabInputs) {
        const aiMessage = await interviewer.go(userInput as string | null);
        if (order._done) break;
        expect(aiMessage).toBeTruthy();
      }
      
      // Verify the order was completed correctly
      expect(order._done).toBe(true);
      expect(String(order.starter)).toBe('Garden salad');
      expect(String(order.main_course)).toBe('Veggie pasta');
      expect(String(order.dessert)).toBe('Fruit sorbet');
      
      // Check that vegan trait was activated
      const traits = order._chatfield.roles.bob.possible_traits || {};
      expect('Vegan' in traits).toBe(true);
      
      // TODO: Activating traits is not implemented yet
      // expect(traits.Vegan?.active).toBe(true);
    });
    
    test('handles regular order', async () => {
      // User messages are strings, everything else is from the model.
      const allMessages = [
        null,
        new AIMessage('Welcome to the restaurant! What is your regular order?'),
        
        'The Sir Digby Chicken Caesar sounds good',
        new AIMessage('Great choice! And for your main course?'),
        
        'I\'ll have the grilled salmon',
        new AIMessage('Excellent! And what would you like for dessert?'),
        
        'Chocolate mousse for dessert',
        toolCall(
          'update_Restaurant_Order',
          {
            starter: {
              value: 'Sir Digby Chicken Caesar',
              as_one_selection: 'Sir Digby Chicken Caesar',
            },
            main_course: {
              value: 'Grilled salmon',
              as_one_selection: 'Grilled salmon',
            },
            dessert: {
              value: 'Chocolate mousse',
              as_one_selection: 'Chocolate mousse',
            },
          },
        ),
        new AIMessage('Perfect! Your order is complete.'),
      ];
      
      // From the list above, the AI will return all langchain messages. The user will send either None or a string.
      const prefabInputs = allMessages.filter(msg => !(msg instanceof AIMessage));
      const llmResponses = allMessages.filter(msg => msg instanceof AIMessage);
      
      const llm = new FauxModel(llmResponses);
      
      const order = createRestaurantOrder();
      const interviewer = new Interviewer(order, { threadId: 'test-regular-order', llm: llm });
      
      // Process each input
      for (const userInput of prefabInputs) {
        const aiMessage = await interviewer.go(userInput as string | null);
        if (order._done) break;
        expect(aiMessage).toBeTruthy();
      }
      
      // Verify completion
      expect(order._done).toBe(true);
      expect(String(order.starter)).toBe('Sir Digby Chicken Caesar');
      expect(String(order.main_course)).toBe('Grilled salmon');
      expect(String(order.dessert)).toBe('Chocolate mousse');
    });
  });

  describe('job interview', () => {
    const createJobInterview = () => {
      return chatfield()
        .type('JobInterview')
        .desc('Software Engineer position interview')
        
        .alice()
          .type('Hiring Manager')
        
        .bob()
          .type('Candidate')
          .trait.possible('career-changer', 'mentions different industry or transferable skills')
        
        .field('experience')
          .desc('Tell me about your relevant experience')
          .must('specific examples')
        
        .field('has_mentored')
          .desc('Gives specific evidence of professionally mentoring junior colleagues')
          .confidential()
          .as_bool()
        
        .build();
    };
    
    test('detects career changer', async () => {
      // User messages are strings, everything else is from the model.
      const allMessages = [
        null,
        new AIMessage('Hello! Let\'s start with your experience. Can you tell me about your relevant experience?'),
        
        "I spent 5 years in finance but taught myself programming. " +
        "I built a trading algorithm in Python that automated our daily reports, " +
        "saving the team 20 hours per week. I also created a dashboard using React.",
        new AIMessage('That\'s great experience! Have you mentored any junior colleagues?'),
        
        "In my finance role, I regularly mentored junior analysts on Python programming " +
        "and helped them understand data structures and algorithms.",
        toolCall(
          'update_JobInterview',
          {
            experience: {
              value: 'I spent 5 years in finance but taught myself programming. I built a trading algorithm in Python that automated our daily reports, saving the team 20 hours per week. I also created a dashboard using React.',
            },
            has_mentored: {
              value: 'Yes, mentored junior analysts on Python programming',
              as_bool: true,
            },
          },
        ),
        new AIMessage('Thank you for sharing your experience!'),
      ];
      
      // From the list above, the AI will return all langchain messages. The user will send either None or a string.
      const prefabInputs = allMessages.filter(msg => !(msg instanceof AIMessage));
      const llmResponses = allMessages.filter(msg => msg instanceof AIMessage);
      
      const llm = new FauxModel(llmResponses);
      const interview = createJobInterview();
      const interviewer = new Interviewer(interview, { threadId: 'test-career-change', llm: llm });
      
      // Process inputs
      for (const userInput of prefabInputs) {
        const aiMessage = await interviewer.go(userInput as string | null);
        if (interview._done) break;
        expect(aiMessage).toBeTruthy();
      }
      
      // Verify data collection
      expect(interview.experience).toBeTruthy();
      expect(String(interview.experience).toLowerCase()).toContain('finance');
      expect(String(interview.experience).toLowerCase()).toContain('python');
      
      // Check confidential field
      expect(interview.has_mentored).toBeTruthy();
      expect(interview.has_mentored?.as_bool).toBe(true);
      
      // Check career-changer trait
      const traits = interview._chatfield.roles.bob.possible_traits || {};
      expect('career-changer' in traits).toBe(true);
      // TODO: Trait activation not yet implemented
      // if ('career-changer' in traits) {
      //   expect(traits['career-changer'].active).toBe(true);
      // }
    });
    
    test('handles technical interview', async () => {
      // User messages are strings, everything else is from the model.
      const allMessages = [
        null,
        new AIMessage('Welcome! Please tell me about your relevant experience.'),
        
        "I have 8 years of experience as a full-stack developer. " +
        "Most recently, I led the redesign of our e-commerce platform, " +
        "improving load times by 40% and increasing conversion rates.",
        new AIMessage('Impressive! Have you mentored other developers?'),
        
        "I've been a tech lead for 3 years, mentoring a team of 5 developers " +
        "through code reviews, pair programming, and weekly learning sessions.",
        toolCall(
          'update_JobInterview',
          {
            experience: {
              value: 'I have 8 years of experience as a full-stack developer. Most recently, I led the redesign of our e-commerce platform, improving load times by 40% and increasing conversion rates.',
            },
            has_mentored: {
              value: 'Yes, been a tech lead mentoring 5 developers',
              as_bool: true,
            },
          },
        ),
        new AIMessage('Thank you for your time!'),
      ];
      
      // From the list above, the AI will return all langchain messages. The user will send either None or a string.
      const prefabInputs = allMessages.filter(msg => !(msg instanceof AIMessage));
      const llmResponses = allMessages.filter(msg => msg instanceof AIMessage);
      
      const llm = new FauxModel(llmResponses);
      const interview = createJobInterview();
      const interviewer = new Interviewer(interview, { threadId: 'test-technical', llm: llm });
      
      // Process inputs
      for (const userInput of prefabInputs) {
        const aiMessage = await interviewer.go(userInput as string | null);
        if (interview._done) break;
        expect(aiMessage).toBeTruthy();
      }
      
      // Verify experience was captured
      expect(interview.experience).toBeTruthy();
      expect(
        String(interview.experience).includes('e-commerce') || 
        String(interview.experience).includes('platform')
      ).toBe(true);
      
      // Check mentoring detection
      expect(interview.has_mentored).toBeTruthy();
      expect(interview.has_mentored?.as_bool).toBe(true);
    });
  });

  describe('number conversation', () => {
    const createNumberInterview = () => {
      return chatfield()
        .type('FavoriteNumber')
        .desc("Let's talk about your favorite number")
        
        .alice()
          .type('Mathematician')
        
        .bob()
          .type('Number Enthusiast')
        
        .field('number')
          .desc('Your favorite number between 1 and 100')
          .must('a number between 1 and 100')
          .as_int()
          .as_bool('even', 'True if even, False if odd')
          .as_one('parity', 'even', 'odd')
        
        .build();
    };
    
    test('collects number with transformations', async () => {
      // User messages are strings, everything else is from the model.
      const allMessages = [
        null,
        new AIMessage('Hello! What is your favorite number between 1 and 100?'),
        
        'My favorite number is 42',
        toolCall(
          'update_FavoriteNumber',
          {
            number: {
              value: '42',
              as_int: 42,
              as_bool_even: true,
              as_one_parity: 'even',
            },
          },
        ),
        new AIMessage('Great choice! 42 is a wonderful number.'),
      ];
      
      // From the list above, the AI will return all langchain messages. The user will send either None or a string.
      const prefabInputs = allMessages.filter(msg => !(msg instanceof AIMessage));
      const llmResponses = allMessages.filter(msg => msg instanceof AIMessage);
      
      const llm = new FauxModel(llmResponses);
      
      const interview = createNumberInterview();
      const interviewer = new Interviewer(interview, { threadId: 'test-number', llm: llm });
      
      // Process input
      for (const userInput of prefabInputs) {
        const aiMessage = await interviewer.go(userInput as string | null);
        if (interview._done) break;
        expect(aiMessage).toBeTruthy();
      }
      
      // Verify number was collected with transformations
      expect(interview._done).toBe(true);
      expect(String(interview.number)).toBe('42');
      expect(interview.number?.as_int).toBe(42);
      expect(interview.number?.as_bool_even).toBe(true);
      expect(interview.number?.as_one_parity).toBe('even');
    });
    
    test('handles odd number transformations', async () => {
      // User messages are strings, everything else is from the model.
      const allMessages = [
        null,
        new AIMessage('What is your favorite number between 1 and 100?'),
        
        'I like the number 17',
        toolCall(
          'update_FavoriteNumber',
          {
            number: {
              value: '17',
              as_int: 17,
              as_bool_even: false,
              as_one_parity: 'odd',
            },
          },
        ),
        new AIMessage('17 is a great prime number!'),
      ];
      
      // From the list above, the AI will return all langchain messages. The user will send either None or a string.
      const prefabInputs = allMessages.filter(msg => !(msg instanceof AIMessage));
      const llmResponses = allMessages.filter(msg => msg instanceof AIMessage);
      
      const llm = new FauxModel(llmResponses);
      
      const interview = createNumberInterview();
      const interviewer = new Interviewer(interview, { threadId: 'test-odd-number', llm: llm });
      
      // Process input
      for (const userInput of prefabInputs) {
        const aiMessage = await interviewer.go(userInput as string | null);
        if (interview._done) break;
        expect(aiMessage).toBeTruthy();
      }
      
      // Verify odd number transformations
      expect(interview._done).toBe(true);
      expect(String(interview.number)).toBe('17');
      expect(interview.number?.as_int).toBe(17);
      expect(interview.number?.as_bool_even).toBe(false);
      expect(interview.number?.as_one_parity).toBe('odd');
    });
  });

  describe('simple conversations', () => {
    test('collects name and email', async () => {
      // User messages are strings, everything else is from the model.
      const allMessages = [
        null,
        new AIMessage('Hello! Let me collect your contact information. What is your full name?'),
        
        'John Doe',
        new AIMessage('Thank you, John. What is your email address?'),
        
        'john.doe@example.com',
        toolCall(
          'update_ContactInfo',
          {
            name: {
              value: 'John Doe',
            },
            email: {
              value: 'john.doe@example.com',
            },
          },
        ),
        new AIMessage('Thank you! I have your contact information.'),
      ];
      
      // From the list above, the AI will return all langchain messages. The user will send either None or a string.
      const prefabInputs = allMessages.filter(msg => !(msg instanceof AIMessage));
      const llmResponses = allMessages.filter(msg => msg instanceof AIMessage);
      
      const llm = new FauxModel(llmResponses);
      
      const interview = chatfield()
        .type('ContactInfo')
        .desc('Collecting contact information')
        
        .field('name')
          .desc('Your full name')
        
        .field('email')
          .desc('Your email address')
          .must('valid email format')
        
        .build();
      
      const interviewer = new Interviewer(interview, { threadId: 'test-contact', llm: llm });
      
      // Process inputs
      for (const userInput of prefabInputs) {
        const aiMessage = await interviewer.go(userInput as string | null);
        if (interview._done) break;
        expect(aiMessage).toBeTruthy();
      }
      
      // Verify completion
      expect(interview._done).toBe(true);
      expect(String(interview.name)).toBe('John Doe');
      expect(String(interview.email)).toBe('john.doe@example.com');
    });
    
    test('collects boolean field', async () => {
      // User messages are strings, everything else is from the model.
      const allMessages = [
        null,
        new AIMessage('Let me learn about your preferences. Do you like coffee?'),
        
        'Yes, I love coffee!',
        toolCall(
          'update_Preferences',
          {
            likes_coffee: {
              value: 'Yes, I love coffee!',
              as_bool: true,
            },
          },
        ),
        new AIMessage('Great! Coffee lovers unite!'),
      ];
      
      // From the list above, the AI will return all langchain messages. The user will send either None or a string.
      const prefabInputs = allMessages.filter(msg => !(msg instanceof AIMessage));
      const llmResponses = allMessages.filter(msg => msg instanceof AIMessage);
      
      const llm = new FauxModel(llmResponses);
      
      const interview = chatfield()
        .type('Preferences')
        .desc('Learning about your preferences')
        
        .field('likes_coffee')
          .desc('Do you like coffee?')
          .as_bool()
        
        .build();
      
      const interviewer = new Interviewer(interview, { threadId: 'test-bool', llm: llm });
      
      // Process input
      for (const userInput of prefabInputs) {
        const aiMessage = await interviewer.go(userInput as string | null);
        if (interview._done) break;
        expect(aiMessage).toBeTruthy();
      }
      
      // Verify boolean was collected
      expect(interview._done).toBe(true);
      expect(interview.likes_coffee?.as_bool).toBe(true);
    });
  });
});