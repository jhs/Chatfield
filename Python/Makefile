.PHONY: help install install-dev test test-cov lint format typecheck clean build publish docs proxy plantuml plantuml-extract plantuml-png plantuml-clean

help:
	@echo "Available commands:"
	@echo "  make install       Install the package in production mode"
	@echo "  make install-dev   Install the package in editable mode with dev dependencies"
	@echo "  make test          Run the test suite"
	@echo "  make test-cov      Run tests with coverage report"
	@echo "  make lint          Run linting checks (flake8)"
	@echo "  make format        Format code with black and isort"
	@echo "  make typecheck     Run type checking with mypy"
	@echo "  make clean         Remove build artifacts and cache files"
	@echo "  make build         Build distribution packages"
	@echo "  make publish       Upload package to PyPI (requires credentials)"
	@echo "  make docs          Generate documentation (if available)"
	@echo "  make proxy         Start LiteLLM proxy server for development"
	@echo "  make plantuml      Generate PNG diagrams from PlantUML files"

install:
	pip install -e .

install-dev:
	pip install --upgrade pip setuptools wheel
	pip install -e .[dev]
	@echo "✅ Development environment ready!"
	@echo "Consider running: pre-commit install"

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=chatfield --cov-report=term-missing --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	flake8 chatfield/ tests/
	@echo "✅ Linting passed!"

format:
	black chatfield/ tests/
	isort chatfield/ tests/
	@echo "✅ Code formatted!"

typecheck:
	mypy chatfield/
	@echo "✅ Type checking passed!"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf chatfield.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete
	@echo "✅ Cleaned build artifacts and cache files!"

build: clean
	python -m build
	@echo "✅ Built distribution packages in dist/"

