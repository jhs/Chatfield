# Agent Documentation

This document explains the Agent Documentation system used in the Chatfield project and how to maintain it.

## What is Agent Documentation?

**Agent Documentation** refers to markdown files specifically designed to be read and understood by AI coding agents (like Claude Code, GitHub Copilot, Cursor, etc.) when they work with this codebase. These files use uppercase naming conventions to distinguish them from user-facing documentation.

The primary purpose is to provide AI agents with comprehensive, contextual information about:
- Project structure and architecture
- Development guidelines and conventions
- Implementation-specific details
- Code organization and relationships
- Testing approaches and patterns

## Naming Convention

Agent Documentation uses specific naming conventions:

- ✅ `CLAUDE.md` - Agent documentation (top-level overview, UPPERCASE)
- ✅ `CLAUDE/` - Agent documentation subdirectories (UPPERCASE with underscores)
- ✅ `Documentation/` files - Agent documentation (Normal_Case, e.g., `Architecture.md`)
- ❌ `README.md` - User-facing documentation
- ❌ `Developers.md` - User-facing documentation

**Key Distinction**: Files in `CLAUDE/` subdirectories use ALL_CAPS_WITH_UNDERSCORES (e.g., `JS_CONVERSION_PLAN.md`), while files in the centralized `Documentation/` directory use Normal_Case (e.g., `Architecture.md`) to distinguish them as project-wide reference material rather than implementation-specific agent docs.

### Exceptions
- `README.md` files are **user-facing** despite uppercase naming (standard convention)
- User guides like `Developers.md` are **not** agent documentation

## Two-Tier Structure

Agent Documentation follows a two-tier hierarchy:

### Tier 1: Overview Files (CLAUDE.md)

**Purpose**: Provide high-level overview with references to detailed documentation

**Characteristics**:
- Named `CLAUDE.md`
- Located at key directory levels (root, implementation directories, subdirectories)
- Contains **overviews and references**, not extensive detail
- Acts as an entry point for agents to understand the area
- Points to both detailed agent docs and user-facing docs

**Example locations**:
```
./CLAUDE.md                              # Project overview
./Python/CLAUDE.md                       # Python implementation overview
./TypeScript/CLAUDE.md                   # TypeScript implementation overview
./Python/tests/CLAUDE.md                 # Python test suite overview
./TypeScript/tests/CLAUDE.md             # TypeScript test suite overview
./Python/examples/CLAUDE.md              # Python examples overview
./TypeScript/examples/CLAUDE.md          # TypeScript examples overview
./TypeScript/chatfield/integrations/CLAUDE.md  # Integrations overview
```

### Tier 2: Detailed Files (CLAUDE/ subdirectories)

**Purpose**: Provide comprehensive technical details on specific topics

**Characteristics**:
- Located in `CLAUDE/` subdirectories
- Named with UPPERCASE and underscores: `JS_CONVERSION_PLAN.md`, `PROXY_SETUP.md`
- Contains **detailed technical content** (hundreds of lines)
- **Must be referenced** by a parent `CLAUDE.md` file
- Organized by implementation or topic area

**Example locations**:
```
./TypeScript/CLAUDE/
├── JS_CONVERSION_PLAN.md         # Detailed TypeScript reimplementation plan
├── PROXY_SETUP.md                # Detailed LiteLLM proxy configuration
└── ROLLUP_BUILD_OPTIONS.md       # Detailed build configuration
```

## Documentation/ Directory Exception

The `Documentation/` directory contains **detailed agent documentation** but does **not** use the `CLAUDE/` subdirectory structure. This is an exception because:

1. The entire `Documentation/` directory is dedicated to project-wide reference material
2. Files in `Documentation/` use Normal_Case naming (e.g., `Architecture.md`) to distinguish from implementation-specific CLAUDE/ docs
3. It serves as the central repository for detailed technical documentation
4. It's referenced from all CLAUDE.md files across the project

**Documentation/ contents** (Normal_Case naming):
```
Documentation/
├── README.md                      # Documentation index (user-facing exception)
├── Isomorphic_Development.md      # Isomorphic development principles
├── Architecture.md                # System architecture details
├── Testing_Architecture.md        # Testing approach and structure
├── Builder_Api.md                 # Builder pattern API reference
├── Api_Configuration.md           # API and environment setup
├── Commands.md                    # Development commands reference
├── Project_Structure.md           # Project organization
├── Design_Decisions.md            # Key design decisions
├── Cookbook.md                    # Common patterns and recipes
├── Prompt_System.md               # LLM prompt engineering
└── Getting_Started_*.md           # Quickstart guides

Note: Documentation/ uses Normal_Case to distinguish from UPPERCASE CLAUDE/ subdirectories.
AGENT_DOCUMENTATION.md is in CLAUDE/ at the root level, not in Documentation/.
```

