/**
 * Core type definitions for Chatfield
 *
 * NOTE: This file is TypeScript-specific and an exception to the parallel
 * Python/TypeScript structure. Type definitions are handled differently
 * in Python (via type hints and runtime checks) while TypeScript requires
 * explicit type definitions for compile-time type safety.
 */

export interface FieldMetaOptions {
  name: string
  description: string
  mustRules?: string[]
  rejectRules?: string[]
  hint?: string
}

export interface InterviewSchema {
  fields: Record<string, {
    description: string
    must?: string[]
    reject?: string[]
    hint?: string
  }>
  userContext?: string[]
  agentContext?: string[]
  docstring?: string
}

export interface ConversationMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: Date
}

export interface ValidationResult {
  isValid: boolean
  feedback: string
}

export interface InterviewOptions {
  maxRetryAttempts?: number
}

export interface CollectedData {
  [fieldName: string]: string
}