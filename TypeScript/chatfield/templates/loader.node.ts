/**
 * Node.js template loader - reads templates from filesystem
 *
 * TODO:
 * Three options for "upgrading" this:
 * 1. Could this just re-export fs and path?  Then for the browser, at build time actually run fs.readDirSync, readFileSync, etc.
 *    for all the known paths that will be passed in.  Then those values are all placed into the loader.browser.ts as return values.
 *    (It can throw for an unknown file path or any other unexpected paremeter).
 * 2. Use an open source handlebars plugin for rollup, e.g. https://github.com/mixmaxhq/rollup-plugin-handlebars-plus
 * 3. See about *compiling* the templates at *build* time and then shipping those functions, the goal is make Handlebars
 *    a dev dependency only, not needed or referenced in the rollup builds nor at runtime. I think handlebars compiles templates
 *    to JS functions, so those need to serialize out somehow. (Could this make things harder to debug though?)
 */
import * as fs from 'fs';
import * as path from 'path';

// Path to Prompts directory (at project root, one level up from TypeScript/)
const PROMPTS_DIR = path.join(__dirname, '..', '..', '..', 'Prompts');

/**
 * Get a template by name
 * @param name Template name (without .hbs.txt extension)
 * @returns Template content as string
 */
export function getTemplate(name: string): string {
  const templatePath = path.join(PROMPTS_DIR, `${name}.hbs.txt`);

  if (!fs.existsSync(templatePath)) {
    throw new Error(`Template not found: ${templatePath}`);
  }

  return fs.readFileSync(templatePath, 'utf-8');
}

/**
 * Get a template partial by name
 * @param name Partial name (without .hbs.txt extension)
 * @returns Partial content as string
 */
export function getTemplatePartial(name: string): string {
  const partialPath = path.join(PROMPTS_DIR, 'partials', `${name}.hbs.txt`);

  if (!fs.existsSync(partialPath)) {
    throw new Error(`Template partial not found: ${partialPath}`);
  }

  return fs.readFileSync(partialPath, 'utf-8');
}

/**
 * List all available templates
 * @returns Array of template names (without extensions)
 */
export function listTemplates(): string[] {
  if (!fs.existsSync(PROMPTS_DIR)) {
    return [];
  }

  return fs
    .readdirSync(PROMPTS_DIR)
    .filter((file) => file.endsWith('.hbs.txt'))
    .map((file) => file.replace('.hbs.txt', ''));
}

/**
 * List all available template partials
 * @returns Array of partial names (without extensions)
 */
export function listTemplatePartials(): string[] {
  const partialsDir = path.join(PROMPTS_DIR, 'partials');

  if (!fs.existsSync(partialsDir)) {
    return [];
  }

  return fs
    .readdirSync(partialsDir)
    .filter((file) => file.endsWith('.hbs.txt'))
    .map((file) => file.replace('.hbs.txt', ''));
}
