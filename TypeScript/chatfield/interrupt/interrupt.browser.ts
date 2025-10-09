/**
 * Browser-side interrupt implementation for LangGraph
 *
 * This custom implementation provides interrupt functionality for browser environments
 * where the standard LangGraph interrupt may not work properly. It uses the scratchpad
 * pattern to manage resume values without requiring persistent storage.
 */

import { RunnableConfig } from "@langchain/core/runnables";
import type { PendingWrite } from "@langchain/langgraph-checkpoint";
import { GraphInterrupt, GraphValueError } from '@langchain/langgraph/web';
// import { sha256 } from 'js-sha256';

/**
 * Browser-compatible interrupt function
 *
 * Interrupts execution and waits for resume value. Works by:
 * 1. Checking scratchpad for previous resume values
 * 2. If found, returns the value and continues
 * 3. If not found, throws GraphInterrupt to pause execution
 * 4. On resume, stores value in scratchpad for next run
 *
 * @param value - The value to pass to the interrupt (shown to user)
 * @param config - RunnableConfig with scratchpad in configurable
 * @returns The resume value provided when execution resumes
 */
export function interrupt<I = unknown, R = any>(value: I, config: RunnableConfig): R {
  // Internal config keys (not exported from web.ts)
  const CONFIG_KEY_CHECKPOINTER = "__pregel_checkpointer";
  const CONFIG_KEY_SCRATCHPAD = "__pregel_scratchpad";
  const CONFIG_KEY_SEND = "__pregel_send";
  const RESUME = "__resume__";

  if (!config?.configurable) {
    throw new Error(
      "Called browserInterrupt() without config. " +
      "Make sure your node function accepts config as the second parameter: " +
      "(state: State, config?: RunnableConfig) => {...}"
    );
  }

  const conf = config.configurable;

  // Check for checkpointer
  const checkpointer = conf[CONFIG_KEY_CHECKPOINTER];
  if (!checkpointer) {
    throw new GraphValueError(
      "No checkpointer set. Use MemorySaver: " +
      "graph.compile({ checkpointer: new MemorySaver() })"
    );
  }

  // Get scratchpad
  const scratchpad = conf[CONFIG_KEY_SCRATCHPAD];
  if (!scratchpad) {
    throw new Error("No scratchpad found in config");
  }

  // Track interrupt index
  scratchpad.interruptCounter += 1;
  const idx = scratchpad.interruptCounter;

  // Find previous resume values (from earlier runs)
  if (scratchpad.resume.length > 0 && idx < scratchpad.resume.length) {
    // Write resume array back to channel.
    const pendingWrites = [ [RESUME, scratchpad.resume] as PendingWrite ];
    conf[CONFIG_KEY_SEND]?.(pendingWrites);
    return scratchpad.resume[idx] as R;
  }

  if (scratchpad.nullResume === undefined) {
    // No resume value found; throw interrupt.
    const ns: string = conf.checkpoint_ns;
    const id = ns ? hash_namespace(ns) : undefined;
    throw new GraphInterrupt([{ id, value }]);
  }

  // Find current resume value from Command({ resume })
  if (scratchpad.resume.length !== idx) {
    throw new Error(`Resume length mismatch: ${scratchpad.resume.length} !== ${idx}`);
  }

  const val = scratchpad.consumeNullResume();
  scratchpad.resume.push(val);

  const pendingWrites = [ [RESUME, scratchpad.resume] as PendingWrite ];
  conf[CONFIG_KEY_SEND]?.(pendingWrites);

  return val as R;
}

/**
 * Hash a namespace string
 *
 * For now, this is a no-op that returns the namespace as-is.
 * Could be enhanced to use actual hashing (e.g., sha256) if needed.
 *
 * @param ns - The namespace string to hash
 * @returns The hashed (or pass-through) namespace
 */
function hash_namespace(ns: string): string {
  // For now, just return the namespace as-is.
  // const hash = sha256(ns);
  return ns;
}