## Maintenance Guidelines

### 1. Creating New Agent Documentation

When creating new detailed documentation:

**Step 1**: Determine if it's agent documentation
- Is it for AI agents to understand the code? → Agent doc (UPPERCASE)
- Is it for human users/developers? → User doc (Mixed case)

**Step 2**: Choose the appropriate tier
- High-level overview? → Add to existing `CLAUDE.md` or create new one
- Detailed technical content? → Create in `CLAUDE/` subdirectory

**Step 3**: Create the file
```bash
# For detailed docs in implementation directories (Python/TypeScript)
mkdir -p TypeScript/CLAUDE
touch TypeScript/CLAUDE/NEW_TOPIC.md

# For project-wide detailed reference docs
touch Documentation/NEW_TOPIC.md

# For root-level agent documentation about the project itself
mkdir -p CLAUDE
touch CLAUDE/NEW_TOPIC.md
```

**Step 4**: Add reference in parent `CLAUDE.md`
```markdown
## Advanced Topics

- **New Topic**: [CLAUDE/NEW_TOPIC.md](CLAUDE/NEW_TOPIC.md) - Brief description
```

### 2. Updating Existing Agent Documentation

**When updating CLAUDE.md (Tier 1)**:
- Keep it concise - overviews only
- Add references to detailed docs, don't embed details
- Update cross-references when structure changes
- Maintain consistent section structure across implementations

**When updating detailed docs (Tier 2)**:
- Can be as comprehensive as needed
- Ensure parent CLAUDE.md references it
- Use clear headings and organization
- Include code examples where helpful

### 3. Moving Files Between Tiers

If a `CLAUDE.md` file becomes too detailed (>200 lines with extensive technical content):

```bash
# 1. Create CLAUDE/ subdirectory
mkdir -p SomeDirectory/CLAUDE/

# 2. Extract detailed sections to new files
# Move content from CLAUDE.md to CLAUDE/TOPIC.md

# 3. Update CLAUDE.md to reference the new files
# Add links in appropriate sections

# 4. Commit with descriptive message
git add SomeDirectory/CLAUDE/
git add SomeDirectory/CLAUDE.md
git commit -m "Refactor: Extract detailed content from CLAUDE.md to CLAUDE/ subdocs"
```

### 4. Validation Checklist

Before committing changes to Agent Documentation:

- [ ] All `CLAUDE.md` files are concise overviews with references
- [ ] All detailed docs in `CLAUDE/` subdirectories are referenced
- [ ] No orphaned files (every CLAUDE/ file is referenced somewhere)
- [ ] Cross-references are up to date (especially after moving files)
- [ ] Naming conventions followed (UPPERCASE for agent docs)
- [ ] User-facing docs (README.md, Developers.md) are not in CLAUDE/
- [ ] Documentation/ directory structure is maintained
- [ ] Isomorphic pairs (Python/TypeScript) have parallel structure

## File Organization Examples

### ✅ Correct Structure

```
Chatfield/                         # Project root
├── CLAUDE.md                      # Root overview
├── CLAUDE/                        # Root-level detailed agent docs
│   └── AGENT_DOCUMENTATION.md     # This file!
├── Documentation/                 # Project-wide reference (exception)
│   ├── Architecture.md
│   ├── Builder_Api.md
│   └── ...
├── Python/
│   ├── CLAUDE.md                  # Python overview
│   └── CLAUDE/                    # Python-specific details (if needed)
└── TypeScript/
    ├── CLAUDE.md                  # TypeScript overview
    ├── CLAUDE/                    # TypeScript-specific details
    │   ├── JS_CONVERSION_PLAN.md
    │   ├── PROXY_SETUP.md
    │   └── ROLLUP_BUILD_OPTIONS.md
    ├── README.md                  # User-facing (exception)
    └── chatfield/
        └── integrations/
            └── CLAUDE.md          # Integrations overview
```

### ❌ Incorrect Structure

```
TypeScript/
├── CLAUDE.md                      # Too detailed (500+ lines)
├── JS_CONVERSION_PLAN.md          # Should be in CLAUDE/
├── PROXY_SETUP.md                 # Should be in CLAUDE/
├── README.md
└── chatfield/
    └── integrations/
        └── CLAUDE/                # Has subdirectory but no overview CLAUDE.md
            └── DETAILS.md
```

## Common Patterns

### Pattern 1: Implementation-Specific Documentation

For Python and TypeScript implementations:

