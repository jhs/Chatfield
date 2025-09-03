/**
 * Chatfield: Conversational data gathering powered by LLMs
 * TypeScript/JavaScript implementation
 * Mirrors Python's __init__.py structure
 */

// Core classes - mirroring Python
export { Interview } from './interview'
export { Interviewer } from './interviewer'
export { 
  createFieldProxy,  // Required for TypeScript Proxy creation
  type FieldProxy,
  type FieldTransformations,
  type FieldMetadata
} from './field-proxy'

// Builder API - mirroring Python  
export { 
  chatfield,
  patientGatherer,
  quickGatherer,
  expertGatherer,
  // Builder classes (for type annotations if needed)
  ChatfieldBuilder,
  FieldBuilder,
  RoleBuilder,
  TraitBuilder,
  CastBuilder,
  ChoiceBuilder
} from './builder'

// Decorators - mirroring Python
export { 
  alice, 
  bob,
  must, 
  reject, 
  hint,
  // Type transformations (will be added later)
  // as_int, as_float, as_bool, as_str, as_list, as_dict, as_set, as_obj,
  // as_lang, as_percent,
  // as_any, as_one, as_maybe, as_multi
} from './decorators'

// Metadata classes
export { InterviewMeta, FieldMeta } from './interview'

// Types
export type {
  FieldMetaOptions,
  InterviewSchema,
  ConversationMessage,
  ValidationResult,
  CollectedData,
  InterviewOptions
} from './types'

// Backwards compatibility exports (deprecated)
export { Interview as Gatherer } from './interview'
export { Interview as GathererInstance } from './interview'
export { InterviewMeta as GathererMeta } from './metadata'
export type { InterviewSchema as GathererSchema } from './types'
export type { InterviewOptions as GathererOptions } from './types'
export { alice as agent, bob as user } from './decorators'