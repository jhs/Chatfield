/**
 * Tests for validation functionality (must, reject, hint).
 * Uses real LLM to test validation behavior.
 */

import { chatfield } from '../chatfield/builder'
import { Interviewer } from '../chatfield/interviewer'

describe('Validation', () => {
  // A few unit tests for validation. Small and simple, because testing the prompts is out of scope.

  const testFn = process.env.OPENAI_API_KEY ? test : test.skip

  testFn('passes must', async () => {
    // A 'must' validation should pass when requirement is met
    const interview = chatfield()
      .field('favorite_color')
      .desc("What's your favorite color?")
      .must('be a primary color name')
      .build()

    const interviewer = new Interviewer(interview)
    await interviewer.go('My favorite color is blue')

    expect(String(interview.favorite_color)).toBe('blue')
  })

  testFn('fails must', async () => {
    // A 'must' validation should fail when requirement is not met
    const interview = chatfield()
      .field('favorite_color')
      .desc("What's your favorite color?")
      .must('be a primary color name')
      .build()

    const interviewer = new Interviewer(interview)
    await interviewer.go('My favorite color is the planet Saturn')

    expect(interview.favorite_color).toBeNull()
  })

  testFn('passes reject', async () => {
    // A 'reject' validation should pass when pattern is avoided
    const interview = chatfield()
      .field('first_name')
      .desc('What is your name? (No spaces or special characters allowed.)')
      .reject('contain spaces or special characters')
      .build()

    const interviewer = new Interviewer(interview)
    await interviewer.go('My name is Sam')

    expect(String(interview.first_name)).toBe('Sam')
  })

  testFn('fails reject', async () => {
    // A 'reject' validation should fail when pattern is present
    const interview = chatfield()
      .field('first_name')
      .desc('What is your name? (No spaces or special characters allowed.)')
      .reject('contain spaces or special characters')
      .build()

    const interviewer = new Interviewer(interview)
    await interviewer.go('My name is @l!ce')

    expect(interview.first_name).toBeNull()
  })

  testFn('must and reject both pass', async () => {
    // Both 'must' and 'reject' validations should work together
    const interview = chatfield()
      .field('age')
      .desc('How old are you?')
      .must('be a number between 1 and 120')
      .reject('negative numbers or text')
      .build()

    const interviewer = new Interviewer(interview)
    await interviewer.go('I am 25 years old')

    expect(String(interview.age)).toBe('25')
  })

  test('hint appears in system prompt', () => {
    // A 'hint' should appear in the system prompt
    const formNoHint = chatfield()
      .field('email')
      .desc("What's your email?")
      .build()

    const formWithHint = chatfield()
      .field('email')
      .desc("What's your email?")
      .hint('Format: name@example.com')
      .build()

    let interviewer = new Interviewer(formNoHint)
    let prompt = interviewer.mkSystemPrompt({ interview: formNoHint } as any)
    expect(prompt).not.toContain('Hint')

    interviewer = new Interviewer(formWithHint)
    prompt = interviewer.mkSystemPrompt({ interview: formWithHint } as any)
    expect(prompt).toContain('Hint')
  })

  // TODO: There is some more logic to test, e.g. hints override validation.
})