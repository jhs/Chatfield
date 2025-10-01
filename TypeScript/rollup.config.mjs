import typescript from '@rollup/plugin-typescript';
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import terser from '@rollup/plugin-terser';
import nodePolyfills from 'rollup-plugin-polyfill-node';

// Dependencies that should ALWAYS be external (not bundled)
const alwaysExternal = [
  'react',
  'react-dom',
  'dotenv',
  'langsmith',  // LangChain tracing (dev/debugging only)
  '@opentelemetry/api',  // Optional tracing
  '@opentelemetry/sdk-trace-base',
  '@opentelemetry/sdk-trace-node',
  '@opentelemetry/sdk-trace-web',
  '@opentelemetry/exporter-trace-otlp-http',
  'fs',  // Node.js only - cannot polyfill for browser
  'path'  // Node.js only - cannot polyfill for browser
];

// Dependencies to bundle in "core" variant, external in "lean" variant
const conditionalExternal = [
  '@langchain/core',
  '@langchain/langgraph',
  '@langchain/langgraph/web',
  '@langchain/openai',
  'openai',
  'zod',
  'uuid',
  'handlebars',
  'reflect-metadata'
];

const createPlugins = (outDir, includeBundled = false) => {
  const plugins = [
    resolve({
      browser: true,
      preferBuiltins: false,
      extensions: ['.ts', '.tsx', '.js', '.jsx']
    }),
    commonjs({
      ignoreDynamicRequires: true
    }),
    typescript({
      tsconfig: './tsconfig.json',
      declaration: false,
      declarationDir: undefined,
      outDir: outDir,
      exclude: [
        '**/*.test.ts',
        '**/*.spec.ts',
        'chatfield/integrations/react.ts',
        'chatfield/integrations/react-components.tsx',
        'chatfield/integrations/copilotkit.tsx'
      ],
      compilerOptions: {
        // module: 'esnext',
        declaration: false
      }
    })
  ];

  // Add polyfills for bundled variant (browser compatibility)
  if (includeBundled) {
    plugins.unshift(nodePolyfills());
  }

  return plugins;
};

// Warning handler to show all messages without truncation
const onwarn = (warning, warn) => {
  // Always show the full warning message
  if (warning.code === 'CIRCULAR_DEPENDENCY') {
    console.warn(`Circular dependency: ${warning.message}`);
  } else {
    warn(warning);
  }
};

// Build configurations
const bundledConfigs = [
  // ============================================================================
  // BUNDLED VARIANT (default "core") - All dependencies bundled
  // ============================================================================

  // ESM build for modern bundlers and browsers
  {
    input: 'chatfield/index.ts',
    output: {
      file: 'dist/bundled/esm/index.js',
      format: 'esm',
      sourcemap: true,
      exports: 'named'
    },
    external: alwaysExternal,
    plugins: createPlugins('dist/bundled/esm', true),
    onwarn
  },

  // Minified ESM build
  // {
  //   input: 'chatfield/index.ts',
  //   output: {
  //     file: 'dist/bundled/esm/index.min.js',
  //     format: 'esm',
  //     sourcemap: true,
  //     exports: 'named'
  //   },
  //   external: alwaysExternal,
  //   plugins: [...createPlugins('dist/bundled/esm', true), terser()]
  // },

  // UMD build for CDN usage
  // {
  //   input: 'chatfield/index.ts',
  //   output: {
  //     file: 'dist/bundled/umd/chatfield.js',
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
  //   plugins: createPlugins('dist/bundled/umd', true)
  // },

  // Minified UMD build
  // {
  //   input: 'chatfield/index.ts',
  //   output: {
  //     file: 'dist/bundled/umd/chatfield.min.js',
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
  //   plugins: [...createPlugins('dist/bundled/umd', true), terser()]
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
    // For lean build: make EVERYTHING from node_modules external
    external: (id) => {
      // Keep our own code (non-node_modules)
      if (!id.includes('node_modules')) return false
      // Make everything in node_modules external
      return true
    },
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

// Export based on VARIANT environment variable
const variant = process.env.VARIANT;

export default variant === 'bundled'
  ? bundledConfigs
  : variant === 'lean'
    ? leanConfigs
    : [...bundledConfigs, ...leanConfigs];
