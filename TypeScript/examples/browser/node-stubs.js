// Stub implementations for Node.js modules in browser
// These will throw errors if actually used

const notAvailable = (module, method) => {
  throw new Error(`${module}.${method} is not available in browser environments`)
}

// fs stub
export const existsSync = () => notAvailable('fs', 'existsSync')
export const readdirSync = () => notAvailable('fs', 'readdirSync')
export const readFileSync = () => notAvailable('fs', 'readFileSync')
export const writeFileSync = () => notAvailable('fs', 'writeFileSync')

// path stub
export const join = (...args) => args.join('/')
export const dirname = (p) => p.split('/').slice(0, -1).join('/')
export const basename = (p) => p.split('/').pop()
export const resolve = (...args) => args.join('/')

export default {
  existsSync,
  readdirSync,
  readFileSync,
  writeFileSync,
  join,
  dirname,
  basename,
  resolve
}
