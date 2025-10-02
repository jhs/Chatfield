/**
 * Template loader - exports appropriate implementation
 *
 * For Node.js builds: uses loader.node.ts (reads from filesystem)
 * For browser builds: Rollup aliases this to loader.browser.ts (bundled strings)
 */

export {
  getTemplate,
  getTemplatePartial,
  listTemplates,
  listTemplatePartials
} from './loader.node';
