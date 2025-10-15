/**
 * React hook for Chatfield conversational data collection
 */

import { useState, useEffect, useRef, useCallback } from 'react'
// Isomorphic: TypeScript imports from @chatfield/core/lean (source),
// Python would import from chatfield package
import { Interview, Interviewer, FieldProxy } from '@chatfield/core/lean'

export interface UseChatfieldOptions {
  /**
   * Callback fired when a regular field (not Confidential, not Conclude) is collected.
   * Fires when field transitions from null to FieldProxy.
   */
  onField?: (fieldName: string, fieldProxy: FieldProxy) => void

  /**
   * Callback fired when a Confidential or Conclude field is collected.
   * Fires when field transitions from null to FieldProxy.
   */
  onConfidential?: (fieldName: string, fieldProxy: FieldProxy) => void

  /**
   * Callback fired when an error occurs during the conversation.
   */
  onError?: (error: Error) => void

  /**
   * Configuration options passed to Interviewer constructor
   */
  interviewerOptions?: {
    threadId?: string
    llm?: any
    llmId?: string
    temperature?: number | null
    baseUrl?: string
    apiKey?: string
    endpointSecurity?: 'strict' | 'warn' | 'disabled'
  }
}

export interface ChatfieldMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatfieldState {
  /**
   * Conversation messages (user and assistant only, no system/tool messages)
   */
  messages: ChatfieldMessage[]

  /**
   * True when ready for user input (after interrupt/go() returns)
   */
  isReadyForInput: boolean

  /**
   * Direct access to Interview instance for checking _done, accessing fields, etc.
   */
  interview: Interview
}

export interface ChatfieldActions {
  /**
   * Send a user message and process the next conversation turn
   */
  send: (message: string) => Promise<void>
}

/**
 * React hook for managing Chatfield conversational interviews
 *
 * @example
 * ```typescript
 * const interview = chatfield()
 *   .field('name')
    .desc('Your name')
 *   .field('age')
    .desc('Your age').asInt()
 *   .build()
 *
 * function MyForm() {
 *   const [state, actions] = useChatfield(interview, {
 *     onField: (fieldName, value) => {
 *       console.log(`Collected ${fieldName}:`, value)
 *     }
 *   })
 *
 *   if (state.interview._done) {
 *     return <div>Complete!</div>
 *   }
 *
 *   return (
 *     <div>
 *       {state.messages.map((msg, i) => (
 *         <div key={i}>{msg.content}</div>
 *       ))}
 *       <input
 *         disabled={!state.isReadyForInput}
 *         onKeyPress={(e) => {
 *           if (e.key === 'Enter') {
 *             actions.send(e.target.value)
 *           }
 *         }}
 *       />
 *     </div>
 *   )
 * }
 * ```
 */
export function useChatfield(
  interview: Interview,
  options: UseChatfieldOptions = {}
): [ChatfieldState, ChatfieldActions] {
  const { onField, onConfidential, onError, interviewerOptions } = options

  // Initialize interviewer once
  const interviewerRef = useRef<Interviewer | null>(null)
  const initializedRef = useRef(false)

  // Track which fields have fired callbacks (memoization)
  const firedFieldsRef = useRef<Set<string>>(new Set())

  // State
  const [messages, setMessages] = useState<ChatfieldMessage[]>([])
  const [isReadyForInput, setIsReadyForInput] = useState(false)
  const [interviewState, setInterviewState] = useState<Interview>(interview)

  // Initialize interviewer and start conversation
  useEffect(() => {
    if (initializedRef.current) return
    initializedRef.current = true

    const startConversation = async () => {
      try {
        // Create interviewer instance
        const interviewer = new Interviewer(interview, interviewerOptions)
        interviewerRef.current = interviewer

        // Start conversation (first .go() call with no input)
        const aiMessage = await interviewer.go()

        // Add AI message and mark ready for input
        setMessages([{ role: 'assistant', content: aiMessage }])
        setIsReadyForInput(true)
        setInterviewState(interview)

      } catch (error) {
        console.error('Chatfield conversation error:', error)
        onError?.(error as Error)
      }
    }

    startConversation()
  }, [interview, interviewerOptions, onError])

  // Check for newly collected fields and fire callbacks
  const checkFieldCallbacks = useCallback(() => {
    if (!interviewState) return

    const fields = interviewState._chatfield.fields

    for (const [fieldName, chatfield] of Object.entries(fields)) {
      // Skip if already fired
      if (firedFieldsRef.current.has(fieldName)) {
        continue
      }

      // Check if field has transitioned from null to FieldProxy
      const fieldValue = (interviewState as any)[fieldName]
      if (fieldValue !== null && fieldValue !== undefined) {
        // Mark as fired
        firedFieldsRef.current.add(fieldName)

        // Determine if Confidential or Conclude
        const isConfidential = chatfield.specs?.confidential === true
        const isConclude = chatfield.specs?.conclude === true

        if (isConfidential || isConclude) {
          onConfidential?.(fieldName, fieldValue as FieldProxy)
        } else {
          onField?.(fieldName, fieldValue as FieldProxy)
        }
      }
    }
  }, [interviewState, onField, onConfidential])

  // Check callbacks whenever interview state updates
  useEffect(() => {
    checkFieldCallbacks()
  }, [interviewState, checkFieldCallbacks])

  // Send user message
  const send = useCallback(async (message: string) => {
    if (!interviewerRef.current || !isReadyForInput) {
      console.warn('Cannot send message: interviewer not ready')
      return
    }

    try {
      // Add user message immediately
      setMessages(prev => [...prev, { role: 'user', content: message }])
      setIsReadyForInput(false)

      // Process with interviewer
      const aiMessage = await interviewerRef.current.go(message)

      // Add AI message and mark ready again
      setMessages(prev => [...prev, { role: 'assistant', content: aiMessage }])
      setIsReadyForInput(true)

      // Update interview state to trigger field callbacks
      setInterviewState(interview)

    } catch (error) {
      console.error('Chatfield send error:', error)
      setIsReadyForInput(true) // Re-enable input on error
      onError?.(error as Error)
    }
  }, [isReadyForInput, interview, onError])

  const state: ChatfieldState = {
    messages,
    isReadyForInput,
    interview: interviewState
  }

  const actions: ChatfieldActions = {
    send
  }

  return [state, actions]
}
