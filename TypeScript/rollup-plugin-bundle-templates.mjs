/**
 * Rollup plugin to bundle Handlebars templates as TypeScript strings
 *
 * This plugin:
 * 1. Scans the /Prompts directory for .hbs.txt files
 * 2. Generates a loader.browser.ts file with templates as string literals
 * 3. Makes templates available to browser builds without fs/path dependencies
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default function bundleTemplates() {
  let sourceCodeTS = null;
  let sourceCodeJS = null;

  return {
    name: 'bundle-templates',

    buildStart() {
      // Path to Prompts directory (project root)
      const promptsDir = path.join(__dirname, '..', 'Prompts');
      const outputPathTS = path.join(__dirname, 'chatfield', 'templates', 'loader.browser.ts');
      const outputPathJS = path.join(__dirname, 'chatfield', 'templates', 'loader.browser.js');

      if (!fs.existsSync(promptsDir)) {
        this.warn(`Prompts directory not found at ${promptsDir}`);
        return;
      }

      // Read all template files
      const templates = {};
      const templateFiles = fs.readdirSync(promptsDir)
        .filter(file => file.endsWith('.hbs.txt'));

      for (const file of templateFiles) {
        const name = file.replace('.hbs.txt', '');
        const content = fs.readFileSync(path.join(promptsDir, file), 'utf-8');
        // Escape backticks and backslashes for template literal
        templates[name] = content
          .replace(/\\/g, '\\\\')
          .replace(/`/g, '\\`')
          .replace(/\$/g, '\\$');
      }

      // Read all partial files
      const partials = {};
      const partialsDir = path.join(promptsDir, 'partials');

      if (fs.existsSync(partialsDir)) {
        const partialFiles = fs.readdirSync(partialsDir)
          .filter(file => file.endsWith('.hbs.txt'));

        for (const file of partialFiles) {
          const name = file.replace('.hbs.txt', '');
          const content = fs.readFileSync(path.join(partialsDir, file), 'utf-8');
          // Escape backticks and backslashes for template literal
          partials[name] = content
            .replace(/\\/g, '\\\\')
            .replace(/`/g, '\\`')
            .replace(/\$/g, '\\$');
        }
      }

      sourceCodeTS = generateLoaderCode(templates, partials, true);
      sourceCodeJS = generateLoaderCode(templates, partials, false);

      fs.writeFileSync(outputPathTS, sourceCodeTS, 'utf-8');
      fs.writeFileSync(outputPathJS, sourceCodeJS, 'utf-8');

      console.log(`✓ Bundled ${Object.keys(templates).length} templates and ${Object.keys(partials).length} partials into loader.browser.ts`);
    },

    // load(id) {
    //   return null; // Return "file" content for the id string, or null to no-op.
    // },

    resolveId(source, importer) {
      if (source === './loader.node') {
        if (importer.endsWith('chatfield/templates/index.ts')) {
          const result = path.resolve(__dirname, 'chatfield', 'templates', 'loader.browser.js');
          return result;
        }
      }
      return null;
    },
  };
}

function toEntries(obj) {
  return Object.entries(obj)
    .map(([name, content]) => `  '${name}': \`${content}\``)
    .join(',\n');
}

function generateLoaderCode(templates, partials, withTypes = false) {
  const t = withTypes;
  const templateEntries = toEntries(templates);
  const partialEntries = toEntries(partials);

  return `// Generated file, do not edit manually!

const TEMPLATES${t ? ': Record<string, string>' : ''} = {
${templateEntries}
};

const PARTIALS${t ? ': Record<string, string>' : ''} = {
${partialEntries}
};

export function getTemplate(name${t ? ': string' : ''})${t ? ': string' : ''} {
  const template = TEMPLATES[name];
  if (!template) {
    throw new Error(\`Template not found: \${name}\`);
  }
  return template;
}

export function getTemplatePartial(name${t ? ': string' : ''})${t ? ': string' : ''} {
  const partial = PARTIALS[name];
  if (!partial) {
    throw new Error(\`Template partial not found: \${name}\`);
  }
  return partial;
}

export function listTemplates()${t ? ': string[]' : ''} {
  return Object.keys(TEMPLATES);
}

export function listTemplatePartials()${t ? ': string[]' : ''} {
  return Object.keys(PARTIALS);
}
`;
}