```
Python/
├── CLAUDE.md                      # Python overview
├── CLAUDE/                        # Python-specific details (if needed)
│   └── IMPLEMENTATION_NOTES.md
├── tests/
│   └── CLAUDE.md                  # Test suite overview
└── examples/
    └── CLAUDE.md                  # Examples overview

TypeScript/
├── CLAUDE.md                      # TypeScript overview
├── CLAUDE/                        # TypeScript-specific details
│   ├── JS_CONVERSION_PLAN.md
│   ├── PROXY_SETUP.md
│   └── ROLLUP_BUILD_OPTIONS.md
├── tests/
│   └── CLAUDE.md                  # Test suite overview (mirrors Python)
└── examples/
    └── CLAUDE.md                  # Examples overview (mirrors Python)
```

### Pattern 2: Subdirectory Documentation

For specialized subdirectories:

```
TypeScript/chatfield/integrations/
├── CLAUDE.md                      # Overview of integrations
├── CLAUDE/                        # Detailed integration docs (if needed)
│   ├── REACT_PATTERNS.md
│   └── COPILOTKIT_SETUP.md
├── react.ts
├── react-components.tsx
└── copilotkit.tsx
```

### Pattern 3: Cross-Referencing

Within `CLAUDE.md` files, reference other documentation:

```markdown
## Architecture

**See**: [../Documentation/Architecture.md](../Documentation/Architecture.md) for detailed architecture.

## Advanced Topics

- **Proxy Setup**: [CLAUDE/PROXY_SETUP.md](CLAUDE/PROXY_SETUP.md) - LiteLLM proxy configuration
- **Build Options**: [CLAUDE/ROLLUP_BUILD_OPTIONS.md](CLAUDE/ROLLUP_BUILD_OPTIONS.md) - Rollup configuration
```

## Benefits of This System

1. **Clear Separation**: AI agents vs. human users documentation
2. **Discoverability**: Top-level CLAUDE.md files act as entry points
3. **Scalability**: Detailed content in subdirectories keeps overviews clean
4. **Maintainability**: Two-tier structure prevents documentation sprawl
5. **Consistency**: Standard naming and structure across the project
6. **Navigation**: Agents can easily find relevant context
7. **Isomorphic**: Parallel structure in Python and TypeScript implementations

## Integration with Development Workflow

### For Contributors

When adding new features:
1. Update relevant `CLAUDE.md` files with overview changes
2. Create detailed docs in `CLAUDE/` if needed (>100 lines of technical detail)
3. Update cross-references in parent `CLAUDE.md`
4. Ensure isomorphic pairs (Python/TypeScript) have matching structure

### For Code Reviews

Reviewers should check:
- Agent documentation updated for new features
- References are correct and not broken
- Documentation follows the two-tier structure
- Isomorphic documentation maintained in both implementations

### For AI Agents

When working with this codebase:
1. Start with root `CLAUDE.md` for project overview
2. Navigate to implementation-specific `CLAUDE.md` (Python/ or TypeScript/)
3. Follow references to `CLAUDE/` subdirectories for details
4. Consult `Documentation/` for project-wide technical references
5. Check `tests/CLAUDE.md` for testing approach
6. Review `examples/CLAUDE.md` for usage patterns

## Related Documentation

- **Project Structure**: [../Documentation/Project_Structure.md](../Documentation/Project_Structure.md) - Overall project organization
- **Isomorphic Development**: [../Documentation/Isomorphic_Development.md](../Documentation/Isomorphic_Development.md) - Maintaining parallel implementations
- **Documentation Index**: [../Documentation/README.md](../Documentation/README.md) - All documentation files

## Questions and Clarifications

**Q: When should I use CLAUDE/ vs Documentation/?**
- Use `CLAUDE/` for **implementation-specific** detailed docs (Python-only, TypeScript-only)
- Use `Documentation/` for **project-wide** detailed docs (applies to both implementations)

**Q: Can CLAUDE.md files contain code examples?**
- Yes, but keep them brief and illustrative
- For extensive code examples, create a file in `CLAUDE/` or reference `examples/`

**Q: How long should a CLAUDE.md file be?**
- Aim for <200 lines
- If longer, consider extracting detailed sections to `CLAUDE/` subdirectory

**Q: Should test files have their own CLAUDE/ subdirectories?**
- Generally no - `tests/CLAUDE.md` should be comprehensive enough
- Exception: If test infrastructure is very complex and needs detailed documentation

**Q: What about temporary documentation files?**
- Temporary files (like `Tomorrow_Plan.md`) should **not** be in CLAUDE/
- Keep them at root level and remove when no longer needed
- Don't reference them from CLAUDE.md files
