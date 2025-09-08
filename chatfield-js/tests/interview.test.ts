/**
 * Tests for the Interview base class equivalent functionality.
 * Mirrors Python's test_interview.py with identical test descriptions.
 */

import { chatfield } from '../src/builder'
import { Interview } from '../src/interview'
import { FieldProxy } from '../src/field-proxy'

describe('Interview', () => {
  describe('field discovery', () => {
    it('uses field name when no description', () => {
      const interview = chatfield()
        .type('TestInterview')
        .field('test_field') // No description
        .build()

      // Should use field name as description
      expect(interview._chatfield.fields.test_field.desc).toBe('test_field')
    })
  })

  describe('field access', () => {
    it('returns none for uncollected fields', () => {
      const interview = chatfield()
        .type('TestInterview')
        .field('name').desc('Your name')
        .field('age').desc('Your age')
        .build()

      expect(interview.name).toBeNull()
      expect(interview.age).toBeNull()
    })
  })

  describe('completion state', () => {
    it('starts with done as false', () => {
      const interview = chatfield()
        .type('TestInterview')
        .field('field1').desc('Field 1')
        .field('field2').desc('Field 2')
        .build()

      expect(interview._done).toBe(false)
    })

    it('becomes done when all fields collected', () => {
      const interview = chatfield()
        .type('TestInterview')
        .field('field1').desc('Field 1')
        .field('field2').desc('Field 2')
        .build()

      // Initially not done
      expect(interview._done).toBe(false)

      // Set one field - still not done
      interview._chatfield.fields.field1!.value = {
        value: 'test1'
      }
      expect(interview._done).toBe(false)

      // Set both fields - now done
      interview._chatfield.fields.field2!.value = {
        value: 'test2'
      }
      expect(interview._done).toBe(true)
    })

    it('marks empty interview as done', () => {
      const empty = chatfield().build()
      expect(empty._done).toBe(true)
    })
  })

  describe('enough state', () => {
    it('starts with enough as false when normal fields exist', () => {
      const interview = chatfield()
        .type('TestInterview')
        .field('field1').desc('Normal field 1')
        .field('field2').desc('Normal field 2')
        .build()
      
      expect(interview._enough).toBe(false)
    })

    it('becomes enough when normal fields collected', () => {
      const interview = chatfield()
        .type('TestInterview')
        .field('normal1').desc('Normal field 1')
        .field('normal2').desc('Normal field 2')
        .field('secret').desc('Secret info').confidential()
        .field('rating').desc('Final rating').conclude()
        .build()
      
      // Initially not enough
      expect(interview._enough).toBe(false)
      expect(interview._done).toBe(false)
      
      // Set one normal field - still not enough
      interview._chatfield.fields.normal1!.value = {
        value: 'test1'
      }
      expect(interview._enough).toBe(false)
      expect(interview._done).toBe(false)
      
      // Set both normal fields - now enough (but not done)
      interview._chatfield.fields.normal2!.value = {
        value: 'test2'
      }
      expect(interview._enough).toBe(true)
      expect(interview._done).toBe(false) // Still have confidential/conclude fields
      
      // Set confidential field - still enough, still not done
      interview._chatfield.fields.secret!.value = {
        value: 'secret info'
      }
      expect(interview._enough).toBe(true)
      expect(interview._done).toBe(false)
      
      // Set conclude field - now done
      interview._chatfield.fields.rating!.value = {
        value: '5 stars'
      }
      expect(interview._enough).toBe(true)
      expect(interview._done).toBe(true)
    })

    it('is enough with only confidential fields', () => {
      const interview = chatfield()
        .type('TestInterview')
        .field('secret1').desc('Secret 1').confidential()
        .field('secret2').desc('Secret 2').confidential()
        .build()
      
      // With only confidential fields, _enough is True
      expect(interview._enough).toBe(true)
      expect(interview._done).toBe(false)
    })

    it('is enough with only conclude fields', () => {
      const interview = chatfield()
        .type('TestInterview')
        .field('rating1').desc('Rating 1').conclude()
        .field('rating2').desc('Rating 2').conclude()
        .build()
      
      // With only conclude fields, _enough is True
      expect(interview._enough).toBe(true)
      expect(interview._done).toBe(false)
    })

    it('marks empty interview as enough', () => {
      const empty = chatfield().build()
      expect(empty._enough).toBe(true)
      expect(empty._done).toBe(true)
    })
  })

  describe('serialization', () => {
    it('serializes to dict with model_dump', () => {
      const interview = chatfield()
        .type('TestInterview')
        .field('name').desc('Your name')
        .build()
      const dump = interview.model_dump()

      expect(typeof dump).toBe('object')
      expect(dump.type).toBe('TestInterview')
      expect('fields' in dump).toBe(true)
      expect('name' in dump.fields).toBe(true)
    })

    it('creates independent copy on dump', () => {
      const interview = chatfield()
        .type('TestInterview')
        .field('name').desc('Your name')
        .build()
      const dump = interview.model_dump()

      // Modify original and ensure dump is independent
      interview._chatfield.fields.name.value = { value: 'test' }
      expect(dump.fields.name.value).toBeNull() // Should still be null
    })
  })

  describe('display methods', () => {
    it('formats with pretty method', () => {
      const interview = chatfield()
        .type('TestInterview')
        .field('name').desc('Your name')
        .field('age').desc('Your age')
        .build()

      // Set one field
      interview._chatfield.fields.name.value = {
        value: 'Alice',
        context: 'User provided name',
        as_quote: 'My name is Alice'
      }

      const pretty = interview._pretty()

      expect(typeof pretty).toBe('string')
      expect(pretty.length).toBeGreaterThan(0)
      // Should show field values in pretty format
      expect(pretty.includes('TestInterview') || pretty.includes('name') || pretty.includes('Alice')).toBe(true)
    })
  })
})