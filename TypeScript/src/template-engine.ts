/**
 * Handlebars template engine for prompt generation.
 */

import * as fs from 'fs';
import * as path from 'path';
import * as Handlebars from 'handlebars';

export class TemplateEngine {
  private templatesDir: string;
  private templateCache: Map<string, HandlebarsTemplateDelegate> = new Map();
  private partialsCache: Map<string, HandlebarsTemplateDelegate> = new Map();

  /**
   * Initialize the template engine.
   * @param templatesDir Path to templates directory. Defaults to /Prompts at project root.
   */
  constructor(templatesDir?: string) {
    if (!templatesDir) {
      // Default to /Prompts directory at project root
      const projectRoot = path.join(__dirname, '..', '..');
      templatesDir = path.join(projectRoot, 'Prompts');
    }

    this.templatesDir = templatesDir;

    // Register custom helpers
    this.registerHelpers();

    // Load partials
    this.loadPartials();
  }

  /**
   * Register custom Handlebars helpers.
   */
  private registerHelpers(): void {
    // Dedent helper - remove leading indentation from text blocks
    Handlebars.registerHelper('dedent', (text: string) => {
      if (!text) return '';
      const lines = text.split('\n');
      const minIndent = lines
        .filter(line => line.trim().length > 0)
        .reduce((min, line) => {
          const match = line.match(/^(\s*)/);
          const indent = match && match[1] ? match[1].length : 0;
          return Math.min(min, indent);
        }, Infinity);

      return lines
        .map(line => line.slice(minIndent))
        .join('\n');
    });

    // Indent helper - add consistent indentation to text blocks
    Handlebars.registerHelper('indent', (level: number, text: string) => {
      if (!text) return '';
      const indent = ' '.repeat(level);
      return text
        .split('\n')
        .map(line => line ? indent + line : line)
        .join('\n');
    });

    // Join helper - join list items with separator
    Handlebars.registerHelper('join', (items: any[], separator = ', ') => {
      if (!items || !Array.isArray(items)) return '';
      return items.map(item => String(item)).join(separator);
    });
  }

  /**
   * Load all partial templates from partials directory.
   */
  private loadPartials(): void {
    const partialsDir = path.join(this.templatesDir, 'partials');

    if (!fs.existsSync(partialsDir)) {
      return;
    }

    const partialFiles = fs.readdirSync(partialsDir)
      .filter(file => file.endsWith('.hbs.txt'));

    for (const partialFile of partialFiles) {
      // Get partial name without extension
      const partialName = partialFile.replace('.hbs.txt', '');

      const partialPath = path.join(partialsDir, partialFile);
      const partialSource = fs.readFileSync(partialPath, 'utf-8');

      // Compile and register the partial
      const compiledPartial = Handlebars.compile(partialSource);
      this.partialsCache.set(partialName, compiledPartial);
      Handlebars.registerPartial(partialName, partialSource);
    }
  }

  /**
   * Load and compile a template file.
   * @param templateName Name of the template file (without extension)
   * @returns Compiled template function
   */
  private loadTemplate(templateName: string): HandlebarsTemplateDelegate {
    // Check cache first
    if (this.templateCache.has(templateName)) {
      return this.templateCache.get(templateName)!;
    }

    // Load template file
    const templatePath = path.join(this.templatesDir, `${templateName}.hbs.txt`);

    if (!fs.existsSync(templatePath)) {
      throw new Error(`Template not found: ${templatePath}`);
    }

    const templateSource = fs.readFileSync(templatePath, 'utf-8');

    // Compile and cache
    const template = Handlebars.compile(templateSource);
    this.templateCache.set(templateName, template);

    return template;
  }

  /**
   * Render a template with the given context.
   * @param templateName Name of the template to render
   * @param context Dictionary of variables to pass to the template
   * @returns Rendered template string
   */
  render(templateName: string, context: Record<string, any>): string {
    const template = this.loadTemplate(templateName);
    return template(context);
  }

  /**
   * Clear the template cache to force reloading on next use.
   */
  clearCache(): void {
    this.templateCache.clear();
    this.partialsCache.clear();

    // Re-register partials
    for (const [name] of this.partialsCache) {
      Handlebars.unregisterPartial(name);
    }

    this.loadPartials();
  }
}