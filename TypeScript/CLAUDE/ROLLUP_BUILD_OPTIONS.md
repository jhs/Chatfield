# Rollup Build Options

This document describes the environment variables available to control which Rollup builds are generated.

## Overview

By default, all build variants are enabled. You can exclude specific builds using the `EXCLUDE_BUILDS` environment variable.

## Environment Variables

### EXCLUDE_BUILDS

A comma-separated list of build types to exclude from generation. If not set or empty, all builds are generated.

**Available build types:**
- `esm` - Unminified ESM build
- `esm-min` - Minified ESM build
- `umd` - Unminified UMD build
- `umd-min` - Minified UMD build

**Default:** Empty (all builds enabled)

### VARIANT

Required. Specifies which variant to build:
- `standalone` - All dependencies bundled
- `lean` - External LangChain dependencies

## Output Files

### Standalone Variant (VARIANT=standalone)
- `esm` → `dist/standalone/esm/index.js`
- `esm-min` → `dist/standalone/esm/index.min.js`
- `umd` → `dist/standalone/umd/chatfield.js`
- `umd-min` → `dist/standalone/umd/chatfield.min.js`

### Lean Variant (VARIANT=lean)
- `esm` → `dist/lean/esm/index.js`
- `esm-min` → `dist/lean/esm/index.min.js`
- `umd` → `dist/lean/umd/chatfield.js`
- `umd-min` → `dist/lean/umd/chatfield.min.js`

## Usage Examples

### Build all variants (default)

```bash
# Standalone - all builds
VARIANT=standalone rollup --config rollup.config.mjs

# Lean - all builds
VARIANT=lean rollup --config rollup.config.mjs
```

### Exclude minified versions (build only unminified)

```bash
# Standalone
EXCLUDE_BUILDS=esm-min,umd-min VARIANT=standalone rollup --config rollup.config.mjs

# Lean
EXCLUDE_BUILDS=esm-min,umd-min VARIANT=lean rollup --config rollup.config.mjs
```

### Exclude UMD builds (ESM only)

```bash
# Standalone
EXCLUDE_BUILDS=umd,umd-min VARIANT=standalone rollup --config rollup.config.mjs

# Lean
EXCLUDE_BUILDS=umd,umd-min VARIANT=lean rollup --config rollup.config.mjs
```

### Exclude unminified versions (build only minified)

```bash
# Standalone
EXCLUDE_BUILDS=esm,umd VARIANT=standalone rollup --config rollup.config.mjs

# Lean
EXCLUDE_BUILDS=esm,umd VARIANT=lean rollup --config rollup.config.mjs
```

### Build only one specific output

```bash
# Only standalone ESM (unminified) - exclude all others
EXCLUDE_BUILDS=esm-min,umd,umd-min VARIANT=standalone rollup --config rollup.config.mjs

# Only lean UMD minified - exclude all others
EXCLUDE_BUILDS=esm,esm-min,umd VARIANT=lean rollup --config rollup.config.mjs

# Only standalone UMD (both minified and unminified) - exclude ESM
EXCLUDE_BUILDS=esm,esm-min VARIANT=standalone rollup --config rollup.config.mjs
```

## NPM Scripts

The following npm scripts use these environment variables:

```bash
# Build all standalone variants (all 4 builds)
npm run build:browser:standalone

# Build all lean variants (all 4 builds)
npm run build:browser:lean

# Watch mode - builds only standalone ESM (unminified) for debugging
npm run build:browser:standalone:watch
```

The watch script is optimized for development and debugging downstream applications:
- Builds only `dist/standalone/esm/index.js` (1 target)
- Automatically rebuilds on file changes
- Faster rebuild times with minimal output

## Build Variants Explained

### Standalone vs Lean

- **Standalone**: Bundles all dependencies (LangChain, OpenAI, Zod, etc.) into the output. Larger file size but easier to use in browsers without a bundler.
- **Lean**: Keeps LangChain and related dependencies as external. Smaller file size but requires those dependencies to be available (e.g., via import maps or a bundler).

### ESM vs UMD

- **ESM** (ECMAScript Modules): Modern module format for browsers and bundlers. Use with `<script type="module">` or modern build tools.
- **UMD** (Universal Module Definition): Older format for CDN usage with `<script>` tags. Compatible with older browsers.

### Minified vs Unminified

- **Minified**: Compressed for production use. Smaller file size, harder to debug.
- **Unminified**: Full source with sourcemaps. Easier to debug, larger file size.

## Notes

- The `VARIANT` environment variable must be set to either `standalone` or `lean`
- All builds are enabled by default when `EXCLUDE_BUILDS` is not set or empty
- You can exclude any combination of `esm`, `esm-min`, `umd`, `umd-min` in a comma-separated list
- Build names are case-insensitive
- These environment variables are only used during build time, not at runtime
- Empty `EXCLUDE_BUILDS` is more self-documenting than specifying all builds explicitly
- The watch script (`build:browser:standalone:watch`) builds only one target for optimal rebuild performance
