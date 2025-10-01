// Stub for langsmith - no-op tracing in browser
// langsmith is only used for debugging/tracing, not core functionality

export const __version__ = '0.0.0-stub'

// No-op traceable decorator
export function traceable(fn) {
  return fn
}

// No-op client
export class Client {
  constructor() {}
}

// Export everything as no-ops
export default {
  __version__,
  traceable,
  Client
}
