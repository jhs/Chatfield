/**
 * Demonstrates the type-safe builder for TypeScript users
 */

import { chatfield, chatfieldDynamic } from '../src/builder'

// Type-safe version - TypeScript knows the field names
function typeSafeExample() {
  const form = chatfield()
    .type('UserProfile')
    .desc('Collect user profile information')
    .field('name')
      .desc('Your full name')
      .must('include first and last name')
    .field('email')
      .desc('Your email address')
      .must('be a valid email format')
    .field('age')
      .desc('Your age')
      .as_int()
    .build()
  
  // TypeScript knows these fields exist
  console.log('Fields:', form._chatfield.fields.name?.desc)
  console.log('Fields:', form._chatfield.fields.email?.desc)
  console.log('Fields:', form._chatfield.fields.age?.desc)
  
  // This would be a TypeScript error if uncommented:
  // console.log(form._chatfield.fields.unknown) // Error: Property 'unknown' does not exist
  
  return form
}

// Dynamic version - Python-like experience
function dynamicExample() {
  const form = chatfieldDynamic()
    .type('DynamicForm')
    .desc('Any field names allowed')
    .field('anything')
      .desc('Any field name works')
    .field('random_field_123')
      .desc('Another dynamic field')
    .build()
  
  // Works with any field names
  console.log('Dynamic fields work:', form._chatfield.fields.anything?.desc)
  console.log('Dynamic fields work:', form._chatfield.fields.random_field_123?.desc)
  
  return form
}

// Test callable builders
function callableBuilderExample() {
  const form = chatfield()
    .type('AdvancedForm')
    .alice()
      .type('AI Assistant')
      .trait('helpful')  // Callable trait builder
      .trait('patient')
    .bob()
      .type('User')
      .trait('curious')
    .field('question')
      .desc('Your question')
      .must('be specific')
      .as_lang.fr('Translate to French')  // Sub-attribute cast
      .as_lang.es('Translate to Spanish')
    .field('priority')
      .desc('Priority level')
      .as_one('low', 'medium', 'high')  // Choice builder
    .build()
  
  console.log('Alice traits:', form._chatfield.roles.alice.traits)
  console.log('Bob traits:', form._chatfield.roles.bob.traits)
  console.log('Question casts:', Object.keys(form._chatfield.fields.question?.casts || {}))
  console.log('Priority choices:', form._chatfield.fields.priority?.casts.as_one)
  
  return form
}

// Run examples
console.log('\n=== Type-Safe Example ===')
typeSafeExample()

console.log('\n=== Dynamic Example ===')
dynamicExample()

console.log('\n=== Callable Builder Example ===')
callableBuilderExample()

console.log('\n✅ All examples completed successfully!')