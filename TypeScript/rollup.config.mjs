import typescript from '@rollup/plugin-typescript';
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import terser from '@rollup/plugin-terser';
// import nodePolyfills from 'rollup-plugin-polyfill-node';
import { fileURLToPath } from 'url';
import path from 'path';

import alias from '@rollup/plugin-alias';

import bundleTemplates from './rollup-plugin-bundle-templates.mjs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Dependencies that should ALWAYS be external (not bundled)
const alwaysExternal = [
  'react',
  'react-dom',
  'dotenv',
];

// Dependencies external only in "lean" variant
const conditionalExternal = [
  '@langchain/core',
  '@langchain/langgraph',
  '@langchain/langgraph/web',
  '@langchain/openai',

  'langsmith',
  'langsmith/run_trees',
  'langsmith/singletons/traceable',

  '@opentelemetry/api',  // Optional tracing
  '@opentelemetry/sdk-trace-base',
  '@opentelemetry/sdk-trace-node',
  '@opentelemetry/sdk-trace-web',
  '@opentelemetry/exporter-trace-otlp-http',

  'openai',
  'zod',
  'handlebars',
  'reflect-metadata',

  'zod-to-json-schema',
];

// Dependencies deliberately bundled in all cases.
// uuid - Small enough to just bundle.

const createPlugins = (outDir, _unusedOption = false) => {
  const plugins = [
    bundleTemplates(),

    alias({
      entries: [
        {
          find: './langgraph/langgraph.server',
          replacement: path.resolve(__dirname, 'chatfield', 'langgraph', 'langgraph.browser.ts'),
        },
        {
          find: './interrupt/interrupt.server',
          replacement: path.resolve(__dirname, 'chatfield', 'interrupt', 'interrupt.browser.ts'),
        },
      ],
    }),

    // TypeScript must come before resolve/commonjs to handle .ts files
    typescript({
      module: 'esnext',
      tsconfig: './tsconfig.rollup.json',
      declaration: true,
      declarationMap: true,
      declarationDir: outDir,
      outDir: outDir,
      exclude: [
        // 'node_modules/**',
        // 'dist/**',
        '**/*.test.ts',
        '**/*.spec.ts',
        'chatfield/integrations/react.ts',
        'chatfield/integrations/react-components.tsx',
        'chatfield/integrations/copilotkit.tsx',
        'examples/**/*.ts',
      ],
      // compilerOptions: {
      //   module: 'esnext',
      //   declaration: true,
      //   declarationMap: true
      // },
    }),

    resolve({
      browser: true,
      preferBuiltins: false,
      extensions: ['.ts', '.tsx', '.js', '.jsx']
    }),

    commonjs({
      // TODO: Should this always be in all cases?
      ignoreDynamicRequires: true
    }),
  ];

  // Add polyfills for bundled variant (browser compatibility)
  // if (_unusedOption) {
  //   plugins.unshift(nodePolyfills());
  // }

  return plugins;
};

// Warning handler to show all messages without truncation
const onwarn = (warning, warn) => {
  const squelch = true;
  const ok_packages = ['@langchain', 'langsmith', 'zod-to-json-schema', 'semver', 'zod'];

  if (warning.code === 'CIRCULAR_DEPENDENCY') {
    if (squelch) {
      for (const ok_pkg of ok_packages) {
        if (warning.message.includes(`node_modules/${ok_pkg}/`)) {
          return; // Squelch.
        }
      }
    }
    // console.warn(`Circular dependency: ${warning.message}`);
  }
  return warn(warning);
};

// Build configurations
const standaloneConfigs = [
  // ============================================================================
  // STANDALONE VARIANT (default "core") - All dependencies bundled
  // ============================================================================

  // ESM build for modern bundlers and browsers
  {
    input: 'chatfield/index.ts',
    output: {
      file: 'dist/standalone/esm/index.js',
      format: 'esm',
      sourcemap: true,
      exports: 'named'
    },
    external: alwaysExternal,
    plugins: createPlugins('dist/standalone/esm', true),
    onwarn,
  },

  // Minified ESM build
  // {
  //   input: 'chatfield/index.ts',
  //   output: {
  //     file: 'dist/standalone/esm/index.min.js',
  //     format: 'esm',
  //     sourcemap: true,
  //     exports: 'named'
  //   },
  //   external: alwaysExternal,
  //   plugins: [...createPlugins('dist/standalone/esm', true), terser()],
  //   onwarn,
  // },

  // UMD build for CDN usage
  // {
  //   input: 'chatfield/index.ts',
  //   output: {
  //     file: 'dist/standalone/umd/chatfield.js',
  //     format: 'umd',
  //     name: 'Chatfield',
  //     sourcemap: true,
  //     exports: 'named',
  //     globals: {
  //       'react': 'React',
  //       'react-dom': 'ReactDOM'
  //     }
  //   },
  //   external: alwaysExternal,
  //   plugins: createPlugins('dist/standalone/umd', true)
  // },

  // Minified UMD build
  // {
  //   input: 'chatfield/index.ts',
  //   output: {
  //     file: 'dist/standalone/umd/chatfield.min.js',
  //     format: 'umd',
  //     name: 'Chatfield',
  //     sourcemap: true,
  //     exports: 'named',
  //     globals: {
  //       'react': 'React',
  //       'react-dom': 'ReactDOM'
  //     }
  //   },
  //   external: alwaysExternal,
  //   plugins: [...createPlugins('dist/standalone/umd', true), terser()]
  // }
];

