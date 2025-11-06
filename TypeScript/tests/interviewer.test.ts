/**
 * Tests for the Interviewer class.
 * Mirrors Python's test_interviewer.py with identical test descriptions.
 */

import { chatfield } from '../chatfield/builder'
import { Interviewer } from '../chatfield/interviewer'
import { Interview } from '../chatfield/interview'

// Mock the LLM backend for testing
class MockLLMBackend {
  temperature: number = 0.0
  modelName: string = 'openai:gpt-4o'
  tools: any[] = []
  boundTools: any[] = []
  
  bind(args: any) {
    // Support bind method for LangChain compatibility
    if (args.tools) {
      this.boundTools = args.tools
    }
    return this
  }
  
  bindTools(tools: any[]) {
    this.tools = tools
    this.boundTools = tools
    return this
  }
  
  async invoke(messages: any[]) {
    return { content: 'Mock response' }
  }
  
  withStructuredOutput(schema: any) {
    return this
  }
}

describe('Interviewer', () => {
  describe('initialization', () => {
    it('creates with interview instance', () => {
      const mockLlm = new MockLLMBackend()
      const interview = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .field('email').desc('Your email')
        .build()
      const interviewer = new Interviewer(interview, { llm: mockLlm })
      
      expect(interviewer.interview).toBe(interview)
      expect(interviewer.config.configurable.thread_id).toBeDefined()
      expect(interviewer.checkpointer).toBeDefined()
      expect(interviewer.graph).toBeDefined()
    })
    
    it('generates unique thread id', () => {
      const mockLlm = new MockLLMBackend()
      const interview = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()
      const interviewer = new Interviewer(interview, { threadId: 'custom-123', llm: mockLlm })
      
      expect(interviewer.config.configurable.thread_id).toBe('custom-123')
    })
    
    it('configures llm model', () => {
      const mockLlm = new MockLLMBackend()
      const interview = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()
      const interviewer = new Interviewer(interview, { llm: mockLlm })
      
      // Should use the provided mock LLM
      expect(interviewer.llm).toBeDefined()
      expect(interviewer.llm).toBe(mockLlm)
    })

    it('accepts api key from options', () => {
      const interview = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()

      // Should not throw when API key is provided in options
      expect(() => {
        new Interviewer(interview, {
          apiKey: 'test-api-key',
          baseUrl: 'https://my-proxy.com'
        })
      }).not.toThrow()
    })


    it('configures custom base url', () => {
      const interview = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()

      const interviewer = new Interviewer(interview, {
        apiKey: 'test-key',
        baseUrl: 'https://my-custom-proxy.com/v1'
      })

      expect(interviewer.llm).toBeDefined()
    })

    it('uses default base url when not specified', () => {
      const interview = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()

      const interviewer = new Interviewer(interview, {
        apiKey: 'test-key'
      })

      expect(interviewer.llm).toBeDefined()
    })
  })

  describe('endpoint security', () => {
    it('defaults to disabled mode in server environment', () => {
      const interview = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()

      // Ensure we're in Node environment (no window)
      expect(typeof window).toBe('undefined')

      // Should not throw with official endpoint in disabled mode (default)
      expect(() => {
        new Interviewer(interview, {
          apiKey: 'test-key',
          baseUrl: 'https://api.openai.com/v1'
        })
      }).not.toThrow()
    })

    it('defaults to strict mode in browser environment', () => {
      // Isomorphic: Python runs server-side only and has no browser/Node.js
      // environment distinction. TypeScript tests browser environment detection
      // by mocking window object. This test documents the difference with no-op
      // behavior that passes to maintain identical test counts across languages.
      const interview = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()

      // Mock browser environment
      const originalWindow = global.window;
      (global as any).window = {}

      try {
        // Should throw with official endpoint in strict mode (browser default)
        expect(() => {
          new Interviewer(interview, {
            apiKey: 'test-key',
            baseUrl: 'https://api.openai.com/v1'
          })
        }).toThrow('SECURITY ERROR')
      } finally {
        // Restore original window
        if (originalWindow !== undefined) {
          global.window = originalWindow
        } else {
          delete (global as any).window
        }
      }
    })

    it('throws error in strict mode for dangerous endpoint', () => {
      const interview = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()

      // Should throw with official endpoint in strict mode
      expect(() => {
        new Interviewer(interview, {
          apiKey: 'test-key',
          baseUrl: 'https://api.openai.com/v1',
          endpointSecurity: 'strict'
        })
      }).toThrow('SECURITY ERROR')

      expect(() => {
        new Interviewer(interview, {
          apiKey: 'test-key',
          baseUrl: 'https://api.openai.com/v1',
          endpointSecurity: 'strict'
        })
      }).toThrow('api.openai.com')
    })

    it('warns in warn mode for dangerous endpoint', () => {
      const interview = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()

      // Capture console warnings
      const originalWarn = console.warn
      const warnings: string[] = []
      console.warn = (message: string) => {
        warnings.push(message)
      }

      try {
        // Should warn but not throw with official endpoint in warn mode
        const interviewer = new Interviewer(interview, {
          apiKey: 'test-key',
          baseUrl: 'https://api.openai.com/v1',
          endpointSecurity: 'warn'
        })

        // Verify warning was issued
        expect(warnings.length).toBeGreaterThan(0)
        expect(warnings.some(w => w.includes('WARNING'))).toBe(true)
        expect(warnings.some(w => w.includes('api.openai.com'))).toBe(true)
        expect(interviewer).toBeDefined()
      } finally {
        // Restore console.warn
        console.warn = originalWarn
      }
    })

    it('allows safe endpoints in all modes', () => {
      const interview = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()

      // Should work in all modes with safe endpoint
      const modes: Array<'disabled' | 'warn' | 'strict'> = ['disabled', 'warn', 'strict']
      for (const mode of modes) {
        const interviewer = new Interviewer(interview, {
          apiKey: 'test-key',
          baseUrl: 'https://my-proxy.com/v1',
          endpointSecurity: mode
        })
        expect(interviewer).toBeDefined()
      }
    })

    it('detects anthropic endpoint', () => {
      const interview = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()

      // Should throw with Anthropic endpoint in strict mode
      expect(() => {
        new Interviewer(interview, {
          apiKey: 'test-key',
          baseUrl: 'https://api.anthropic.com/v1',
          endpointSecurity: 'strict'
        })
      }).toThrow('SECURITY ERROR')

      expect(() => {
        new Interviewer(interview, {
          apiKey: 'test-key',
          baseUrl: 'https://api.anthropic.com/v1',
          endpointSecurity: 'strict'
        })
      }).toThrow('api.anthropic.com')
    })

    it('handles none base url safely', () => {
      const interview = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()

      // Should throw in strict mode with no base URL
      expect(() => {
        new Interviewer(interview, {
          apiKey: 'test-key',
          baseUrl: undefined,
          endpointSecurity: 'strict'
        })
      }).toThrow('No explicit endpoint configured')

      // Should work in disabled mode
      const i1 = new Interviewer(interview, {
        apiKey: 'test-key',
        baseUrl: undefined,
        endpointSecurity: 'disabled'
      })
      expect(i1).toBeDefined()

      // Should warn in warn mode
      const originalWarn = console.warn
      const warnings: string[] = []
      console.warn = (message: string) => {
        warnings.push(message)
      }

      try {
        const i2 = new Interviewer(interview, {
          apiKey: 'test-key',
          baseUrl: undefined,
          endpointSecurity: 'warn'
        })
        expect(i2).toBeDefined()
        expect(warnings.length).toBeGreaterThan(0)
      } finally {
        console.warn = originalWarn
      }
    })

    it('cannot disable security in browser', () => {
      // Isomorphic: Python runs server-side only and has no browser environment.
      // TypeScript tests that disabling security in a browser throws an error by
      // mocking window object. This test documents the difference with no-op
      // behavior that passes to maintain identical test counts across languages.
      const interview = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()

      // Mock browser environment
      const originalWindow = global.window;
      (global as any).window = {}

      try {
        // Should throw when trying to disable security in browser
        expect(() => {
          new Interviewer(interview, {
            apiKey: 'test-key',
            baseUrl: 'https://api.openai.com/v1',
            endpointSecurity: 'disabled'
          })
        }).toThrow('Cannot disable endpoint security')
      } finally {
        // Restore original window
        if (originalWindow !== undefined) {
          global.window = originalWindow
        } else {
          delete (global as any).window
        }
      }
    })

    it('handles relative base url safely', () => {
      const interview = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()

      // Should work in all modes with relative URL
      const i1 = new Interviewer(interview, {
        apiKey: 'test-key',
        baseUrl: '/v1',
        endpointSecurity: 'disabled'
      })
      expect(i1).toBeDefined()

      const i2 = new Interviewer(interview, {
        apiKey: 'test-key',
        baseUrl: '/v1',
        endpointSecurity: 'warn'
      })
      expect(i2).toBeDefined()

      const i3 = new Interviewer(interview, {
        apiKey: 'test-key',
        baseUrl: '/v1',
        endpointSecurity: 'strict'
      })
      expect(i3).toBeDefined()
    })
  })

  describe('system prompt', () => {
    it('generates basic prompt', () => {
      const mockLlm = new MockLLMBackend()
      const interview = chatfield()
        .type('SimpleInterview')
        .desc('Customer feedback form')
        .field('rating').desc('Overall satisfaction rating')
        .field('comments').desc('Additional comments')
        .build()
      const interviewer = new Interviewer(interview, { llm: mockLlm })
      
      const prompt = interviewer.mkSystemPrompt({ interview, messages: [], hasDigestedConfidentials: false, hasDigestedConcludes: false })

      expect(prompt).toContain('Customer feedback form')
      expect(prompt).toContain('rating: Overall satisfaction rating')
      expect(prompt).toContain('comments: Additional comments')
      expect(prompt).toContain('Agent')  // Default role
      expect(prompt).toContain('User')   // Default role
    })

    it('includes custom roles', () => {
      const mockLlm = new MockLLMBackend()
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
      const interviewer = new Interviewer(interview, { llm: mockLlm })

      const prompt = interviewer.mkSystemPrompt({ interview, messages: [], hasDigestedConfidentials: false, hasDigestedConcludes: false })

      expect(prompt).toContain('Customer Support Agent')
      expect(prompt).toContain('Frustrated Customer')
      expect(prompt).toContain('Friendly and helpful')
      expect(prompt).toContain('Had a bad experience')
    })

    it('includes validation rules', () => {
      const mockLlm = new MockLLMBackend()
      const interview = chatfield()
        .type('ValidatedInterview')
        .field('feedback')
          .desc('Your feedback')
          .must('specific details')
          .reject('profanity')
          .hint('Be constructive')
        .build()
      const interviewer = new Interviewer(interview, { llm: mockLlm })

      const prompt = interviewer.mkSystemPrompt({ interview, messages: [], hasDigestedConfidentials: false, hasDigestedConcludes: false })

      expect(prompt).toContain('Must: specific details')
      expect(prompt).toContain('Reject: profanity')
      // Note: Hints are included in specs but may not appear in system prompt
    })

    it('instructs about confidentiality', () => {
      const mockLlm = new MockLLMBackend()
      const interview = chatfield()
        .type('HistoryAndLiteratureExam')
        .desc('We are administering a history and literature exam. It will affect your final grade.')
        .alice()
          .type('Teacher administering the Exam')
        .bob()
          .type('Student taking the Exam')
        .field('q1_hitchhiker')
          .desc('Who wrote The Hitchhiker\'s Guide to the Galaxy?')
          .as_bool('correct', 'true if the answer is Douglas Adams, false otherwise')
        .build()
      const interviewer = new Interviewer(interview, { llm: mockLlm })

      const prompt = interviewer.mkSystemPrompt({ interview, messages: [], hasDigestedConfidentials: false, hasDigestedConcludes: false })

      expect(prompt).toContain('Key Confidential Information')
    })
  })

  describe('conversation flow', () => {
    it('routes to digest_concludes after digest_confidentials when _enough is true', () => {
      /**
       * This test demonstrates issue #71: the state machine fails to execute
       * digest_concludes after digest_confidentials completes, leaving conclude
       * fields as null and preventing the interview from reaching _done state.
       */
      const mockLlm = new MockLLMBackend()

      // Create interview with conclude fields
      const interview = chatfield()
        .type('TestForm')
        .field('name').desc('Your name')
        .field('summary').desc('Summary of conversation').conclude()
        .build()
      const interviewer = new Interviewer(interview, { llm: mockLlm })

      // Manually set _enough to true (simulating all master fields collected)
      if (interview._chatfield.fields.name) {
        interview._chatfield.fields.name.value = {
          value: 'John Doe',
          context: 'User provided name',
          as_quote: 'My name is John Doe'
        }
      }

      // Create state after digest_confidentials has completed
      // Import AIMessage for proper typing
      const { AIMessage } = require('@langchain/core/messages')
      const state = {
        messages: [new AIMessage('Confidentials digested')],
        interview: interview,
        hasDigestedConfidentials: true,  // Already digested
        hasDigestedConcludes: false      // Not yet digested
      }

      // Call routeFromDigest (this is called after digest_confidentials completes)
      // Use 'any' to access private method for testing purposes
      const route = (interviewer as any).routeFromDigest(state)

      // BUG: Should route to 'digest_concludes' but actually routes to 'think'
      // This is the core bug in issue #71
      expect(route).toBe('digest_concludes')
      // Error message for when this fails
      if (route !== 'digest_concludes') {
        throw new Error(
          `Expected route to 'digest_concludes' after digest_confidentials ` +
          `when _enough=true and hasDigestedConcludes=false, but got '${route}'. ` +
          `This causes conclude fields to remain null and prevents interview completion.`
        )
      }
    })

    it('updates field values', () => {
      const mockLlm = new MockLLMBackend()
      const interview = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()
      const interviewer = new Interviewer(interview, { llm: mockLlm })
      
      // Manually update field as if tool was called
      interviewer.processUpdateTool(interview, {
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
      const mockLlm = new MockLLMBackend()
      const interview = chatfield()
        .type('SimpleInterview')
        .field('field1').desc('Field 1')
        .field('field2').desc('Field 2')
        .build()
      const interviewer = new Interviewer(interview, { llm: mockLlm })
      
      // Initially not done
      expect(interview._done).toBe(false)
      
      // Set both fields
      interviewer.processUpdateTool(interview, {
        field1: { value: 'value1', context: 'N/A', as_quote: 'value1' }
      })
      interviewer.processUpdateTool(interview, {
        field2: { value: 'value2', context: 'N/A', as_quote: 'value2' }
      })
      
      // Should be done
      expect(interview._done).toBe(true)
    })
    
    it('handles transformations', () => {
      const mockLlm = new MockLLMBackend()
      const interview = chatfield()
        .type('TypedInterview')
        .field('number')
          .desc('A number')
          .as_int()
          .as_lang('fr')
        .build()
      const interviewer = new Interviewer(interview, { llm: mockLlm })
      
      // Process tool input with transformations
      interviewer.processUpdateTool(interview, {
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
      const mockLlm = new MockLLMBackend()
      const interview = chatfield()
        .type('EmptyInterview')
        .desc('Empty interview')
        .build()
      const interviewer = new Interviewer(interview, { llm: mockLlm })
      
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
      const mockLlm1 = new MockLLMBackend()
      const mockLlm2 = new MockLLMBackend()
      const interview1 = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()
      const interview2 = chatfield()
        .type('SimpleInterview')
        .field('name').desc('Your name')
        .build()
      
      const interviewer1 = new Interviewer(interview1, {threadId: 'thread-1', llm: mockLlm1})
      const interviewer2 = new Interviewer(interview2, {threadId: 'thread-2', llm: mockLlm2})
      
      expect(interviewer1.config.configurable.thread_id).toBe('thread-1')
      expect(interviewer2.config.configurable.thread_id).toBe('thread-2')
      expect(interviewer1.config).not.toBe(interviewer2.config)
    })
  })
})