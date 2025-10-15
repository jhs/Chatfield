/**
 * @chatfield/react - React hooks for Chatfield conversational data collection
 *
 * @example
 * ```typescript
 * import { useChatfield } from '@chatfield/react'
 * import { chatfield } from '@chatfield/core'
 *
 * const interview = chatfield()
 *   .field('name')
    .desc('Your name')
 *   .build()
 *
 * function MyComponent() {
 *   const [state, actions] = useChatfield(interview)
 *   // ... use state.messages, actions.send(), etc.
 * }
 * ```
 */

export {
  useChatfield,
  type UseChatfieldOptions,
  type ChatfieldMessage,
  type ChatfieldState,
  type ChatfieldActions
} from './useChatfield'