const leanConfigs = [
  // ============================================================================
  // LEAN VARIANT - External LangChain dependencies
  // ============================================================================

  // ESM build for modern bundlers and browsers
  {
    input: 'chatfield/index.ts',
    output: {
      file: 'dist/lean/esm/index.js',
      format: 'esm',
      sourcemap: true,
      exports: 'named'
    },

    external: [...alwaysExternal, ...conditionalExternal],

    // For lean build: make EVERYTHING from node_modules external
    // external: (id) => {
    //   console.log('External check for:', id)

    //   const allExternals = [...alwaysExternal, ...conditionalExternal];

    //   // If the ID is a member of allExternals, treat as external.
    //   if (allExternals.includes(id)) {
    //     console.log('  Confirmed external: ', id);
    //     return true;
    //   }

    //   // If the ID contains the string "langsmith", throw an error.
    //   if (id.includes('langsmith')) {
    //     throw new Error(`Saw "langsmith": ${id}`);
    //   }

    //   return false;
    // },

    plugins: createPlugins('dist/lean/esm', false),  // No polyfills for lean (uses import maps/bundler)
    onwarn
  },

  // // Minified ESM build
  // {
  //   input: 'chatfield/index.ts',
  //   output: {
  //     file: 'dist/lean/esm/index.min.js',
  //     format: 'esm',
  //     sourcemap: true,
  //     exports: 'named'
  //   },
  //   external: [...alwaysExternal, ...conditionalExternal],
  //   plugins: [...createPlugins('dist/lean/esm', false), terser()]
  // },
  // // UMD build for CDN usage
  // {
  //   input: 'chatfield/index.ts',
  //   output: {
  //     file: 'dist/lean/umd/chatfield.js',
  //     format: 'umd',
  //     name: 'Chatfield',
  //     sourcemap: true,
  //     exports: 'named',
  //     globals: {
  //       '@langchain/core': 'LangChainCore',
  //       '@langchain/langgraph': 'LangGraph',
  //       '@langchain/langgraph/web': 'LangGraphWeb',
  //       '@langchain/openai': 'LangChainOpenAI',
  //       'openai': 'OpenAI',
  //       'zod': 'Zod',
  //       'uuid': 'UUID',
  //       'react': 'React',
  //       'react-dom': 'ReactDOM',
  //       'handlebars': 'Handlebars'
  //     }
  //   },
  //   external: [...alwaysExternal, ...conditionalExternal],
  //   plugins: createPlugins('dist/lean/umd', false)
  // },
  // // Minified UMD build
  // {
  //   input: 'chatfield/index.ts',
  //   output: {
  //     file: 'dist/lean/umd/chatfield.min.js',
  //     format: 'umd',
  //     name: 'Chatfield',
  //     sourcemap: true,
  //     exports: 'named',
  //     globals: {
  //       '@langchain/core': 'LangChainCore',
  //       '@langchain/langgraph': 'LangGraph',
  //       '@langchain/langgraph/web': 'LangGraphWeb',
  //       '@langchain/openai': 'LangChainOpenAI',
  //       'openai': 'OpenAI',
  //       'zod': 'Zod',
  //       'uuid': 'UUID',
  //       'react': 'React',
  //       'react-dom': 'ReactDOM',
  //       'handlebars': 'Handlebars'
  //     }
  //   },
  //   external: [...alwaysExternal, ...conditionalExternal],
  //   plugins: [...createPlugins('dist/lean/umd', false), terser()]
  // }
];

// Export the appropriate config based on VARIANT env variable.
let configs;
if (process.env.VARIANT === 'standalone') {
  configs = standaloneConfigs;
} else if (process.env.VARIANT === 'lean') {
  configs = leanConfigs;
} else {
  throw new Error(`Invalid VARIANT value: ${process.env.VARIANT}. Must be 'standalone' or 'lean'`);
}
export default configs;