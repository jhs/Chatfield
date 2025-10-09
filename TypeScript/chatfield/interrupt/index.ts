/**
 * Interrupt module exports - Node.js version by default
 *
 * For Node.js builds: uses interrupt.node.ts (wraps real LangGraph interrupt)
 * For browser builds: Rollup aliases this to interrupt.browser.ts (custom implementation)
 */

export { interrupt } from './interrupt.node';
