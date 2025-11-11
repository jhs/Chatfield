/**
 * Type definitions for the type-safe builder API
 *
 * NOTE: This file is TypeScript-specific and an exception to the parallel
 * Python/TypeScript structure. TypeScript requires explicit type definitions
 * for the builder pattern to provide compile-time type safety and IDE
 * autocompletion, features that Python handles through runtime introspection.
 */

/**
 * Generic type for tracking field transformations at compile time
 */
export type FieldTransformations<T extends Record<string, any> = {}> = T;

/**
 * Base field value type - always a string with tracked transformations
 */
export type FieldValue<Transforms extends Record<string, any> = {}> = string &
  Transforms & {
    as_quote?: string;
    as_context?: string;
    _chatfield?: any;
    _pretty?: () => string;
  };

/**
 * Field configuration with transformation tracking
 */
export type FieldConfig<Transforms = {}> = {
  desc: string;
  specs: FieldSpecs;
  casts: Transforms;
  value: any;
};

/**
 * Field specification with all validation rules
 */
export interface FieldSpecs {
  must?: string[];
  reject?: string[];
  hint?: string[];
  confidential?: boolean;
  conclude?: boolean;
}

/**
 * Cast information for field transformations
 */
export interface CastInfo {
  type: string;
  prompt: string;
  choices?: string[];
  null?: boolean;
  multi?: boolean;
}

/**
 * Field metadata structure
 */
export interface FieldMeta {
  desc: string;
  specs: FieldSpecs;
  casts: Record<string, CastInfo>;
  value: null | {
    value: string;
    context?: string;
    as_quote?: string;
    [key: string]: any; // For transformations
  };
}

/**
 * Role configuration
 */
export interface RoleMeta {
  type: string | null;
  traits: string[];
}

/**
 * Complete interview metadata
 */
export interface InterviewMeta<Fields extends string = string> {
  type: string;
  desc: string;
  roles: {
    alice: RoleMeta;
    bob: RoleMeta;
    [key: string]: RoleMeta;
  };
  fields: Record<Fields, FieldMeta>;
}

/**
 * Callable trait builder interface
 */
export interface TraitBuilder {
  (trait: string): any; // Returns RoleBuilder but avoiding circular dependency
}

/**
 * Callable cast builder interface with function overloads
 */
export interface CastBuilder<TParent> {
  // Overloads for different parameter combinations
  (): TParent; // No args (for optional sub-name casts)
  (promptOrSubName: string): TParent; // Single arg
  (subName: string, prompt: string): TParent; // Two args
  (...args: any[]): TParent; // Catch-all for flexibility
}

/**
 * Callable choice builder interface with function overloads
 */
export interface ChoiceBuilder<TParent> {
  (...choices: string[]): TParent; // Direct choices
  (subName: string, ...choices: string[]): TParent; // Sub-name + choices
}
