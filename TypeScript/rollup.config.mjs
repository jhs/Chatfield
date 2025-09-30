import typescript from '@rollup/plugin-typescript';
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import terser from '@rollup/plugin-terser';

const external = [
  '@langchain/core',
  '@langchain/langgraph',
  '@langchain/langgraph/web',
  '@langchain/openai',
  'openai',
  'zod',
  'uuid',
  'dotenv',
  'handlebars',
  'reflect-metadata',
  'react',
  'react-dom',
  'fs',
  'path'
];

const createPlugins = (outDir) => [
  resolve({
    browser: true,
    preferBuiltins: false,
    extensions: ['.ts', '.tsx', '.js', '.jsx']
  }),
  commonjs(),
  typescript({
    tsconfig: './tsconfig.json',
    declaration: false,
    declarationDir: undefined,
    outDir: outDir,
    compilerOptions: {
      module: 'esnext',
      declaration: false
    }
  })
];

export default [
  // ESM build for modern bundlers and browsers
  {
    input: 'chatfield/index.ts',
    output: {
      file: 'dist/esm/index.js',
      format: 'esm',
      sourcemap: true,
      exports: 'named'
    },
    external,
    plugins: createPlugins('dist/esm')
  },
  // Minified ESM build
  {
    input: 'chatfield/index.ts',
    output: {
      file: 'dist/esm/index.min.js',
      format: 'esm',
      sourcemap: true,
      exports: 'named'
    },
    external,
    plugins: [...createPlugins('dist/esm'), terser()]
  },
  // UMD build for CDN usage
  {
    input: 'chatfield/index.ts',
    output: {
      file: 'dist/umd/chatfield.js',
      format: 'umd',
      name: 'Chatfield',
      sourcemap: true,
      exports: 'named',
      globals: {
        '@langchain/core': 'LangChainCore',
        '@langchain/langgraph': 'LangGraph',
        '@langchain/langgraph/web': 'LangGraphWeb',
        '@langchain/openai': 'LangChainOpenAI',
        'openai': 'OpenAI',
        'zod': 'Zod',
        'uuid': 'UUID',
        'react': 'React',
        'react-dom': 'ReactDOM',
        'handlebars': 'Handlebars',
        'fs': 'fs',
        'path': 'path'
      }
    },
    external,
    plugins: createPlugins('dist/umd')
  },
  // Minified UMD build
  {
    input: 'chatfield/index.ts',
    output: {
      file: 'dist/umd/chatfield.min.js',
      format: 'umd',
      name: 'Chatfield',
      sourcemap: true,
      exports: 'named',
      globals: {
        '@langchain/core': 'LangChainCore',
        '@langchain/langgraph': 'LangGraph',
        '@langchain/langgraph/web': 'LangGraphWeb',
        '@langchain/openai': 'LangChainOpenAI',
        'openai': 'OpenAI',
        'zod': 'Zod',
        'uuid': 'UUID',
        'react': 'React',
        'react-dom': 'ReactDOM',
        'handlebars': 'Handlebars',
        'fs': 'fs',
        'path': 'path'
      }
    },
    external,
    plugins: [...createPlugins('dist/umd'), terser()]
  }
];