/**
 * Type-safe Builder API for creating Chatfield interviews.
 * Mirrors Python's builder.py with full TypeScript type tracking.
 */

import { Interview } from './interview'
import { createFieldProxy } from './field-proxy'
import type {
  FieldMeta,
  FieldSpecs,
  InterviewMeta,
  RoleMeta,
  TraitBuilder,
  CastBuilder,
  ChoiceBuilder,
  CastInfo,
  FieldValue
} from './builder-types'

/**
 * Creates a callable TraitBuilder
 */
function createTraitBuilder(parent: RoleBuilder, role: string): TraitBuilder {
  const addTrait = (trait: string) => {
    parent._addTrait(role, trait)
    return parent
  }
  
  addTrait.possible = (name: string, trigger: string = "") => {
    parent._addPossibleTrait(role, name, trigger)
    return parent
  }
  
  return addTrait
}

/**
 * Creates a callable CastBuilder with function-based API
 */
function createCastBuilder<TParent extends FieldBuilder<any, any>>(
  parent: TParent,
  baseName: string,
  primitiveType: any,
  basePrompt: string,
  requiresSubName: boolean = false
): CastBuilder<TParent> {
  // Function with overloads for different parameter combinations
  const castFunction = function(...args: any[]): TParent {
    let subName: string | undefined
    let customPrompt: string | undefined
    
    if (requiresSubName) {
      // Mandatory sub-name (like as_lang)
      // as_lang("fr") or as_lang("fr", "Translate to French")
      if (args.length === 0) {
        throw new Error(`${baseName} requires a sub-name parameter`)
      }
      subName = String(args[0])
      customPrompt = args[1] ? String(args[1]) : undefined
    } else {
      // Optional sub-name (like as_int)
      if (args.length === 0) {
        // as_int() - default behavior
      } else if (args.length === 1) {
        // as_int("custom prompt") - override prompt
        customPrompt = String(args[0])
      } else if (args.length >= 2) {
        // as_int("severity", "Range 0-10") - sub-name + prompt
        subName = String(args[0])
        customPrompt = String(args[1])
      }
    }
    
    // Build the cast name
    const castName = subName ? `${baseName}_${subName}` : baseName
    
    // Build the prompt
    let finalPrompt: string
    if (customPrompt) {
      finalPrompt = customPrompt
    } else if (subName && basePrompt.includes('{name}')) {
      finalPrompt = basePrompt.replace('{name}', subName)
    } else if (subName) {
      finalPrompt = `${basePrompt} for ${subName}`
    } else {
      finalPrompt = basePrompt
    }
    
    // Store the cast
    const castInfo: CastInfo = {
      type: typeof primitiveType === 'function' ? primitiveType.name.toLowerCase() : String(primitiveType),
      prompt: finalPrompt
    }
    parent._chatfieldField.casts[castName] = castInfo
    return parent
  }
  
  return castFunction as CastBuilder<TParent>
}

/**
 * Creates a callable ChoiceBuilder with function-based API
 */
function createChoiceBuilder<TParent extends FieldBuilder<any, any>>(
  parent: TParent,
  baseName: string,
  nullAllowed: boolean,
  multi: boolean
): ChoiceBuilder<TParent> {
  const choiceFunction = function(...args: any[]): TParent {
    let subName: string | undefined
    let choices: string[]
    
    // Check if first arg is a sub-name (non-choice string followed by choices)
    if (args.length >= 2 && typeof args[0] === 'string') {
      // Could be as_one('selection', 'red', 'green', 'blue')
      // We'll treat it as sub-name if followed by more strings
      const possibleChoices = args.slice(1)
      if (possibleChoices.every(arg => typeof arg === 'string')) {
        subName = args[0]
        choices = possibleChoices
      } else {
        // All args are choices
        choices = args
      }
    } else {
      // Direct choices: as_one('red', 'green', 'blue')
      choices = args
    }
    
    // Build the cast name
    const castName = subName ? `${baseName}_${subName}` : baseName
    
    // Build the prompt
    const promptBase = `Choose ${multi ? 'one or more' : 'one'}`
    const prompt = subName ? `${promptBase} for ${subName}` : promptBase
    
    // Store the cast
    const castInfo: CastInfo = {
      type: 'choice',
      prompt: prompt,
      choices: choices,
      null: nullAllowed,
      multi: multi
    }
    parent._chatfieldField.casts[castName] = castInfo
    return parent
  }
  
  return choiceFunction as ChoiceBuilder<TParent>
}