publish: build
	@echo "Publishing to PyPI..."
	twine check dist/*
	twine upload dist/*
	@echo "✅ Package published to PyPI!"

docs:
	@echo "Documentation generation not yet configured"
	@echo "Consider using Sphinx or MkDocs for documentation"

proxy:
	@echo "Starting LiteLLM proxy on http://localhost:4000"
	@echo "Press Ctrl+C to stop"
	litellm --config litellm_config.yaml --detailed_debug

# Development workflow shortcuts
.PHONY: dev check ci

dev: format lint typecheck test
	@echo "✅ All development checks passed!"

check: lint typecheck test
	@echo "✅ All checks passed!"

ci: check
	@echo "✅ CI checks passed!"

# PlantUML file generation and diagram rendering
.PHONY: plantuml plantuml-extract plantuml-png plantuml-clean

# Paths relative to Python/
SKILL_DIR = ../Claude/filling-pdf-forms/skills/filling-pdf-forms
EXTRACTING_SKILL_DIR = ../Claude/filling-pdf-forms/skills/extracting-form-fields
PLANTUML_FILES = \
	$(SKILL_DIR)/SKILL.plantuml \
	$(SKILL_DIR)/references/Translating.plantuml \
	$(SKILL_DIR)/references/Converting-PDF-To-Chatfield.plantuml \
	$(SKILL_DIR)/references/Populating-Fillable.plantuml \
	$(SKILL_DIR)/references/Populating-Nonfillable.plantuml \
	$(SKILL_DIR)/references/CLI-Interview-Loop.plantuml \
	$(EXTRACTING_SKILL_DIR)/SKILL.plantuml \
	$(EXTRACTING_SKILL_DIR)/references/Fillable-Forms.plantuml \
	$(EXTRACTING_SKILL_DIR)/references/Nonfillable-Forms.plantuml

# Extract .plantuml files from .md sources
plantuml-extract: $(PLANTUML_FILES)

$(SKILL_DIR)/SKILL.plantuml: $(SKILL_DIR)/SKILL.md
	@sed -n '/^```plantuml$$/,/^```$$/p' $< | sed '1d;$$d' > $@

$(SKILL_DIR)/references/Translating.plantuml: $(SKILL_DIR)/references/Translating.md
	@sed -n '/^```plantuml$$/,/^```$$/p' $< | sed '1d;$$d' > $@

$(SKILL_DIR)/references/Converting-PDF-To-Chatfield.plantuml: $(SKILL_DIR)/references/Converting-PDF-To-Chatfield.md
	@sed -n '/^```plantuml$$/,/^```$$/p' $< | sed '1d;$$d' > $@

$(SKILL_DIR)/references/Populating-Fillable.plantuml: $(SKILL_DIR)/references/Populating-Fillable.md
	@sed -n '/^```plantuml$$/,/^```$$/p' $< | sed '1d;$$d' > $@

$(SKILL_DIR)/references/Populating-Nonfillable.plantuml: $(SKILL_DIR)/references/Populating-Nonfillable.md
	@sed -n '/^```plantuml$$/,/^```$$/p' $< | sed '1d;$$d' > $@

$(SKILL_DIR)/references/CLI-Interview-Loop.plantuml: $(SKILL_DIR)/references/CLI-Interview-Loop.md
	@sed -n '/^```plantuml$$/,/^```$$/p' $< | sed '1d;$$d' > $@

$(EXTRACTING_SKILL_DIR)/SKILL.plantuml: $(EXTRACTING_SKILL_DIR)/SKILL.md
	@sed -n '/^```plantuml$$/,/^```$$/p' $< | sed '1d;$$d' > $@

$(EXTRACTING_SKILL_DIR)/references/Fillable-Forms.plantuml: $(EXTRACTING_SKILL_DIR)/references/Fillable-Forms.md
	@sed -n '/^```plantuml$$/,/^```$$/p' $< | sed '1d;$$d' > $@

$(EXTRACTING_SKILL_DIR)/references/Nonfillable-Forms.plantuml: $(EXTRACTING_SKILL_DIR)/references/Nonfillable-Forms.md
	@sed -n '/^```plantuml$$/,/^```$$/p' $< | sed '1d;$$d' > $@

# Generate PNG diagrams from .plantuml files using Docker
plantuml-png: plantuml-extract
	@docker run --rm -v "$(shell cd .. && pwd)":/data plantuml/plantuml -tpng "/data/Claude/filling-pdf-forms/skills/filling-pdf-forms/SKILL.plantuml" 2>/dev/null
	@docker run --rm -v "$(shell cd .. && pwd)":/data plantuml/plantuml -tpng "/data/Claude/filling-pdf-forms/skills/filling-pdf-forms/references/Translating.plantuml" 2>/dev/null
	@docker run --rm -v "$(shell cd .. && pwd)":/data plantuml/plantuml -tpng "/data/Claude/filling-pdf-forms/skills/filling-pdf-forms/references/Populating-Fillable.plantuml" 2>/dev/null
	@docker run --rm -v "$(shell cd .. && pwd)":/data plantuml/plantuml -tpng "/data/Claude/filling-pdf-forms/skills/filling-pdf-forms/references/Populating-Nonfillable.plantuml" 2>/dev/null
	@docker run --rm -v "$(shell cd .. && pwd)":/data plantuml/plantuml -tpng "/data/Claude/filling-pdf-forms/skills/filling-pdf-forms/references/Converting-PDF-To-Chatfield.plantuml" 2>/dev/null
	@docker run --rm -v "$(shell cd .. && pwd)":/data plantuml/plantuml -tpng "/data/Claude/filling-pdf-forms/skills/filling-pdf-forms/references/CLI-Interview-Loop.plantuml" 2>/dev/null
	@docker run --rm -v "$(shell cd .. && pwd)":/data plantuml/plantuml -tpng "/data/Claude/filling-pdf-forms/skills/extracting-form-fields/SKILL.plantuml" 2>/dev/null
	@docker run --rm -v "$(shell cd .. && pwd)":/data plantuml/plantuml -tpng "/data/Claude/filling-pdf-forms/skills/extracting-form-fields/references/Fillable-Forms.plantuml" 2>/dev/null
	@docker run --rm -v "$(shell cd .. && pwd)":/data plantuml/plantuml -tpng "/data/Claude/filling-pdf-forms/skills/extracting-form-fields/references/Nonfillable-Forms.plantuml" 2>/dev/null

# Clean up temporary .plantuml files
plantuml-clean:
	@rm -f $(PLANTUML_FILES)

# Main plantuml target: extract .plantuml from .md, generate PNG, then clean up .plantuml files
plantuml: plantuml-png plantuml-clean
