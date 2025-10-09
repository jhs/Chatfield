/**
 * Rollup plugin to alias Node.js modules to browser versions
 *
 * This plugin redirects imports for browser builds:
 * 1. ./interrupt/interrupt.node -> ./interrupt/interrupt.browser
 * 2. ./langgraph/index.node -> ./langgraph/index.browser
 *
 * This allows code to import from the default (Node) version, and Rollup
 * automatically substitutes the browser version when building for the browser.
 */

import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default function browserNodeAlias() {
  return {
    name: 'browser-node-alias',

    resolveId(source, importer) {
      // Only process if there's an importer (not the entry point)
      if (!importer) {
        return null;
      }

      // Handle interrupt module aliasing
      if (source === './interrupt.node') {
        if (importer.endsWith('chatfield/interrupt/index.ts')) {
          const result = path.resolve(__dirname, 'chatfield', 'interrupt', 'interrupt.browser.js');
          return result;
        }
      }

      // Handle langgraph module aliasing
      if (source === './index.node') {
        if (importer.endsWith('chatfield/langgraph/index.ts')) {
          const result = path.resolve(__dirname, 'chatfield', 'langgraph', 'index.browser.js');
          return result;
        }
      }

      return null;
    },
  };
}
