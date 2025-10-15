# Isomorphic Development in Chatfield

**CRITICAL: Chatfield is an isomorphic library—both Python and TypeScript implementations are treated as equal first-class implementations.** This is a fundamental design principle that permeates every aspect of the project.

## What "Isomorphic" Means in Chatfield

1. **Identical Concepts**: Both languages implement identical concepts, architecture, and patterns
2. **Near-Identical Code**: Code structure, naming, and logic are nearly identical across languages
3. **Documented Deviations**: Language-specific differences are explicitly documented with "Isomorphic:" comments
4. **Identical Test Suites**: Test files, test names, test descriptions, and test counts are identical
5. **Zero Skipped Tests**: Both implementations maintain identical test counts with zero skipped tests
6. **Shared Documentation**: Both implementations share consistent documentation patterns

## The "Isomorphic:" Comment Pattern

When code must differ between Python and TypeScript due to language-specific requirements, both implementations MUST include an identical "Isomorphic:" comment explaining the difference:

```python
# Python example
def some_method(self):
    # Isomorphic: Python uses snake_case for method names, TypeScript uses camelCase.
    # Both implementations have identical logic and behavior.
    return self._do_something()
```

```typescript
// TypeScript example
someMethod() {
  // Isomorphic: Python uses snake_case for method names, TypeScript uses camelCase.
  // Both implementations have identical logic and behavior.
  return this._doSomething()
}
```

**Key Rules**:
- Both languages MUST contain the identical "Isomorphic:" comment
- The comment appears before the code that differs
- The comment explains WHY the code differs and confirms behavior is identical
- Without an "Isomorphic:" comment, code should be identical across languages

## Isomorphic Synchronization Requirements

**CRITICAL**: Both implementations follow these principles:
- **File names**: Match across languages (e.g., `interview.py` → `interview.ts`)
- **Class/function names**: Identical names (e.g., `Interview`, `Interviewer`, `FieldProxy`)
- **Method names**: Preserved across languages (e.g., `_name()`, `_pretty()`, `as_int`)
- **Logic**: Identical algorithms and control flow
- **Test structure**: Mirror each other (e.g., `test_builder.py` → `builder.test.ts`)
- **Test descriptions**: Match exactly between implementations
- **Test counts**: Identical (zero skipped tests)
- **Deviations**: Only for language-specific requirements (e.g., async/await, TypeScript types)
- **Documentation**: Use "Isomorphic:" comments in both languages for any differences
- **Test organization**: Both use BDD-style (pytest-describe in Python, nested describe/it in Jest)

## Benefits of Isomorphic Development

1. **Developer Confidence**: Identical behavior across languages builds trust
2. **Easy Context Switching**: Developers can work in either language seamlessly
3. **Feature Parity**: No language is second-class; both receive equal attention
4. **Reduced Bugs**: Differences are explicit and documented
5. **Better Collaboration**: Team members can review code in either language

## Examples

See the latest `interviewer.py` and `interviewer.ts` files for extensive examples of "Isomorphic:" comments documenting language-specific differences while maintaining conceptual identity.

## Contributing with Isomorphic Principles

1. **Isomorphic first**: Maintain the isomorphic principle—both implementations are equal first-class citizens
2. **Synchronize implementations**: Keep Python and TypeScript code structures, names, and logic identical
3. **Document deviations**: Use "Isomorphic:" comments in both languages for any necessary differences
4. **Test coverage**: Write tests for all new features using BDD style with identical structure
5. **Test naming**: Use identical test descriptions between Python and TypeScript
6. **No-skip policy**: NEVER skip tests - use no-op tests that pass to maintain identical test counts
7. **Parallel development**: Implement features in both languages simultaneously when possible
8. **Documentation**: Update CLAUDE.md files when adding features, maintaining consistency
9. **Examples**: Provide example usage for new functionality in both languages
