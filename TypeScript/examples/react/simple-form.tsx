/**
 * Simple React example using useChatfield hook
 *
 * This example demonstrates:
 * - Basic useChatfield hook usage
 * - Field collection callbacks
 * - Completion detection
 * - Message display
 *
 * To run this example:
 * 1. Set up a React app (Create React App, Vite, Next.js, etc.)
 * 2. Install dependencies: npm install @chatfield/core @chatfield/react
 * 3. Set up LiteLLM proxy or configure API key
 * 4. Import and use this component
 */

import React from 'react'
import { useChatfield } from '@chatfield/react'
import { chatfield } from '@chatfield/core/lean'

// Define interview
const contactInterview = chatfield()
  .type('Contact Form')
  .desc('Collect basic contact information')
  .field('name')
    .desc('Your full name')
    .must('be at least 2 characters')
  .field('email')
    .desc('Your email address')
    .must('be a valid email format')
  .field('age')
    .desc('Your age')
    .must('be between 18 and 120')
    .as_int()
  .field('interests')
    .desc('What are your interests?')
    .hint('Be specific - share a few things you enjoy')
  .build()

export function SimpleContactForm() {
  const [state, actions] = useChatfield(contactInterview, {
    // Log when fields are collected
    onField: (fieldName, fieldValue) => {
      console.log(`Field collected: ${fieldName}`)
      console.log('Value:', fieldValue)

      // Access transformations
      if (fieldName === 'age') {
        console.log('Age as integer:', fieldValue.as_int)
      }
    },

    // Handle errors
    onError: (error) => {
      console.error('Chatfield error:', error)
      alert(`Error: ${error.message}`)
    }
  })

  // Check if interview is complete
  if (state.interview._done) {
    return (
      <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
        <h2>Thank You!</h2>
        <p>We've collected all your information:</p>
        <ul>
          <li><strong>Name:</strong> {state.interview.name}</li>
          <li><strong>Email:</strong> {state.interview.email}</li>
          <li><strong>Age:</strong> {state.interview.age.as_int}</li>
          <li><strong>Interests:</strong> {state.interview.interests}</li>
        </ul>
      </div>
    )
  }

  // Conversation UI
  return (
    <div style={{
      maxWidth: '600px',
      margin: '0 auto',
      padding: '20px',
      fontFamily: 'sans-serif'
    }}>
      <h1>Contact Form</h1>
      <p style={{ color: '#666' }}>
        Let's collect some information about you through conversation.
      </p>

      {/* Messages */}
      <div style={{
        border: '1px solid #ddd',
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '20px',
        minHeight: '300px',
        maxHeight: '500px',
        overflowY: 'auto',
        backgroundColor: '#f9f9f9'
      }}>
        {state.messages.map((msg, index) => (
          <div
            key={index}
            style={{
              marginBottom: '15px',
              textAlign: msg.role === 'user' ? 'right' : 'left'
            }}
          >
            <div
              style={{
                display: 'inline-block',
                maxWidth: '70%',
                padding: '10px 15px',
                borderRadius: '12px',
                backgroundColor: msg.role === 'user' ? '#007bff' : '#e9ecef',
                color: msg.role === 'user' ? 'white' : 'black',
                textAlign: 'left'
              }}
            >
              <strong style={{ fontSize: '0.85em', opacity: 0.8 }}>
                {msg.role === 'user' ? 'You' : 'AI'}:
              </strong>
              <div style={{ marginTop: '5px' }}>{msg.content}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Input */}
      <div style={{ display: 'flex', gap: '10px' }}>
        <input
          type="text"
          placeholder={
            state.isReadyForInput
              ? 'Type your response...'
              : 'AI is thinking...'
          }
          disabled={!state.isReadyForInput}
          style={{
            flex: 1,
            padding: '12px',
            border: '1px solid #ddd',
            borderRadius: '6px',
            fontSize: '16px',
            opacity: state.isReadyForInput ? 1 : 0.6
          }}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              const input = e.currentTarget
              const value = input.value.trim()
              if (value) {
                actions.send(value)
                input.value = ''
              }
            }
          }}
        />
        <button
          disabled={!state.isReadyForInput}
          style={{
            padding: '12px 24px',
            backgroundColor: state.isReadyForInput ? '#007bff' : '#ccc',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: state.isReadyForInput ? 'pointer' : 'not-allowed',
            fontSize: '16px'
          }}
          onClick={(e) => {
            const input = e.currentTarget.previousElementSibling as HTMLInputElement
            const value = input.value.trim()
            if (value) {
              actions.send(value)
              input.value = ''
            }
          }}
        >
          Send
        </button>
      </div>

      {/* Status indicator */}
      <div style={{
        marginTop: '10px',
        fontSize: '14px',
        color: '#666',
        textAlign: 'center'
      }}>
        {state.isReadyForInput ? '✓ Ready for input' : '⏳ AI is thinking...'}
      </div>
    </div>
  )
}
