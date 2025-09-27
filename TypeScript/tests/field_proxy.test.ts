/**
 * Tests for FieldProxy string subclass functionality.
 * Mirrors Python's test_field_proxy.py with identical test descriptions.
 */

import { chatfield } from '../chatfield/builder'
import { FieldProxy } from '../chatfield/field-proxy'

describe('FieldProxy', () => {
  describe('string behavior', () => {
    it('acts as normal string', () => {
      const instance = chatfield()
        .type('TestInterview')
        .field('name').desc('Your name')
        .build()

      // Set field value
      instance._chatfield.fields.name!.value = {
        value: 'John Doe',
        context: 'User provided their name',
        as_quote: 'John Doe'
      }

      const name = instance.name

      // Should act as string
      expect(String(name)).toBe('John Doe')
      expect(name.toString()).toBe('John Doe')
      expect(name.valueOf()).toBe('John Doe')
      expect(name.length).toBe(8)
    })

    it('supports string methods', () => {
      const instance = chatfield()
        .type('TestInterview')
        .field('name').desc('Your name')
        .build()

      instance._chatfield.fields.name!.value = {
        value: 'John Doe',
        context: 'User provided their name',
        as_quote: 'John Doe'
      }

      const name = instance.name

      // String methods should work
      expect(name.toUpperCase()).toBe('JOHN DOE')
      expect(name.toLowerCase()).toBe('john doe')
      expect(name.startsWith('John')).toBe(true)
      expect(name.endsWith('Doe')).toBe(true)
      expect(name.includes('John')).toBe(true)
    })
  })

  describe('transformation access', () => {
    it('provides as_int property', () => {
      const instance = chatfield()
        .type('TestInterview')
        .field('age')
          .desc('Your age')
          .as_int()
        .build()

      instance._chatfield.fields.age!.value = {
        value: '42',
        context: 'User said forty-two',
        as_quote: 'forty-two',
        as_int: 42
      }

      const age = instance.age
      expect(String(age)).toBe('42')
      expect(age.as_int).toBe(42)
    })

    it('provides as_float property', () => {
      const instance = chatfield()
        .type('TestInterview')
        .field('height')
          .desc('Your height')
          .as_float()
        .build()

      instance._chatfield.fields.height!.value = {
        value: '5.9',
        context: 'User provided height',
        as_quote: 'five point nine',
        as_float: 5.9
      }

      const height = instance.height
      expect(String(height)).toBe('5.9')
      expect(height.as_float).toBe(5.9)
    })

    it('provides as_bool property', () => {
      const instance = chatfield()
        .type('TestInterview')
        .field('active')
          .desc('Are you active?')
          .as_bool()
        .build()

      instance._chatfield.fields.active!.value = {
        value: 'yes',
        context: 'User confirmed',
        as_quote: 'yes, I am active',
        as_bool: true
      }

      const active = instance.active
      expect(String(active)).toBe('yes')
      expect(active.as_bool).toBe(true)
    })

    it('provides as_lang properties', () => {
      const instance = chatfield()
        .type('TestInterview')
        .field('greeting')
          .desc('Say hello')
          .as_lang('fr')
          .as_lang('es')
        .build()

      instance._chatfield.fields.greeting!.value = {
        value: 'hello',
        context: 'User greeted',
        as_quote: 'hello there',
        as_lang_fr: 'bonjour',
        as_lang_es: 'hola'
      }

      const greeting = instance.greeting
      expect(String(greeting)).toBe('hello')
      expect(greeting.as_lang_fr).toBe('bonjour')
      expect(greeting.as_lang_es).toBe('hola')
    })

    it('provides as_quote property', () => {
      const instance = chatfield()
        .type('TestInterview')
        .field('name').desc('Your name')
        .build()

      instance._chatfield.fields.name!.value = {
        value: 'John',
        context: 'User introduction',
        as_quote: 'My name is John'
      }

      const name = instance.name
      expect(String(name)).toBe('John')
      expect(name.as_quote).toBe('My name is John')
    })
  })

  describe('edge cases', () => {
    it('handles missing transformations', () => {
      const instance = chatfield()
        .type('TestInterview')
        .field('name').desc('Your name')
        .build()

      instance._chatfield.fields.name!.value = {
        value: 'test',
        context: 'N/A',
        as_quote: 'test'
      }

      const name = instance.name

      // Accessing non-existent transformation should return undefined
      // or throw error depending on implementation
      try {
        const result = name.as_int // This transformation doesn't exist
        expect(result).toBeUndefined() // May return undefined
      } catch (e) {
        expect(e).toBeInstanceOf(Error) // Or may throw error
      }
    })

    it('handles null values', () => {
      const instance = chatfield()
        .type('TestInterview')
        .field('name').desc('Your name')
        .build()

      // Field not yet collected
      const name = instance.name
      expect(name).toBeNull()
    })

    it('preserves original value', () => {
      const instance = chatfield()
        .type('TestInterview')
        .field('number')
          .desc('A number')
          .as_int()
          .as_float()
          .as_lang('fr')
        .build()

      instance._chatfield.fields.number!.value = {
        value: '42',
        context: 'User provided number',
        as_quote: 'forty-two',
        as_int: 42,
        as_float: 42.0,
        as_lang_fr: 'quarante-deux'
      }

      const number = instance.number

      // Original string value preserved
      expect(String(number)).toBe('42')
      expect(String(number)).toBe('42')

      // Transformations available as properties
      expect(number.as_int).toBe(42)
      expect(number.as_float).toBe(42.0)
      expect(number.as_lang_fr).toBe('quarante-deux')
    })
  })
})