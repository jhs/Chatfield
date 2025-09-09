/**
 * TypeScript decorators for Chatfield - mirroring Python implementation
 */

import 'reflect-metadata'
import { InterviewMeta, FieldMeta } from './interview'
import { Interview } from './interview'
// TODO: Replace with Interviewer from interviewer.ts

// Metadata keys for storing decorator information
const CHATFIELD_FIELDS = Symbol('chatfield:fields')
const CHATFIELD_USER_CONTEXT = Symbol('chatfield:user_context')
const CHATFIELD_AGENT_CONTEXT = Symbol('chatfield:agent_context')

// Field metadata storage
interface FieldDescriptor {
  name: string
  description: string
  mustRules: string[]
  rejectRules: string[]
  hint?: string
}

/**
 * Define a field with description and optional validation
 */
export function field(description: string, options?: {
  must?: string | string[]
  reject?: string | string[]
  hint?: string
}) {
  return function (target: any, propertyKey: string) {
    if (!target[CHATFIELD_FIELDS]) {
      target[CHATFIELD_FIELDS] = new Map<string, FieldDescriptor>()
    }
    
    const mustRules = options?.must 
      ? Array.isArray(options.must) ? options.must : [options.must]
      : []
    
    const rejectRules = options?.reject
      ? Array.isArray(options.reject) ? options.reject : [options.reject] 
      : []
    
    target[CHATFIELD_FIELDS].set(propertyKey, {
      name: propertyKey,
      description,
      mustRules,
      rejectRules,
      hint: options?.hint
    })
  }
}

/**
 * Add a must rule to a field (can stack multiple)
 */
export function must(rule: string) {
  return function (target: any, propertyKey: string) {
    if (!target[CHATFIELD_FIELDS]) {
      target[CHATFIELD_FIELDS] = new Map<string, FieldDescriptor>()
    }
    
    const existing = target[CHATFIELD_FIELDS].get(propertyKey) || {
      name: propertyKey,
      description: propertyKey, // fallback
      mustRules: [],
      rejectRules: []
    }
    
    existing.mustRules.push(rule)
    target[CHATFIELD_FIELDS].set(propertyKey, existing)
  }
}

/**
 * Add a reject rule to a field (can stack multiple)
 */
export function reject(rule: string) {
  return function (target: any, propertyKey: string) {
    if (!target[CHATFIELD_FIELDS]) {
      target[CHATFIELD_FIELDS] = new Map<string, FieldDescriptor>()
    }
    
    const existing = target[CHATFIELD_FIELDS].get(propertyKey) || {
      name: propertyKey,
      description: propertyKey, // fallback
      mustRules: [],
      rejectRules: []
    }
    
    existing.rejectRules.push(rule)
    target[CHATFIELD_FIELDS].set(propertyKey, existing)
  }
}

/**
 * Add a hint to a field
 */
export function hint(tooltip: string) {
  return function (target: any, propertyKey: string) {
    if (!target[CHATFIELD_FIELDS]) {
      target[CHATFIELD_FIELDS] = new Map<string, FieldDescriptor>()
    }
    
    const existing = target[CHATFIELD_FIELDS].get(propertyKey) || {
      name: propertyKey,
      description: propertyKey, // fallback
      mustRules: [],
      rejectRules: []
    }
    
    existing.hint = tooltip
    target[CHATFIELD_FIELDS].set(propertyKey, existing)
  }
}

/**
 * Add information about bob (the user)
 */
export function bob(roleType: string) {
  return function <T extends { new(...args: any[]): {} }>(constructor: T): T {
    if (!constructor.prototype[CHATFIELD_USER_CONTEXT]) {
      constructor.prototype[CHATFIELD_USER_CONTEXT] = []
    }
    constructor.prototype[CHATFIELD_USER_CONTEXT].push(roleType)
    return constructor
  }
}

/**
 * Define how alice (the agent) should behave
 */
export function alice(roleType: string) {
  return function <T extends { new(...args: any[]): {} }>(constructor: T): T {
    if (!constructor.prototype[CHATFIELD_AGENT_CONTEXT]) {
      constructor.prototype[CHATFIELD_AGENT_CONTEXT] = []
    }
    constructor.prototype[CHATFIELD_AGENT_CONTEXT].push(roleType)
    return constructor
  }
}

// Aliases for backwards compatibility
export const user = bob
export const agent = alice

/**
 * Transform a class into a conversational gatherer
 */
export function interview<T extends { new(...args: any[]): {} }>(constructor: T): T & InterviewClass {
  // Process the class to extract metadata
  const meta = processInterviewClass(constructor)
  
  // Create new class that extends the original
  class InterviewedClass extends constructor {
    static async gather(): Promise<Interview> {
      // TODO: Replace with Interviewer implementation
      console.warn('Decorator interview() needs refactoring to use Interviewer')
      const collectedData = {} // Temporary stub
      return new Interview(meta, collectedData)
    }
    
    static _chatfield_meta = meta
    
    static getFieldPreview() {
      return meta.getFields().map(field => ({
        name: field.name,
        description: field.description,
        hasValidation: field.hasValidationRules(),
        hint: field.hint
      }))
    }
  }
  
  // Preserve the original class name
  Object.defineProperty(GatheredClass, 'name', { value: constructor.name })
  
  return GatheredClass as any
}

/**
 * Extract all metadata from a decorated class (mirrors Python implementation)
 */
function processInterviewClass(cls: any): InterviewMeta {
  const meta = new InterviewMeta()
  
  // Get docstring from class name
  if (cls.name) {
    meta.setDocstring(`${cls.name} data gathering session`)
  }
  
  // Get user/agent context from class decorators
  const userContext = cls.prototype[CHATFIELD_USER_CONTEXT] || []
  const agentContext = cls.prototype[CHATFIELD_AGENT_CONTEXT] || []
  
  userContext.forEach((context: string) => meta.addUserContext(context))
  agentContext.forEach((behavior: string) => meta.addAgentContext(behavior))
  
  // Get field metadata from decorators
  const fields = cls.prototype[CHATFIELD_FIELDS] || new Map<string, FieldDescriptor>()
  
  // Process each field descriptor
  for (const [propertyKey, fieldDesc] of fields) {
    const fieldMeta = meta.addField(fieldDesc.name, fieldDesc.description)
    
    // Add validation rules
    fieldDesc.mustRules.forEach((rule: string) => fieldMeta.addMustRule(rule))
    fieldDesc.rejectRules.forEach((rule: string) => fieldMeta.addRejectRule(rule))
    
    if (fieldDesc.hint) {
      fieldMeta.setHint(fieldDesc.hint)
    }
  }
  
  return meta
}

/**
 * Helper type for interview classes
 */
export interface InterviewClass {
  gather(): Promise<Interview>
  getFieldPreview(): Array<{
    name: string
    description: string
    hasValidation: boolean
    hint?: string
  }>
  _chatfield_meta: InterviewMeta
}

// Alias for backwards compatibility
export const gather = interview
export type GathererClass = InterviewClass