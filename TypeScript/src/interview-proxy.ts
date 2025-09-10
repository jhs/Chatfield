/**
 * Interview proxy utility for wrapping Interview instances with field access
 * This ensures field values are returned as FieldProxy instances
 */

import { Interview } from './interview'
import { createFieldProxy } from './field-proxy'

/**
 * Wraps an Interview instance with a Proxy to intercept field access
 * and return FieldProxy instances for field values.
 * 
 * This is necessary because TypeScript doesn't have Python's __getattr__
 * magic method, so we use a Proxy to achieve similar behavior.
 * 
 * @param interview The Interview instance to wrap
 * @returns A proxied Interview that returns FieldProxy for field access
 */
export function wrapInterviewWithProxy(interview: Interview): Interview {
  // If interview is null/undefined, return as-is
  if (!interview) {
    return interview
  }

  // Wrap the interview in a Proxy to intercept field access
  const proxiedInterview = new Proxy(interview, {
    get(target: Interview, prop: string | symbol, receiver: any) {
      // Check if this is a field name
      if (typeof prop === 'string' && prop in target._chatfield.fields) {
        const field = target._chatfield.fields[prop]
        if (field && field.value && field.value.value) {
          // Return a FieldProxy for the field value
          return createFieldProxy(field.value.value, field)
        }
        return null
      }
      
      // Otherwise, return the original property
      return Reflect.get(target, prop, receiver)
    }
  })
  
  return proxiedInterview
}