/**
 * Test custom transformations demonstrating feature parity.
 * This test file shows how TypeScript supports dynamic custom transformations.
 * Mirrors Python's test_custom_transformations.py with identical test descriptions.
 */

import { chatfield } from '../src/builder'

describe('CustomTransformations', () => {
  describe('multiple transformations', () => {
    it('applies multiple custom transformations', () => {
      // Test multiple custom transformations on the same field
      const form = chatfield()
        .field('value')
          .desc('Enter a value')
          .as_int()  // Base transformation
          .as_int('neg1', 'This is always -1')
          .as_int('doubled', 'Double the integer value')
          .as_int('squared', 'Square the integer value')
          .as_bool('even', 'True if the integer is even')
          .as_lang('fr', 'French translation')
          .as_str('uppercase', 'Convert to uppercase')
        .build()

      // Check that all custom transformations were created
      const fields = form._chatfield.fields
      expect(fields['value']).toBeDefined()
      
      const casts = fields['value']?.casts
      if (!casts) throw new Error('Casts not defined')
      
      // Check base transformations
      expect(casts['as_int']).toBeDefined()
      
      // Check integer custom transformations
      expect(casts['as_int_neg1']).toBeDefined()
      expect(casts['as_int_neg1'].prompt).toBe('This is always -1')
      
      expect(casts['as_int_doubled']).toBeDefined()
      expect(casts['as_int_doubled'].prompt).toBe('Double the integer value')
      
      expect(casts['as_int_squared']).toBeDefined()
      expect(casts['as_int_squared'].prompt).toBe('Square the integer value')
      
      // Check boolean custom transformation
      expect(casts['as_bool_even']).toBeDefined()
      expect(casts['as_bool_even'].prompt).toBe('True if the integer is even')
      
      // Check language custom transformation
      expect(casts['as_lang_fr']).toBeDefined()
      expect(casts['as_lang_fr'].prompt).toBe('French translation')
      
      // Check string custom transformation
      expect(casts['as_str_uppercase']).toBeDefined()
      expect(casts['as_str_uppercase'].prompt).toBe('Convert to uppercase')
    })

    it('provides access to transformation values', () => {
      const form = chatfield()
        .field('value')
          .desc('Enter a value')
          .as_int()
          .as_int('neg1', 'This is always -1')
          .as_int('doubled', 'Double the integer value')
          .as_int('squared', 'Square the integer value')
          .as_bool('even', 'True if the integer is even')
          .as_lang('fr', 'French translation')
          .as_str('uppercase', 'Convert to uppercase')
        .build()

      // Simulate LLM having provided the value with transformations
      if (form._chatfield.fields.value) {
        form._chatfield.fields.value.value = {
          value: 'six',
          as_int: 6,
          as_int_neg1: -1,
          as_int_doubled: 12,
          as_int_squared: 36,
          as_bool_even: true,
          as_lang_fr: 'six',
          as_str_uppercase: 'SIX',
          context: 'User said six',
          as_quote: 'six'
        }
      }

      // Access the values through field value
      // Note: TypeScript doesn't have FieldProxy like Python, so we access via _chatfield
      const fieldValue = form._chatfield.fields.value?.value
      expect(fieldValue?.value).toBe('six')
      // Check transformations are accessible
      expect(fieldValue?.as_int).toBe(6)
      expect(fieldValue?.as_int_neg1).toBe(-1)
      expect(fieldValue?.as_int_doubled).toBe(12)
      expect(fieldValue?.as_int_squared).toBe(36)
      expect(fieldValue?.as_bool_even).toBe(true)
      expect(fieldValue?.as_lang_fr).toBe('six')
      expect(fieldValue?.as_str_uppercase).toBe('SIX')
    })
  })
})