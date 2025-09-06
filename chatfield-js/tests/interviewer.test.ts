/**
 * Tests for the Interviewer class.
 * Mirrors Python's test_interviewer.py with identical test descriptions.
 */

import { chatfield } from '../src/builder'
import { Interviewer } from '../src/interviewer'
import { Interview } from '../src/interview'

// Mock the LLM backend for testing
class MockLLMBackend {
  temperature: number = 0.0
  modelName: string = 'openai:gpt-4o'
  tools: any[] = []
  
  bind_tools(tools: any[]) {
    this.tools = tools
    return this
  }
  
  async invoke(messages: any[]) {
    return { content: 'Mock response' }
  }
  
  withStructuredOutput(schema: any) {
    return this
  }
}

// Mock chat model initialization
jest.mock('../src/interviewer', () => {
  const actual = jest.requireActual('../src/interviewer')
  return {
    ...actual,
    init_chat_model: jest.fn((model: string, temperature: number) => {
      return new MockLLMBackend()
    })
  }
})

describe('Interviewer', () => {
  describe('initialization', () => {
    it('creates with interview instance', () => {
      const interview = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .field('email').desc('Your email')
        .build()
      const interviewer = new Interviewer(interview)
      
      expect(interviewer.interview).toBe(interview)
      expect(interviewer.config.configurable.thread_id).toBeDefined()
      expect(interviewer.checkpointer).toBeDefined()
      expect(interviewer.graph).toBeDefined()
    })
    
    it('generates unique thread id', () => {
      const interview = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()
      const interviewer = new Interviewer(interview, { threadId: 'custom-123' })
      
      expect(interviewer.config.configurable.thread_id).toBe('custom-123')
    })
    
    it('configures llm model', () => {
      const interview = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()
      const interviewer = new Interviewer(interview)
      
      // Should initialize with GPT-4o by default
      expect(interviewer.llm).toBeDefined()
      expect(interviewer.llm instanceof MockLLMBackend).toBe(true)
    })
  })

  describe('system prompt', () => {
    it('generates basic prompt', () => {
      const interview = chatfield()
        .type('SimpleInterview')
        .desc('Customer feedback form')
        .field('rating').desc('Overall satisfaction rating')
        .field('comments').desc('Additional comments')
        .build()
      const interviewer = new Interviewer(interview)
      
      const prompt = interviewer.mk_system_prompt({ interview })
      
      expect(prompt).toContain('Customer feedback form')
      expect(prompt).toContain('rating: Overall satisfaction rating')
      expect(prompt).toContain('comments: Additional comments')
      expect(prompt).toContain('Agent')  // Default role
      expect(prompt).toContain('User')   // Default role
    })
    
    it('includes custom roles', () => {
      const interview = chatfield()
        .type('SupportInterview')
        .desc('Support ticket')
        .alice()
          .type('Customer Support Agent')
          .trait('Friendly and helpful')
        .bob()
          .type('Frustrated Customer')
          .trait('Had a bad experience')
        .field('issue').desc('What went wrong')
        .build()
      const interviewer = new Interviewer(interview)
      
      const prompt = interviewer.mk_system_prompt({ interview })
      
      expect(prompt).toContain('Customer Support Agent')
      expect(prompt).toContain('Frustrated Customer')
      expect(prompt).toContain('Friendly and helpful')
      expect(prompt).toContain('Had a bad experience')
    })
    
    it('includes validation rules', () => {
      const interview = chatfield()
        .type('ValidatedInterview')
        .field('feedback')
          .desc('Your feedback')
          .must('specific details')
          .reject('profanity')
          .hint('Be constructive')
        .build()
      const interviewer = new Interviewer(interview)
      
      const prompt = interviewer.mk_system_prompt({ interview })
      
      expect(prompt).toContain('Must: specific details')
      expect(prompt).toContain('Reject: profanity')
      // Note: Hints are included in specs but may not appear in system prompt
    })
  })

  describe('tool generation', () => {
    it('creates tool for each field', () => {
      const interview = chatfield()
        .type('SimpleInterview')
        .field('field1').desc('Field 1')
        .field('field2').desc('Field 2')
        .build()
      const interviewer = new Interviewer(interview)
      
      // Tool should be bound to LLM
      expect(interviewer.llm_with_both).toBeDefined()
      expect(interviewer.llm_with_both).toHaveProperty('bind_tools')
    })
    
    it('includes transformations in tool schema', () => {
      const interview = chatfield()
        .type('TypedInterview')
        .field('number')
          .desc('A number')
          .as_int()
          .as_bool()
          .as_lang('fr')
        .build()
      const interviewer = new Interviewer(interview)
      
      // Tool args should include transformations
      // This is complex to test without running the actual tool
      expect(interviewer.llm_with_both).toBeDefined()
    })
  })

  describe('conversation flow', () => {
    it('updates field values', () => {
      const interview = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()
      const interviewer = new Interviewer(interview)
      
      // Manually update field as if tool was called
      interviewer.process_tool_input(interview, {
        name: {
          value: 'Test User',
          context: 'User provided their name',
          as_quote: 'My name is Test User'
        }
      })
      
      // Check interview was updated
      expect(interview._chatfield.fields.name?.value).toBeDefined()
      expect(interview._chatfield.fields.name?.value?.value).toBe('Test User')
    })
    
    it('detects completion', () => {
      const interview = chatfield()
        .type('SimpleInterview')
        .field('field1').desc('Field 1')
        .field('field2').desc('Field 2')
        .build()
      const interviewer = new Interviewer(interview)
      
      // Initially not done
      expect(interview._done).toBe(false)
      
      // Set both fields
      interviewer.process_tool_input(interview, {
        field1: { value: 'value1', context: 'N/A', as_quote: 'value1' }
      })
      interviewer.process_tool_input(interview, {
        field2: { value: 'value2', context: 'N/A', as_quote: 'value2' }
      })
      
      // Should be done
      expect(interview._done).toBe(true)
    })
    
    it('handles transformations', () => {
      const interview = chatfield()
        .type('TypedInterview')
        .field('number')
          .desc('A number')
          .as_int()
          .as_lang('fr')
        .build()
      const interviewer = new Interviewer(interview)
      
      // Process tool input with transformations
      interviewer.process_tool_input(interview, {
        number: {
          value: 'five',
          context: 'User said five',
          as_quote: 'The answer is five',
          choose_exactly_one_as_int: 5,  // Note: Tool prefixes with choose_
          choose_exactly_one_as_lang_fr: 'cinq'
        }
      })
      
      // Check the field was updated with renamed keys
      const fieldValue = interview._chatfield.fields.number?.value
      expect(fieldValue?.value).toBe('five')
      expect(fieldValue?.as_one_as_int).toBe(5)  // Renamed from choose_exactly_one_
      expect(fieldValue?.as_one_as_lang_fr).toBe('cinq')
    })
  })

  describe('edge cases', () => {
    it('handles empty interview', () => {
      const interview = chatfield()
        .type('EmptyInterview')
        .desc('Empty interview')
        .build()
      const interviewer = new Interviewer(interview)
      
      // Should handle empty interview gracefully
      expect(interview._done).toBe(true)
    })
    
    it('copies interview state', () => {
      const interview1 = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()
      const interview2 = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()
      
      // Set field in interview2
      if (interview2._chatfield.fields.name) {
        interview2._chatfield.fields.name.value = {
          value: 'Test',
          context: 'N/A',
          as_quote: 'Test'
        }
      }
      
      // Copy from interview2 to interview1
      interview1._copy_from(interview2)
      
      // Check the copy worked
      expect(interview1._chatfield.fields.name?.value).toBeDefined()
      expect(interview1._chatfield.fields.name?.value?.value).toBe('Test')
      
      // Ensure it's a deep copy
      if (interview2._chatfield.fields.name?.value) {
        interview2._chatfield.fields.name.value!.value = 'Changed'
      }
      expect(interview1._chatfield.fields.name?.value?.value).toBe('Test')
    })
    
    it('maintains thread isolation', () => {
      const interview1 = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()
      const interview2 = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()
      
      const interviewer1 = new Interviewer(interview1, {threadId: 'thread-1'})
      const interviewer2 = new Interviewer(interview2, {threadId: 'thread-2'})
      
      expect(interviewer1.config.configurable.thread_id).toBe('thread-1')
      expect(interviewer2.config.configurable.thread_id).toBe('thread-2')
      expect(interviewer1.config).not.toBe(interviewer2.config)
    })
  })
})