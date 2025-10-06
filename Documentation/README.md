# Chatfield Documentation

Welcome to the Chatfield documentation! This directory contains comprehensive guides covering architecture, design, testing, and usage of the Chatfield conversational data collection framework.

## 📚 Documentation Map

### Getting Started

- **[Getting Started - Python](Getting_Started_Python.md)**: Quick start guide for Python developers
- **[Getting Started - TypeScript](Getting_Started_TypeScript.md)**: Quick start guide for TypeScript/JavaScript developers
- **[Mandatory Environment File](Mandatory_Environment_File.md)**: API key configuration and environment setup

### Architecture Documentation

- **[Architecture Overview](ARCHITECTURE.md)** ⭐ **START HERE**
  - System overview and core concepts
  - Component architecture (Interview, Interviewer, Builder, FieldProxy)
  - Data flow through the system
  - LangGraph state machine details
  - Integration architecture (React, CopilotKit)
  - Key design patterns and file reference

- **[Prompt System](PROMPT_SYSTEM.md)**
  - Template engine architecture
  - Handlebars template structure
  - System prompt generation
  - Digest prompts (confidential/conclude)
  - Custom helpers and context variables
  - Best practices for prompt development

- **[Testing Architecture](TESTING_ARCHITECTURE.md)**
  - Test philosophy and harmonization
  - Testing infrastructure (pytest, Jest)
  - Test categories (unit, integration, conversation, security)
  - Mock LLM system for fast testing
  - Security evaluation suite
  - Test writing guidelines and debugging

- **[Design Decisions](DESIGN_DECISIONS.md)**
  - Builder pattern vs inheritance
  - FieldProxy implementation rationale
  - LangGraph state machine choice
  - Dual language implementation strategy
  - Template-based prompts
  - Transformation at collection time
  - Confidential vs conclude fields
  - Mock injection for testing
  - Tool-based vs direct updates

### Test Documentation

- **[Test Harmonization Guide](TEST_HARMONIZATION.md)**: Cross-implementation test synchronization (if exists)
- **[Python Test Guide](../Python/tests/CLAUDE.md)**: Python-specific testing details
- **[TypeScript Test Guide](../TypeScript/tests/CLAUDE.md)**: TypeScript-specific testing details

### Implementation Guides

- **[Python Implementation](../Python/CLAUDE.md)**: Python-specific architecture and usage
- **[TypeScript Implementation](../TypeScript/CLAUDE.md)**: TypeScript-specific architecture and usage
- **[Project Overview](../CLAUDE.md)**: Main project documentation

### Developer Resources

- **[Developer Guide](../Developers.md)**: Contributing guidelines and development setup (if exists)

---

## 🎯 Quick Navigation by Topic

### I want to understand...

#### **...the overall system**
→ Start with [Architecture Overview](ARCHITECTURE.md)
- Read: System Overview, Core Components, Data Flow Architecture

#### **...how prompts work**
→ Read [Prompt System](PROMPT_SYSTEM.md)
- Focus on: System Prompt Structure, Template Generation Flow

#### **...how to write tests**
→ Read [Testing Architecture](TESTING_ARCHITECTURE.md)
- Focus on: Test Categories, Test Writing Guidelines

#### **...why things are designed this way**
→ Read [Design Decisions](DESIGN_DECISIONS.md)
- Focus on: Rationale sections for each decision

#### **...how to get started quickly**
→ Use Getting Started guides
- Python: [Getting Started - Python](Getting_Started_Python.md)
- TypeScript: [Getting Started - TypeScript](Getting_Started_TypeScript.md)

---

## 📖 Learning Paths

### For New Contributors

1. **[Getting Started](Getting_Started_Python.md)** - Set up and run examples
2. **[Architecture Overview](ARCHITECTURE.md)** - Understand core components
3. **[Testing Architecture](TESTING_ARCHITECTURE.md)** - Learn testing approach
4. **[Design Decisions](DESIGN_DECISIONS.md)** - Understand the "why"

### For Users Building Forms

1. **[Getting Started](Getting_Started_Python.md)** - Initial setup
2. **[Architecture Overview](ARCHITECTURE.md)** → Builder Pattern section
3. **[Python/TypeScript CLAUDE.md](../Python/CLAUDE.md)** - API reference
4. **Examples** - See `examples/` directory in Python or TypeScript

