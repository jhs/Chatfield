/**
 * Node.js interrupt implementation - wraps the real LangGraph interrupt
 *
 * This is a shim that wraps the actual interrupt function from @langchain/langgraph.
 * It accepts the same signature as the browser version (value, config) but only
 * passes the value to the underlying interrupt, since the Node version doesn't
 * need the config parameter.
 */

import { interrupt as langgraphInterrupt } from '@langchain/langgraph';
import { RunnableConfig } from '@langchain/core/runnables';

/**
 * Node.js interrupt function - wraps LangGraph's built-in interrupt
 *
 * Accepts both value and config parameters for API compatibility with browser version,
 * but only passes the value to the underlying LangGraph interrupt function.
 *
 * @param value - The value to pass to the interrupt
 * @param config - RunnableConfig (accepted for compatibility, not used)
 * @returns The resume value when execution continues
 */
export function interrupt<I = unknown, R = any>(value: I, config: RunnableConfig): R {
  // The Node version of interrupt from langgraph only takes the value parameter
  // We accept config for API compatibility but don't use it
  return langgraphInterrupt(value) as R;
}