/**
 * Builder for alice/bob role configuration.
 * Mirrors Python's RoleBuilder
 */
export class RoleBuilder<Fields extends string = never> {
  parent: ChatfieldBuilder<Fields>
  role: string
  trait: TraitBuilder

  constructor(parent: ChatfieldBuilder<Fields>, role: string) {
    this.parent = parent
    this.role = role
    this._ensureRole()
    // Set context for subsequent calls
    this.parent._currentRole = role
    this.trait = createTraitBuilder(this, role)
  }

  private _ensureRole(): void {
    // Ensure role exists in chatfield structure
    if (!(this.role in this.parent._chatfield.roles)) {
      this.parent._chatfield.roles[this.role] = {
        type: null,
        traits: [],
        possible_traits: {}
      }
    }
  }

  type(roleType: string): RoleBuilder<Fields> {
    // Set the role type
    const roleData = this.parent._chatfield.roles[this.role]
    if (roleData) {
      roleData.type = roleType
    }
    return this
  }

  _addTrait(role: string, trait: string): void {
    // Add a regular trait
    const roleData = this.parent._chatfield.roles[role]
    if (roleData && !roleData.traits.includes(trait)) {
      roleData.traits.push(trait)
    }
  }

  _addPossibleTrait(role: string, name: string, trigger: string): void {
    // Add a possible trait
    const roleData = this.parent._chatfield.roles[role]
    if (roleData && roleData.possible_traits) {
      roleData.possible_traits[name] = {
        active: false,
        desc: trigger
      }
    }
  }

  field<Name extends string>(name: Name): FieldBuilder<Fields | Name, Name> {
    // Start defining a new field
    return this.parent.field(name)
  }

  alice(): RoleBuilder<Fields> {
    // Switch to alice configuration
    return this.parent.alice()
  }

  bob(): RoleBuilder<Fields> {
    // Switch to bob configuration
    return this.parent.bob()
  }

  build(): TypedInterview<Fields> {
    // Build the final Interview
    return this.parent.build()
  }
}

/**
 * Builder for field configuration with all decorators.
 * Tracks the field name and transformations in the type system.
 */
export class FieldBuilder<
  Fields extends string, 
  CurrentField extends string,
  CurrentTransforms extends Record<string, any> = {}
