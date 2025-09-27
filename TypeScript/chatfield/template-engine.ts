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
    // ===== Text Processing Helpers =====

    // Dedent helper - remove leading indentation from text blocks
    // Handlebars.registerHelper('dedent', (text: string) => {
    //   if (!text) return '';
    //   const lines = text.split('\n');
    //   const minIndent = lines
    //     .filter(line => line.trim().length > 0)
    //     .reduce((min, line) => {
    //       const match = line.match(/^(\s*)/);
    //       const indent = match && match[1] ? match[1].length : 0;
    //       return Math.min(min, indent);
    //     }, Infinity);

    //   return lines
    //     .map(line => line.slice(minIndent))
    //     .join('\n');
    // });

    // Indent helper - add consistent indentation to text blocks
    // Handlebars.registerHelper('indent', (level: number, text: string) => {
    //   if (!text) return '';
    //   const indent = ' '.repeat(level);
    //   return text
    //     .split('\n')
    //     .map(line => line ? indent + line : line)
    //     .join('\n');
    // });

    // Clean whitespace helper - removes excess whitespace while preserving structure
    // Handlebars.registerHelper('trim', function(options: any) {
    //   const content = options.fn(this);
    //   return content
    //     .replace(/^\s+|\s+$/g, '')  // Trim start and end
    //     .replace(/\n\s*\n\s*\n/g, '\n\n');  // Collapse multiple blank lines to max 2
    // });

    // ===== Markdown Formatting Helpers =====

    // Section header helper
    Handlebars.registerHelper('section', (title: string, level: number = 1) => {
      return '#'.repeat(Math.min(level, 6)) + ' ' + title;
    });

    // Bullet point helper with optional indentation
    Handlebars.registerHelper('bullet', (text: string, indent: number = 0) => {
      return ' '.repeat(indent * 2) + '- ' + text;
    });

    // ===== List Helpers =====

    // Join helper - join list items with separator
    // Handlebars.registerHelper('join', (items: any[], separator = ', ') => {
    //   if (!items || !Array.isArray(items)) return '';
    //   return items.map(item => String(item)).join(separator);
    // });

    // List join with proper English grammar (commas and 'and')
    // Handlebars.registerHelper('listJoin', (items: string[], separator: string = ', ', lastSeparator: string = ' and ') => {
    //   if (!items || items.length === 0) return '';
    //   if (items.length === 1) return items[0];
    //   if (items.length === 2) return items.join(lastSeparator);
    //   return items.slice(0, -1).join(separator) + lastSeparator + items[items.length - 1];
    // });

    // ===== Conditional Logic Helpers =====

    // Simple conditional content helper
    // Handlebars.registerHelper('when', (condition: boolean, content: string) => {
    //   return condition ? content : '';
    // });

    // Check if any of the conditions are true
    // Handlebars.registerHelper('ifAny', function(this: any, ...args: any[]) {
    //   const options = args[args.length - 1];
    //   const conditions = args.slice(0, -1);
    //   return conditions.some(c => c) ? options.fn(this) : (options.inverse ? options.inverse(this) : '');
    // });

    // Check if all conditions are true
    // Handlebars.registerHelper('ifAll', function(this: any, ...args: any[]) {
    //   const options = args[args.length - 1];
    //   const conditions = args.slice(0, -1);
    //   return conditions.every(c => c) ? options.fn(this) : (options.inverse ? options.inverse(this) : '');
    // });

    // ===== Field Specification Helpers =====

    // Format field specifications (must, reject, hint)
    // Handlebars.registerHelper('fieldSpec', (field: any, specType: string, bobRoleName?: string) => {
    //   const specs = field.specs?.[specType];
    //   if (!specs || !Array.isArray(specs) || specs.length === 0) return '';

    //   // Special handling for confidential
    //   if (specType === 'confidential' && field.specs?.confidential) {
    //     return `    - **Confidential**: Do not inquire about this explicitly nor bring it up yourself. Continue your normal behavior. However, if the ${bobRoleName || 'user'} ever volunteers or implies it, you must record this information.`;
    //   }

    //   const label = specType.charAt(0).toUpperCase() + specType.slice(1);
    //   return specs.map((rule: string) => `    - ${label}: ${rule}`).join('\n');
    // });

    // Format all field specs for a field
    // Handlebars.registerHelper('allFieldSpecs', function(this: any, field: any, bobRoleName?: string) {
    //   if (!field.specs) return '';

    //   const specs: string[] = [];

    //   // Handle confidential first (special case)
    //   if (field.specs.confidential) {
    //     specs.push(`    - **Confidential**: Do not inquire about this explicitly nor bring it up yourself. Continue your normal behavior. However, if the ${bobRoleName || 'user'} ever volunteers or implies it, you must record this information.`);
    //   }

    //   // Handle regular specs
    //   const specTypes = ['must', 'reject', 'hint'];
    //   for (const specType of specTypes) {
    //     const specRules = field.specs[specType];
    //     if (specRules && Array.isArray(specRules)) {
    //       const label = specType.charAt(0).toUpperCase() + specType.slice(1);
    //       for (const rule of specRules) {
    //         specs.push(`    - ${label}: ${rule}`);
    //       }
    //     }
    //   }

    //   return specs.join('\n');
    // });

    // ===== Block Helpers =====

    // Conditional section - only renders if content is non-empty
    // Handlebars.registerHelper('conditionalSection', function(this: any, title: string, level: number, options: any) {
    //   const content = options.fn(this).trim();
    //   if (!content) return '';

    //   const header = '#'.repeat(Math.min(level, 6)) + ' ' + title;
    //   return `${header}\n\n${content}\n`;
    // });

    // ===== String Helpers =====

    // Concatenate strings
    Handlebars.registerHelper('concat', (...args: any[]) => {
      // Remove last arg (Handlebars options object)
      return args.slice(0, -1).join('');
    });

    // ===== Debug Helper (for development) =====

    Handlebars.registerHelper('debug', function(this: any, value: any, label?: string) {
      const prefix = label ? `Debug [${label}]:` : 'Debug:';
      console.log(prefix, JSON.stringify(value, null, 2));
      return '';
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