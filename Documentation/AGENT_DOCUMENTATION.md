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

- ✅ `CLAUDE.md` - Agent documentation (top-level overview files at directory levels, UPPERCASE)
- ✅ `Documentation/` files - All agent documentation (UPPERCASE for agent-focused, Normal_Case for human-focused)
- ❌ `README.md` - User-facing documentation (exception to UPPERCASE convention)
- ❌ `Developers.md` - User-facing documentation

**Key Distinction**: Files in the `Documentation/` directory use UPPERCASE_WITH_UNDERSCORES for agent-focused documentation (e.g., `AGENT_DOCUMENTATION.md`, `JS_CONVERSION_PLAN.md`) and Normal_Case for human-focused documentation (e.g., `Architecture.md`, `Getting_Started_Python.md`).

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

### Tier 2: Detailed Files (Documentation/ directory)

**Purpose**: Provide comprehensive technical details on specific topics

**Characteristics**:
- Located in the centralized `Documentation/` directory
- Agent-focused files use UPPERCASE and underscores: `JS_CONVERSION_PLAN.md`, `PROXY_SETUP.md`, `AGENT_DOCUMENTATION.md`
- Human-focused files use Normal_Case: `Architecture.md`, `Getting_Started_Python.md`
- Contains **detailed technical content** (hundreds of lines)
- **Must be referenced** by a parent `CLAUDE.md` file or other documentation
- Organized by topic area in a single centralized location

**Example locations**:
```
./Documentation/
├── AGENT_DOCUMENTATION.md        # Agent documentation system guide
├── JS_CONVERSION_PLAN.md         # Detailed TypeScript reimplementation plan
├── PROXY_SETUP.md                # Detailed LiteLLM proxy configuration
├── ROLLUP_BUILD_OPTIONS.md       # Detailed build configuration
├── Architecture.md               # System architecture (human-focused)
└── Getting_Started_Python.md     # Python quickstart (human-focused)
```

## Documentation/ Directory

The `Documentation/` directory is the **central location for all detailed documentation**, both agent-focused and human-focused:

1. The entire `Documentation/` directory serves as the centralized repository for all project-wide documentation
2. UPPERCASE files (e.g., `AGENT_DOCUMENTATION.md`, `JS_CONVERSION_PLAN.md`) are agent-focused
3. Normal_Case files (e.g., `Architecture.md`, `Getting_Started_Python.md`) are human-focused
4. It's referenced from all CLAUDE.md files across the project

**Documentation/ contents** (mixed naming conventions):
```
Documentation/
├── README.md                      # Documentation index (user-facing exception)
├── AGENT_DOCUMENTATION.md         # Agent documentation system guide (agent-focused)
├── JS_CONVERSION_PLAN.md          # TypeScript reimplementation plan (agent-focused)
├── PROXY_SETUP.md                 # LiteLLM proxy configuration (agent-focused)
├── ROLLUP_BUILD_OPTIONS.md        # Build configuration (agent-focused)
├── CONVERTING_WITH_SCREENSHOTS.md # Form conversion guide (agent-focused)
├── CLAUDE_SKILLS_BEST_PRACTICES.md # Skills authoring guide (agent-focused)
├── Isomorphic_Development.md      # Isomorphic development principles (human-focused)
├── Architecture.md                # System architecture details (human-focused)
├── TESTING_Architecture.md        # Testing approach and structure (human-focused)
├── Builder_Api.md                 # Builder pattern API reference (human-focused)
├── Api_Configuration.md           # API and environment setup (human-focused)
├── Commands.md                    # Development commands reference (human-focused)
├── Project_Structure.md           # Project organization (human-focused)
├── Design_Decisions.md            # Key design decisions (human-focused)
├── Cookbook.md                    # Common patterns and recipes (human-focused)
├── Prompt_System.md               # LLM prompt engineering (human-focused)
└── Getting_Started_*.md           # Quickstart guides (human-focused)

Note: UPPERCASE = agent-focused, Normal_Case = human-focused. All documentation is centralized in Documentation/.
```

## Maintenance Guidelines

### 1. Creating New Agent Documentation

When creating new detailed documentation:

**Step 1**: Determine if it's agent documentation
- Is it for AI agents to understand the code? → Agent doc (UPPERCASE)
- Is it for human users/developers? → User doc (Mixed case)

**Step 2**: Choose the appropriate tier
- High-level overview? → Add to existing `CLAUDE.md` or create new one
- Detailed technical content? → Create in `Documentation/` directory with appropriate naming

**Step 3**: Create the file
```bash
# For project-wide detailed documentation (both agent-focused and human-focused)
# Agent-focused: Use UPPERCASE_WITH_UNDERSCORES
touch Documentation/NEW_AGENT_TOPIC.md

# Human-focused: Use Normal_Case
touch Documentation/New_Human_Topic.md
```

**Step 4**: Add reference in parent `CLAUDE.md`
```markdown
## Advanced Topics

- **New Topic**: [Documentation/NEW_AGENT_TOPIC.md](Documentation/NEW_AGENT_TOPIC.md) - Brief description
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
# 1. Extract detailed sections to new files in Documentation/
# Use UPPERCASE for agent-focused content
touch Documentation/NEW_DETAILED_TOPIC.md

# 2. Move content from CLAUDE.md to Documentation/NEW_DETAILED_TOPIC.md

# 3. Update CLAUDE.md to reference the new files
# Add links in appropriate sections

# 4. Commit with descriptive message
git add Documentation/NEW_DETAILED_TOPIC.md
git add SomeDirectory/CLAUDE.md
git commit -m "Refactor: Extract detailed content from CLAUDE.md to Documentation/"
```

### 4. Validation Checklist

Before committing changes to Agent Documentation:

- [ ] All `CLAUDE.md` files are concise overviews with references
- [ ] All detailed docs in `Documentation/` directory are referenced
- [ ] No orphaned files (every Documentation/ file is referenced somewhere)
- [ ] Cross-references are up to date (especially after moving files)
- [ ] Naming conventions followed (UPPERCASE for agent-focused docs, Normal_Case for human-focused docs)
- [ ] User-facing docs (README.md, Developers.md) follow appropriate conventions
- [ ] Documentation/ directory structure is maintained with proper naming
- [ ] Isomorphic pairs (Python/TypeScript) have parallel structure

## File Organization Examples

### ✅ Correct Structure

```
Chatfield/                         # Project root
├── CLAUDE.md                      # Root overview
├── Documentation/                 # All detailed documentation (centralized)
│   ├── AGENT_DOCUMENTATION.md     # Agent-focused (UPPERCASE)
│   ├── JS_CONVERSION_PLAN.md      # Agent-focused (UPPERCASE)
│   ├── PROXY_SETUP.md             # Agent-focused (UPPERCASE)
│   ├── ROLLUP_BUILD_OPTIONS.md    # Agent-focused (UPPERCASE)
│   ├── Architecture.md            # Human-focused (Normal_Case)
│   ├── Builder_Api.md             # Human-focused (Normal_Case)
│   └── ...
├── Python/
│   ├── CLAUDE.md                  # Python overview
│   ├── README.md                  # User-facing (exception)
│   └── chatfield/
└── TypeScript/
    ├── CLAUDE.md                  # TypeScript overview
    ├── README.md                  # User-facing (exception)
    └── chatfield/
        └── integrations/
            └── CLAUDE.md          # Integrations overview
```

### ❌ Incorrect Structure

```
TypeScript/
├── CLAUDE.md                      # Too detailed (500+ lines)
├── JS_CONVERSION_PLAN.md          # Should be in Documentation/
├── PROXY_SETUP.md                 # Should be in Documentation/
├── README.md
└── chatfield/
    └── integrations/
        ├── DETAILS.md             # Should be in Documentation/ or referenced in CLAUDE.md
        └── (no CLAUDE.md)         # Missing overview file
```

## Common Patterns

### Pattern 1: Implementation-Specific Documentation

For Python and TypeScript implementations:

```
Python/
├── CLAUDE.md                      # Python overview
├── tests/
│   └── CLAUDE.md                  # Test suite overview
└── examples/
    └── CLAUDE.md                  # Examples overview

TypeScript/
├── CLAUDE.md                      # TypeScript overview
├── tests/
│   └── CLAUDE.md                  # Test suite overview (mirrors Python)
└── examples/
    └── CLAUDE.md                  # Examples overview (mirrors Python)

Documentation/                     # Centralized detailed docs
├── JS_CONVERSION_PLAN.md          # TypeScript-specific (agent-focused)
├── PROXY_SETUP.md                 # TypeScript-specific (agent-focused)
└── ROLLUP_BUILD_OPTIONS.md        # TypeScript-specific (agent-focused)
```

### Pattern 2: Subdirectory Documentation

For specialized subdirectories:

```
TypeScript/chatfield/integrations/
├── CLAUDE.md                      # Overview of integrations
├── react.ts
├── react-components.tsx
└── copilotkit.tsx

Documentation/                     # Detailed integration docs (if needed)
├── REACT_PATTERNS.md              # Detailed React patterns (agent-focused)
└── COPILOTKIT_SETUP.md            # Detailed CopilotKit setup (agent-focused)
```

### Pattern 3: Cross-Referencing

Within `CLAUDE.md` files, reference other documentation:

```markdown
## Architecture

**See**: [../Documentation/Architecture.md](../Documentation/Architecture.md) for detailed architecture.

## Advanced Topics

- **Proxy Setup**: [../Documentation/PROXY_SETUP.md](../Documentation/PROXY_SETUP.md) - LiteLLM proxy configuration
- **Build Options**: [../Documentation/ROLLUP_BUILD_OPTIONS.md](../Documentation/ROLLUP_BUILD_OPTIONS.md) - Rollup configuration
- **JS Conversion**: [../Documentation/JS_CONVERSION_PLAN.md](../Documentation/JS_CONVERSION_PLAN.md) - TypeScript reimplementation plan
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
2. Create detailed docs in `Documentation/` if needed (>100 lines of technical detail, use UPPERCASE for agent-focused)
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
3. Follow references to `Documentation/` directory for detailed documentation
4. Consult `Documentation/` for both agent-focused (UPPERCASE) and human-focused (Normal_Case) documentation
5. Check `tests/CLAUDE.md` for testing approach
6. Review `examples/CLAUDE.md` for usage patterns

## Related Documentation

- **Project Structure**: [../Documentation/Project_Structure.md](../Documentation/Project_Structure.md) - Overall project organization
- **Isomorphic Development**: [../Documentation/Isomorphic_Development.md](../Documentation/Isomorphic_Development.md) - Maintaining parallel implementations
- **Documentation Index**: [../Documentation/README.md](../Documentation/README.md) - All documentation files

## Questions and Clarifications

**Q: When should I use UPPERCASE vs Normal_Case in Documentation/?**
- Use `UPPERCASE_WITH_UNDERSCORES` for **agent-focused** documentation (e.g., `AGENT_DOCUMENTATION.md`, `JS_CONVERSION_PLAN.md`)
- Use `Normal_Case` for **human-focused** documentation (e.g., `Architecture.md`, `Getting_Started_Python.md`)

**Q: Can CLAUDE.md files contain code examples?**
- Yes, but keep them brief and illustrative
- For extensive code examples, create a file in `Documentation/` (using UPPERCASE) or reference `examples/`

**Q: How long should a CLAUDE.md file be?**
- Aim for <200 lines
- If longer, consider extracting detailed sections to `Documentation/` directory with UPPERCASE naming

**Q: Should test files have their own detailed documentation in Documentation/?**
- Generally no - `tests/CLAUDE.md` should be comprehensive enough
- Exception: If test infrastructure is very complex, create `Documentation/TESTING_DETAILS.md` with UPPERCASE naming

**Q: What about temporary documentation files?**
- Temporary files (like `Tomorrow_Plan.md`) should **not** be in `Documentation/`
- Keep them at root level and remove when no longer needed
- Don't reference them from CLAUDE.md files

**Q: Where do implementation-specific agent docs go?**
- All detailed documentation goes in `Documentation/`, regardless of whether it's implementation-specific
- Use descriptive UPPERCASE naming to indicate the scope (e.g., `JS_CONVERSION_PLAN.md` for TypeScript-specific content)