> {
  parent: ChatfieldBuilder<Fields>
  fieldName: CurrentField
  _chatfieldField: FieldMeta

  // Cast builders - these will be replaced with typed methods
  as_int: CastBuilder<this>
  as_float: CastBuilder<this>
  as_bool: CastBuilder<this>
  as_percent: CastBuilder<this>
  as_lang: CastBuilder<this>
  as_str: CastBuilder<this>
  as_list: CastBuilder<this>
  as_set: CastBuilder<this>
  as_dict: CastBuilder<this>
  as_obj: CastBuilder<this>
  as_context: CastBuilder<this>
  as_quote: CastBuilder<this>
  as_one: ChoiceBuilder<this>
  as_maybe: ChoiceBuilder<this>
  as_multi: ChoiceBuilder<this>
  as_any: ChoiceBuilder<this>

  constructor(parent: ChatfieldBuilder<Fields>, fieldName: CurrentField) {
    this.parent = parent
    this.fieldName = fieldName
    
    // Ensure field exists
    const fieldKey = fieldName as unknown as Fields
    if (!(fieldKey in this.parent._chatfield.fields)) {
      (this.parent._chatfield.fields as any)[fieldKey] = {
        desc: '',
        specs: {
          must: [],
          reject: [],
          hint: []
        },
        casts: {},
        value: null
      }
    }
    
    this._chatfieldField = (this.parent._chatfield.fields as any)[fieldKey]
    
    // Set as current field
    this.parent._currentField = fieldName as string
    
    // Initialize cast builders
    // Basic type casts (no sub-attributes)
    this.as_int = createCastBuilder(this, 'as_int', Number, 'parse as integer', false)
    this.as_float = createCastBuilder(this, 'as_float', Number, 'parse as float', false)
    this.as_bool = createCastBuilder(this, 'as_bool', Boolean, 'parse as boolean', false)
    this.as_percent = createCastBuilder(this, 'as_percent', Number, 'parse as percentage (0-100)', false)
    this.as_list = createCastBuilder(this, 'as_list', Array, 'parse as list/array', false)
    this.as_set = createCastBuilder(this, 'as_set', Set, 'parse as unique set', false)
    this.as_dict = createCastBuilder(this, 'as_dict', Object, 'parse as key-value dictionary', false)
    this.as_obj = this.as_dict  // Alias
    this.as_context = createCastBuilder(this, 'as_context', String, 'capture conversational context', false)
    this.as_quote = createCastBuilder(this, 'as_quote', String, 'capture direct user quote', false)
    
    // Sub-attribute casts
    this.as_str = createCastBuilder(this, 'as_str', String, 'format as {name}', false)
    
    // Mandatory sub-name cast (requires at least 1 arg)
    this.as_lang = createCastBuilder(this, 'as_lang', String, 'translate to {name}', true)
    
    // Initialize choice builders
    this.as_one = createChoiceBuilder(this, 'as_one', false, false)
    this.as_maybe = createChoiceBuilder(this, 'as_maybe', true, false)
    this.as_multi = createChoiceBuilder(this, 'as_multi', false, true)
    this.as_any = createChoiceBuilder(this, 'as_any', true, true)
  }

  desc(description: string): this {
    // Set field description
    this._chatfieldField.desc = description
    return this
  }

  must(rule: string): this {
    // Add a validation requirement
    if (!this._chatfieldField.specs.must) {
      this._chatfieldField.specs.must = []
    }
    this._chatfieldField.specs.must.push(rule)
    return this
  }

  reject(rule: string): this {
    // Add a rejection rule
    if (!this._chatfieldField.specs.reject) {
      this._chatfieldField.specs.reject = []
    }
    this._chatfieldField.specs.reject.push(rule)
    return this
  }

  hint(tooltip: string): this {
    // Add helpful context
    if (!this._chatfieldField.specs.hint) {
      this._chatfieldField.specs.hint = []
    }
    this._chatfieldField.specs.hint.push(tooltip)
    return this
  }

  confidential(): this {
    // Mark field as confidential (tracked silently)
    this._chatfieldField.specs.confidential = true
    return this
  }

  conclude(): this {
    // Mark field for evaluation only after conversation ends (automatically confidential)
    this._chatfieldField.specs.conclude = true
    this._chatfieldField.specs.confidential = true  // Implied
    return this
  }

  field<Name extends string>(name: Name): FieldBuilder<Fields | Name, Name> {
    // Start defining a new field
    return this.parent.field(name)
  }

  alice(): RoleBuilder<Fields> {
    // Switch to alice configuration
    return this.parent.alice()
  }

  bob(): RoleBuilder<Fields> {
    // Switch to bob configuration
    return this.parent.bob()
  }

  build(): TypedInterview<Fields> {
    // Build the final Interview
    return this.parent.build()
  }
}

/**
 * Main builder for creating Chatfield interviews with type tracking.
 * The Fields generic tracks all field names added during building.
 */
export class ChatfieldBuilder<Fields extends string = never> {
  _chatfield: InterviewMeta<Fields>
  _currentField: string | null
  _currentRole: string | null