### For Prompt Engineers

1. **[Prompt System](PROMPT_SYSTEM.md)** - Template architecture
2. **[Architecture Overview](ARCHITECTURE.md)** → Template System section
3. **[Design Decisions](DESIGN_DECISIONS.md)** → Template-based Prompts
4. **Prompts/** directory - Actual templates

### For Testers

1. **[Testing Architecture](TESTING_ARCHITECTURE.md)** - Complete testing guide
2. **[Design Decisions](DESIGN_DECISIONS.md)** → Mock Injection
3. **[Architecture Overview](ARCHITECTURE.md)** → Mock LLM System
4. **Test files** - Examples in `tests/` directories

### For Security Researchers

1. **[Testing Architecture](TESTING_ARCHITECTURE.md)** → Security Evaluation Suite
2. **[Architecture Overview](ARCHITECTURE.md)** → Security Model
3. **[Prompt System](PROMPT_SYSTEM.md)** → Confidential Information
4. **Python/evals/** - Security evaluation code

---

## 🔑 Key Concepts Index

### Core Components

| Component | File | Description |
|-----------|------|-------------|
| Interview | [ARCHITECTURE.md](ARCHITECTURE.md#1-interview-class) | Central data structure for forms |
| Builder API | [ARCHITECTURE.md](ARCHITECTURE.md#2-builder-api) | Fluent interface for defining forms |
| Interviewer | [ARCHITECTURE.md](ARCHITECTURE.md#3-interviewer-class) | Conversation orchestration |
| FieldProxy | [ARCHITECTURE.md](ARCHITECTURE.md#4-fieldproxy-class) | String-like field values with transformations |
| TemplateEngine | [PROMPT_SYSTEM.md](PROMPT_SYSTEM.md#template-engine-architecture) | Handlebars-based prompt generation |

### Patterns & Concepts

| Concept | File | Section |
|---------|------|---------|
| Builder Pattern | [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md#builder-pattern-vs-inheritance) | Why builder over inheritance |
| LangGraph State Machine | [ARCHITECTURE.md](ARCHITECTURE.md#langgraph-state-machine) | Conversation flow control |
| Test Harmonization | [TESTING_ARCHITECTURE.md](TESTING_ARCHITECTURE.md#test-harmonization) | Cross-language test sync |
| Mock LLM System | [TESTING_ARCHITECTURE.md](TESTING_ARCHITECTURE.md#mock-llm-system) | Fast deterministic testing |
| Confidential Fields | [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md#confidential-vs-conclude-fields) | Security-focused fields |
| Transformations | [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md#transformation-at-collection-time) | LLM-powered type conversion |

### Technical Details

| Topic | File | Section |
|-------|------|---------|
| _chatfield Structure | [ARCHITECTURE.md](ARCHITECTURE.md#internal-structure-_chatfield-dictionary) | Internal data format |
| Node Graph | [ARCHITECTURE.md](ARCHITECTURE.md#node-graph) | State machine nodes |
| System Prompt | [PROMPT_SYSTEM.md](PROMPT_SYSTEM.md#system-prompt-structure) | Main conversation prompt |
| Tool Generation | [ARCHITECTURE.md](ARCHITECTURE.md#key-methods) | Dynamic Pydantic/Zod schemas |
| Merge Logic | [ARCHITECTURE.md](ARCHITECTURE.md#6-merge-logic) | State merging strategy |

---

## 📝 Documentation Standards

### File Naming

- **UPPERCASE.md**: Architecture/design documentation
- **Sentence_Case.md**: Getting started guides
- **lowercase.md**: README and index files

### Structure

All major docs follow this structure:
1. **Table of Contents** - Easy navigation
2. **Overview** - What this doc covers
3. **Main Content** - Detailed sections
4. **Examples** - Code samples
5. **Summary/Conclusion** - Key takeaways

### Cross-References

Documents link to related content:
- Internal links to sections: `[Architecture](#architecture)`
- Cross-document links: `[Testing](TESTING_ARCHITECTURE.md)`
- External links: `[LangGraph](https://langchain.com/langgraph)`

---

## 🛠️ Contributing to Documentation

### Adding New Documentation

1. Create file in `Documentation/`
2. Add entry to this README
3. Link from relevant existing docs
4. Follow documentation standards
5. Update cross-references

### Updating Existing Documentation

1. Maintain table of contents
2. Update "Last Updated" if present
3. Check cross-references still work
4. Verify code examples still accurate
5. Update index entries if section names change

### Documentation Principles

1. **Clarity**: Write for the target audience
2. **Completeness**: Cover all aspects of the topic
3. **Examples**: Show don't just tell
4. **Consistency**: Follow established patterns
5. **Maintenance**: Keep docs in sync with code

---

## 📊 Documentation Statistics

| Document | Focus | Audience | Est. Reading Time |
|----------|-------|----------|-------------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design | Developers | 45 min |
| [PROMPT_SYSTEM.md](PROMPT_SYSTEM.md) | Prompt engineering | Prompt engineers | 30 min |
| [TESTING_ARCHITECTURE.md](TESTING_ARCHITECTURE.md) | Testing strategy | Testers/Contributors | 40 min |
| [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) | Design rationale | Architects | 35 min |
| [Getting_Started_Python.md](Getting_Started_Python.md) | Quick start | Python users | 15 min |
| [Getting_Started_TypeScript.md](Getting_Started_TypeScript.md) | Quick start | TypeScript users | 15 min |

**Total**: ~3 hours for complete understanding

---

## 🔗 External Resources

### LangGraph Documentation
- [LangGraph Python](https://langchain-ai.github.io/langgraph/)
- [LangGraph JavaScript](https://langchain-ai.github.io/langgraphjs/)

### Related Technologies
- [Handlebars](https://handlebarsjs.com/) - Template engine
- [Pydantic](https://docs.pydantic.dev/) - Python validation
- [Zod](https://zod.dev/) - TypeScript validation
- [OpenAI API](https://platform.openai.com/docs/) - LLM provider

### Testing Frameworks
- [pytest](https://docs.pytest.org/) - Python testing
- [Jest](https://jestjs.io/) - TypeScript testing
- [DeepEval](https://docs.confident-ai.com/) - LLM evaluation

---

## 📞 Getting Help

### Documentation Issues

If documentation is unclear, incomplete, or incorrect:

1. **Check related docs** - Use cross-references
2. **Review examples** - Code often clarifies
3. **File an issue** - Help us improve docs
4. **Contribute fixes** - PRs welcome!

### Code Issues

For code-related questions:

1. **Read relevant docs** - Start with Architecture
2. **Check examples** - See it in action
3. **Review tests** - Tests document behavior
4. **File an issue** - Describe the problem

---

## 🎓 Advanced Topics

### For Deep Dives

- **State Management**: [ARCHITECTURE.md](ARCHITECTURE.md#langgraph-state-machine) + LangGraph docs
- **Prompt Engineering**: [PROMPT_SYSTEM.md](PROMPT_SYSTEM.md) + `Prompts/` directory
- **Security Testing**: [TESTING_ARCHITECTURE.md](TESTING_ARCHITECTURE.md#security-evaluation-suite) + `Python/evals/`
- **Type Systems**: Implementation CLAUDE.md files + Pydantic/Zod docs
- **Integration**: [ARCHITECTURE.md](ARCHITECTURE.md#integration-architecture) + integration examples

### Research Papers & Inspiration

(Add relevant papers/articles that influenced the design)

---

## 📅 Documentation Roadmap

### Planned Documentation

- [ ] **API_REFERENCE.md**: Complete API documentation
- [ ] **DEPLOYMENT.md**: Production deployment guide
- [ ] **PERFORMANCE.md**: Optimization and scaling
- [ ] **SECURITY.md**: Security best practices
- [ ] **MIGRATION.md**: Version migration guides
- [ ] **TROUBLESHOOTING.md**: Common issues and solutions

### Documentation Maintenance

- Regular reviews for accuracy
- Update with major releases
- Expand examples based on feedback
- Improve clarity based on questions

---

## 📜 License

Chatfield documentation is part of the Chatfield project. See project LICENSE for details.

---

## ✨ Contributors

Documentation created and maintained by the Chatfield team and community contributors.

Special thanks to all who have helped improve these docs!

---

**Last Updated**: 2025-01-06
**Documentation Version**: 1.0.0
**Chatfield Version**: Python 0.2.0 | TypeScript 0.1.0
