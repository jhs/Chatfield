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
  chatfieldDynamic,
  patientGatherer,
  quickGatherer,
  expertGatherer,
  // Builder classes (for type annotations if needed)
  ChatfieldBuilder,
  FieldBuilder,
  RoleBuilder,
  // Type exports
  type TypedInterview
} from './builder'

// Builder type interfaces
export type {
  TraitBuilder,
  CastBuilder,
  ChoiceBuilder,
  InterviewMeta,
  FieldSpecs,
  FieldMeta as FieldMetaType,
  RoleMeta
} from './builder-types'


// Metadata classes  
export { FieldMeta } from './interview'

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
export type { InterviewSchema as GathererSchema } from './types'
export type { InterviewOptions as GathererOptions } from './types'