  constructor() {
    this._chatfield = {
      type: '',
      desc: '',
      roles: {
        alice: {
          type: null,
          traits: [],
          possible_traits: {}
        },
        bob: {
          type: null,
          traits: [],
          possible_traits: {}
        }
      },
      fields: {} as Record<Fields, FieldMeta>
    }
    this._currentField = null
    this._currentRole = null
  }

  type(name: string): ChatfieldBuilder<Fields> {
    // Set the interview type name
    this._chatfield.type = name
    return this
  }

  desc(description: string): ChatfieldBuilder<Fields> {
    // Set the interview description
    this._chatfield.desc = description
    return this
  }

  alice(): RoleBuilder<Fields> {
    // Configure alice (interviewer) role
    return new RoleBuilder(this, 'alice')
  }

  bob(): RoleBuilder<Fields> {
    // Configure bob (interviewee) role
    return new RoleBuilder(this, 'bob')
  }

  field<Name extends string>(name: Name): FieldBuilder<Fields | Name, Name> {
    // Start defining a new field, tracking its name in the type system
    return new FieldBuilder(this as any as ChatfieldBuilder<Fields | Name>, name)
  }

  build(): TypedInterview<Fields> {
    // Build the final Interview with known field names
    const interview = new Interview(
      this._chatfield.type,
      this._chatfield.desc,
      this._chatfield.roles,
      this._chatfield.fields
    )
    
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
    
    return proxiedInterview as TypedInterview<Fields>
  }
}

/**
 * Type-safe Interview with known field names and transformations
 * For now, we'll use a simplified approach where all fields have all possible transformations
 */
export type TypedInterview<Fields extends string> = Interview & {
  [K in Fields]: FieldValue<{
    as_int?: number
    as_float?: number
    as_bool?: boolean
    as_percent?: number
    as_list?: any[]
    as_set?: Set<any>
    as_dict?: Record<string, any>
    as_obj?: Record<string, any>
    as_context?: string
    as_quote?: string
    [key: `as_lang_${string}`]: string
    [key: `as_str_${string}`]: string
    [key: `as_bool_${string}`]: boolean
    [key: `as_int_${string}`]: number
    [key: `as_set_${string}`]: Set<any>
    [key: `as_one_${string}`]: string
    [key: `as_maybe_${string}`]: string | null
    [key: `as_multi_${string}`]: Set<string>
    [key: `as_any_${string}`]: Set<string>
  }>
}

/**
 * Main entry point - creates a new type-safe builder
 * @returns A new ChatfieldBuilder instance
 */
export function chatfield<Fields extends string = never>(): ChatfieldBuilder<Fields> {
  return new ChatfieldBuilder<Fields>()
}

/**
 * Loose type version for dynamic field names (Python-like experience)
 */
export function chatfieldDynamic(): ChatfieldBuilder<string> {
  return new ChatfieldBuilder<string>()
}

/**
 * Preset builders for common patterns
 */

/**
 * Create a patient, thorough gatherer.
 * Mirrors Python's patient_gatherer()
 */
export function patientGatherer(): ChatfieldBuilder<string> {
  const builder = chatfield<string>()
    .alice()
  builder.trait('Takes time to understand')
  builder.trait('Asks clarifying questions when responses are unclear or incomplete')
  builder.trait('Guides the conversation with gentle suggestions if needed')
  return builder.parent
}

/**
 * Create a quick, efficient gatherer.
 * Mirrors Python's quick_gatherer()
 */
export function quickGatherer(): ChatfieldBuilder<string> {
  const builder = chatfield<string>()
    .alice()
  builder.trait('Gets to the point quickly')
  builder.trait('Focuses on essential information without extra conversation')
  builder.trait('Efficient and business-like')
  return builder.parent
}

/**
 * Create an expert consultation gatherer.
 * Mirrors Python's expert_gatherer()
 */
export function expertGatherer(): ChatfieldBuilder<string> {
  const builder = chatfield<string>()
    .alice()
  builder.trait('Acts as a domain expert')
  builder.trait('Provides context and education during the conversation')
  builder.trait('Can explain complex topics when relevant to the discussion')
  return builder.parent
}