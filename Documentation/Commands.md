# Development Commands

## Python Implementation (Python/)

### Setup & Installation
```bash
cd Python
python -m venv .venv                                # Create virtual environment
source .venv/bin/activate                           # Activate venv (Linux/Mac)
pip install -e ".[dev]"                             # Install with dev dependencies
```

### Testing
```bash
python -m pytest                                    # Run all tests
python -m pytest tests/test_interview.py            # Run specific test file
python -m pytest -k "test_name"                     # Run specific test by name
python -m pytest -m "not slow"                      # Skip slow tests
python -m pytest -m "requires_api_key"              # Run only API tests
```

### Code Quality
```bash
make format                                          # Format with black & isort
make lint                                            # Run flake8 linting
make typecheck                                       # Run mypy type checking
make test-cov                                        # Run tests with coverage report
```

### Build & Distribution
```bash
make build                                           # Build distribution packages
pip install -e .                                     # Development install
```

### Running Examples
```bash
cd examples && python job_interview.py              # Run any example
python -c "from chatfield import Interview"         # Quick import test
```

## TypeScript/JavaScript Implementation (TypeScript/)

### Setup & Installation
```bash
cd TypeScript
npm install                                          # Install dependencies
```

### Development & Build
```bash
npm run build                                        # Compile TypeScript to dist/
npm run dev                                          # Watch mode compilation
npm run clean                                        # Remove dist/ directory
```

### Testing
```bash
npm test                                             # Run Jest test suite
npm run test:watch                                   # Watch mode testing
npm test -- interview.test.ts                       # Run specific test file
```

### Code Quality
```bash
npm run format                                       # Format with Prettier (auto-fix)
npm run format:check                                 # Check formatting without changes
npm run lint                                         # ESLint checks
npm run lint:fix                                     # ESLint auto-fix issues
npm run typecheck                                    # TypeScript type checking
npm run check-all                                    # Run all checks + tests
```

### Running Examples
```bash
npm run min                                          # Run minimal.ts OpenAI test
npx tsx examples/basic-usage.ts                     # Run any example directly
node dist/examples/basic-usage.js                   # Run compiled example

# Quick Tests
npx tsx minimal.ts                                  # Test OpenAI API connection
```

## API Key Configuration

Both implementations require OpenAI API key:

```bash
# Option 1: Environment variable
export OPENAI_API_KEY=your-api-key

# Option 2: .env file in project root
echo "OPENAI_API_KEY=your-api-key" > .env

# Option 3: Pass to Interviewer constructor (see API documentation)
```
