/**
 * Core Interview class for Chatfield
 * Mirrors Python's interview.py
 */

import { createFieldProxy } from './field-proxy'
import type { FieldSpecs } from './builder-types'

/**
 * Main Interview class that holds collected data
 * Mirrors Python's Interview class with _chatfield structure
 */
export class Interview {
  // The core data structure mirroring Python's _chatfield
  _chatfield: {
    type: string
    desc: string
    roles: {
      alice: { type: string; traits: string[]; possible_traits?: Record<string, any> }
      bob: { type: string; traits: string[]; possible_traits?: Record<string, any> }
    }
    fields: Record<string, {
      desc: string
      specs: FieldSpecs
      casts: Record<string, any>
      value: null | {
        value: string
        context?: string
        as_quote?: string
        [key: string]: any  // For transformations like as_int, as_bool, etc.
      }
    }>
  }

  constructor(type?: string, desc?: string, roles?: any, fields?: any) {
    // Initialize with default structure matching Python
    this._chatfield = {
      type: type || '',
      desc: desc || '',
      roles: roles || {
        alice: {
          type: 'Agent',
          traits: [],
          possible_traits: {}
        },
        bob: {
          type: 'User', 
          traits: [],
          possible_traits: {}
        }
      },
      fields: fields || {}
    }
  }

  /**
   * Get the name/type of this Interview
   */
  _name(): string {
    return this._chatfield.type
  }

  /**
   * Get list of field names
   */
  _fields(): string[] {
    return Object.keys(this._chatfield.fields)
  }

  /**
   * Get alice role name
   */
  _alice_role_name(): string {
    return this._chatfield.roles.alice.type || 'Agent'
  }

  /**
   * Get bob role name
   */
  _bob_role_name(): string {
    return this._chatfield.roles.bob.type || 'User'
  }

  /**
   * Get alice role details (method version for Python compatibility)
   */
  _alice_role(): { type?: string; traits: string[] } {
    return this._chatfield.roles.alice
  }

  /**
   * Get bob role details (method version for Python compatibility)
   */
  _bob_role(): { type?: string; traits: string[] } {
    return this._chatfield.roles.bob
  }

  /**
   * Get alice role details
   */
  get _alice(): { type: string; traits: string[] } {
    return this._chatfield.roles.alice
  }

  /**
   * Get bob role details
   */
  get _bob(): { type: string; traits: string[] } {
    return this._chatfield.roles.bob
  }

  /**
   * Get role by name
   */
  _get_role(role_name: string): any {
    if (role_name === 'alice') return this._chatfield.roles.alice
    if (role_name === 'bob') return this._chatfield.roles.bob
    return null
  }

  /**
   * Get field metadata and value
   */
  _get_chat_field(field_name: string): any {
    return this._chatfield.fields[field_name]
  }

  /**
   * Check if all required fields have values
   */
  get _done(): boolean {
    return Object.values(this._chatfield.fields).every(field => field.value !== null)
  }

  /**
   * Check if enough fields have been collected (can be customized)
   * Returns true when all non-confidential, non-conclude fields are populated
   */
  get _enough(): boolean {
    // Check if all non-confidential, non-conclude fields have been collected
    for (const [fieldName, chatfield] of Object.entries(this._chatfield.fields)) {
      const specs = chatfield.specs
      if (!specs.confidential && !specs.conclude) {
        // This is a "normal" field
        if (chatfield.value === null) {
          return false
        }
      }
    }
    return true
  }

  /**
   * Serialize to plain object (mirrors Python's model_dump)
   */
  model_dump(): any {
    return JSON.parse(JSON.stringify(this._chatfield))
  }

  /**
   * Copy data from another Interview
   */
  _copy_from(source: Interview): void {
    this._chatfield = JSON.parse(JSON.stringify(source._chatfield))
  }

  /**
   * Pretty print the interview state (Python compatibility)
   */
  _pretty(): string {
    const lines: string[] = []
    lines.push(`${this._chatfield.type}: ${this._chatfield.desc}`)
    lines.push('Fields:')
    for (const [name, field] of Object.entries(this._chatfield.fields)) {
      const value = field.value?.value || '<not set>'
      lines.push(`  ${name}: ${value}`)
    }
    return lines.join('\n')
  }

  /**
   * Initialize a field's metadata structure
   */
  static _init_field(func: any): void {
    if (!func._chatfield) {
      func._chatfield = {
        specs: {},
        casts: {}
      }
    }
  }

  /**
   * Get field value with proxy support (for transformations)
   * This allows interview.fieldName to return a FieldProxy
   */
  [key: string]: any

  /**
   * Override property access to return FieldProxy for field values
   */
  __getattr__(name: string): any {
    if (name in this._chatfield.fields) {
      const field = this._chatfield.fields[name]
      if (field && field.value && field.value.value) {
        return createFieldProxy(field.value.value, field)
      }
      return null
    }
    // Return actual property if it exists
    return (this as any)[name]
  }
}

// For backwards compatibility
export const Gatherer = Interview
export const GathererInstance = Interview

// Helper type
export type CollectedData = Record<string, string>
export type InterviewOptions = {
  maxRetryAttempts?: number
  [key: string]: any
}

// Metadata classes for compatibility
export class InterviewMeta {
  userContext: string[] = []
  agentContext: string[] = []  
  docstring: string = ''
  fields: Map<string, FieldMeta> = new Map()

  addUserContext(context: string): void {
    this.userContext.push(context)
  }

  addAgentContext(context: string): void {
    this.agentContext.push(context)
  }

  setDocstring(doc: string): void {
    this.docstring = doc
  }

  addField(name: string, description: string): FieldMeta {
    const field = new FieldMeta(name, description)
    this.fields.set(name, field)
    return field
  }

  getFields(): FieldMeta[] {
    return Array.from(this.fields.values())
  }
}

export class FieldMeta {
  name: string
  description: string
  mustRules: string[] = []
  rejectRules: string[] = []
  hint?: string

  constructor(name: string, description: string) {
    this.name = name
    this.description = description
  }

  addMustRule(rule: string): void {
    this.mustRules.push(rule)
  }

  addRejectRule(rule: string): void {
    this.rejectRules.push(rule)
  }

  setHint(hint: string): void {
    this.hint = hint
  }


  hasValidationRules(): boolean {
    return this.mustRules.length > 0 || this.rejectRules.length > 0
  }
}