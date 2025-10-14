# Design: Repository Scaffold Procedure

**Spec ID:** 002  
**Status:** Implemented  
**Created:** 2025-10-14  
**Related:** `requirements.md`

---

## Overview

This document provides the **complete, step-by-step procedure** for creating a new Beast component repository based on the beast-mailbox-core template.

**Verified with:** `beast-mailbox-agent` (created 2025-10-14)

---

## Prerequisites

### Required Tools

```bash
# Verify you have these installed
gh --version          # GitHub CLI
git --version         # Git
python --version      # Python 3.9+
```

### Required Credentials

```bash
# Check these exist in ~/.env
grep GITHUB_TOKEN ~/.env
grep SONAR_TOKEN ~/.env
```

If missing, see AGENT.md for token setup instructions.

### Required Access

- ✅ Admin access to `nkllon` GitHub organization
- ✅ Member of `nkllon` SonarCloud organization
- ✅ Write access to beast-mailbox-core (reference repo)

---

## Procedure

### Step 1: Define Component

**Before creating anything**, clearly define:

**Component Name:** `beast-{purpose}` (e.g., `beast-mailbox-agent`)

**Purpose:** One sentence description

**Dependencies:** What will it depend on? (e.g., beast-mailbox-core)

**Package Name:** Python package name (replace hyphens with underscores)
- Repository: `beast-mailbox-agent`
- Package: `beast_mailbox_agent`

**Verify name is available:**
```bash
# Check PyPI
pip search beast-{your-name} || echo "Name available or pip search disabled"

# Check GitHub
gh repo view nkllon/beast-{your-name} 2>&1 | grep "not found" && echo "Name available"
```

---

### Step 2: Create GitHub Repository

```bash
# Navigate to workspace
cd /path/to/your/workspace

# Create repository (replace with your component name)
gh repo create nkllon/beast-{component-name} \
  --public \
  --description "Your one-line description" \
  --clone

# Verify creation
cd beast-{component-name}
git branch  # Should show 'main'
```

**Expected Output:**
```
https://github.com/nkllon/beast-{component-name}
Cloning into 'beast-{component-name}'...
```

---

### Step 3: Copy Structure from Template

```bash
# Ensure you're in the new repo directory
cd /path/to/workspace/beast-{component-name}

# Copy CI/CD workflows
cp -r ../beast-mailbox-core/.github .

# Copy license and maintainer guide
cp ../beast-mailbox-core/LICENSE .
cp ../beast-mailbox-core/AGENT.md .

# Create directory structure
mkdir -p docs steering tests src/beast_{component_name} .spec-workflow/specs
```

**What this creates:**
```
beast-{component-name}/
├── .github/workflows/      # CI/CD (will be modified)
├── .spec-workflow/specs/   # For future specifications
├── docs/                   # Documentation
├── steering/               # Process docs
├── src/beast_{name}/       # Python package
├── tests/                  # Test suite
├── AGENT.md                # Maintainer guide (will be modified)
└── LICENSE                 # MIT license
```

---

### Step 4: Create Build Configuration

**Create `pyproject.toml`:**

```toml
[project]
name = "beast-{component-name}"
version = "0.1.0"
description = "Your component description"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
keywords = ["your", "keywords", "here"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
  "beast-mailbox-core>=0.3.0",  # If needed
  # Add other dependencies
]

[project.optional-dependencies]
dev = [
  "pytest>=7.0.0",
  "pytest-asyncio>=0.21.0",
  "pytest-cov>=4.0.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = [
  "--cov=src/beast_{component_name}",
  "--cov-report=xml",
  "--cov-report=term-missing",
  "--verbose",
]

[project.urls]
Homepage = "https://github.com/nkllon/beast-{component-name}"
Repository = "https://github.com/nkllon/beast-{component-name}"

[project.scripts]
beast-{name} = "beast_{component_name}.cli:main"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

**Key changes from template:**
- Replace all instances of `beast-mailbox-core` with your component name
- Update `description` and `keywords`
- Update dependencies list
- Update CLI entry point name
- Update coverage path

---

### Step 5: Create SonarCloud Configuration

**Create `sonar-project.properties`:**

```properties
sonar.projectKey=nkllon_beast-{component-name}
sonar.organization=nkllon

# Exclusions
sonar.exclusions=**/node_modules/**,**/__pycache__/**,**/venv/**,**/.venv/**,**/dist/**,**/build/**,**/*.egg-info/**,**/docs/**,**/prompts/**,**/steering/**

# Source directories
sonar.sources=src
sonar.tests=tests

# Python specific
sonar.python.version=3.9,3.10,3.11,3.12

# Coverage
sonar.python.coverage.reportPaths=coverage.xml
```

**Key changes:**
- Update `sonar.projectKey` to match your repo name
- Use hyphens not underscores (matches GitHub repo name)

---

### Step 6: Create .gitignore

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
ENV/
env/
.venv/

# Testing
.pytest_cache/
.coverage
.coverage.*
coverage.xml
*.cover
htmlcov/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
.env
*.log
EOF
```

---

### Step 7: Create README.md

```markdown
# Beast {Component Name}

[![PyPI version](https://img.shields.io/pypi/v/beast-{component-name}?label=PyPI&color=blue)](https://pypi.org/project/beast-{component-name}/)
[![Python Versions](https://img.shields.io/pypi/pyversions/beast-{component-name}.svg)](https://pypi.org/project/beast-{component-name}/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**One-line description of your component**

## Status

🚧 **Under Development** - This project is being built using AI-driven spec-driven development.

## Overview

{Component Name} is a {description} that:
- Feature 1
- Feature 2
- Feature 3

## Architecture

```
[Diagram of your component's architecture]
```

## Installation

```bash
pip install beast-{component-name}
```

## Usage

```bash
# Basic usage example
beast-{name} ...
```

## Development Status

This project follows **spec-driven development**. See [`.spec-workflow/`](.spec-workflow/) for:
- Requirements specifications
- Design documents
- Implementation plans

## For AI Maintainers

**This repository is built 100% by AI agents and maintained by AI agents.**

Start here:
- **📖 [AGENT.md](AGENT.md)** - Comprehensive maintainer guide
- **📁 [.spec-workflow/](.spec-workflow/)** - Specifications and requirements

## Quality Standards

This project maintains the same quality standards as beast-mailbox-core:
- ✅ ≥ 85% test coverage
- ✅ Zero defects (SonarCloud)
- ✅ Comprehensive documentation
- ✅ All tests passing

## License

MIT

---

**Built with ❤️ by AI agents**
```

**Key changes:**
- Replace all `{component-name}` placeholders
- Write actual description
- Add architecture diagram
- Add usage examples

---

### Step 8: Create Python Package Stubs

**Create `src/beast_{component_name}/__init__.py`:**

```python
"""Beast {Component Name} - Short description."""

__version__ = "0.1.0"

# Package implementation to be added based on specifications
```

**Create `src/beast_{component_name}/cli.py`:**

```python
"""CLI entry point for Beast {Component Name}."""

def main():
    """Main entry point - to be implemented based on specifications."""
    print("Beast {Component Name} - Under Development")
    print("See .spec-workflow/ for specifications")

if __name__ == "__main__":
    main()
```

**Create `tests/__init__.py`:**

```python
"""Test suite for Beast {Component Name}."""
```

**Create `tests/conftest.py`:**

```python
"""Shared test fixtures for Beast {Component Name}."""

import pytest

# Fixtures will be added as implementation progresses
```

---

### Step 9: Update AGENT.md

**Replace the header section:**

```markdown
# AGENT.md - Maintainer Guide for AI Agents

**Repository:** beast-{component-name}  
**Current Maintainer:** AI Agent (You)  
**Last Updated:** YYYY-MM-DD  
**Project Status:** Under Development (Alpha)

---

## 🎯 Welcome, AI Maintainer!

You are the primary maintainer of **Beast {Component Name}**, a {description}. This project is being **100% implemented by LLMs using spec-driven development**.

## 🚧 Current Status: Scaffold Phase

This repository was just created from the beast-mailbox-core template. The structure is in place, but **implementation has not started yet**.

**What exists:**
- ✅ Project structure
- ✅ Build configuration
- ✅ CI/CD workflows
- ✅ Quality tooling
- ✅ This maintainer guide

**What needs to be built:**
- ❌ Core implementation
- ❌ Tests
- ❌ Documentation
- ❌ Specifications

**Where to start:**
1. Create specifications in `.spec-workflow/specs/`
2. Follow spec-driven development
3. Write tests first (TDD)
4. Maintain quality standards

[Keep the rest of the AGENT.md from beast-mailbox-core, updating component references]
```

---

### Step 10: Create CHANGELOG.md

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project scaffolding
- Project structure based on beast-mailbox-core
- Quality tooling setup
- Spec-driven development framework

### Status
- 🚧 **Alpha** - Under active development

---

## [0.1.0] - YYYY-MM-DD

### Added
- Initial repository creation
- Project scaffold
```

---

### Step 11: Commit Initial Scaffold

```bash
# Stage all files
git add .

# Check what will be committed
git status

# Commit
git commit -m "Initial project scaffold

- Project structure based on beast-mailbox-core
- Quality tooling: SonarCloud, GitHub Actions, pytest
- Spec-driven development framework (.spec-workflow/)
- Comprehensive AGENT.md for AI maintainers
- Build configuration (pyproject.toml)
- Basic Python package structure
- Ready for specification and implementation"

# Push to GitHub
git push -u origin main
```

**Verify:**
```bash
# Check commit was created
git log --oneline | head -1

# Check push succeeded
git branch -vv
```

---

### Step 12: Configure GitHub Secrets

**Set SONAR_TOKEN:**

```bash
# Navigate to repo
cd /path/to/beast-{component-name}

# Set secret (token from ~/.env)
gh secret set SONAR_TOKEN --body "$(grep SONAR_TOKEN ~/.env | cut -d= -f2)"

# Verify secret is set
gh secret list | grep SONAR
```

**Expected Output:**
```
SONAR_TOKEN  Updated YYYY-MM-DD
```

---

### Step 13: Configure SonarCloud

**Manual steps in SonarCloud web UI:**

1. **Go to SonarCloud:** https://sonarcloud.io

2. **Add project:**
   - Click "+" icon (top right)
   - Select "Analyze new project"

3. **Select repository:**
   - Find `nkllon/beast-{component-name}` in list
   - Check the box
   - Click "Set Up"

4. **Choose analysis method:**
   - Select "With GitHub Actions"
   - Click "Continue"

5. **Set new code definition:**
   - Choose "Number of days"
   - Enter **30** days
   - Click "Continue" or "Save"

6. **Done!**
   - Project key will be: `nkllon_beast-{component-name}`
   - Note: Use hyphens not underscores

---

### Step 14: Create Smoke Tests

**Create `tests/test_basic.py`:**

```python
"""Basic tests to verify setup."""

import beast_{component_name}


def test_version():
    """Test that version is defined."""
    assert hasattr(beast_{component_name}, "__version__")
    assert beast_{component_name}.__version__ == "0.1.0"


def test_import():
    """Test that package can be imported."""
    assert beast_{component_name} is not None
```

---

### Step 15: Trigger First Workflow

```bash
# Add smoke tests
git add tests/test_basic.py

# Commit
git commit -m "test: add basic smoke tests to trigger CI/CD"

# Push (triggers GitHub Actions)
git push

# Wait a moment, then check workflow status
sleep 5
gh run list --limit 1
```

**Expected Output:**
```
in_progress  test: add basic smoke tests  SonarCloud Analysis  main  push  ...
```

---

### Step 16: Wait for Workflow Completion

```bash
# Monitor workflow (auto-stops when complete)
for i in {1..20}; do
    sleep 10
    STATUS=$(gh run list --limit 1 --json status,conclusion --jq '.[0]')
    echo "[$i] $STATUS"
    if echo "$STATUS" | grep -q '"status":"completed"'; then
        break
    fi
done

# Check final status
gh run list --limit 1
```

**Expected Output:**
```
completed  test: add basic smoke tests  SonarCloud Analysis  main  push  ...
                                        ✓ (green checkmark)
```

---

### Step 17: Verify Setup

**Run verification checklist:**

```bash
# 1. Repository exists
gh repo view nkllon/beast-{component-name}

# 2. Main branch exists
git branch -r

# 3. Secrets configured
gh secret list

# 4. Workflow passed
gh run list --limit 1

# 5. SonarCloud project exists
open "https://sonarcloud.io/project/overview?id=nkllon_beast-{component-name}"

# 6. Tests pass locally (optional)
pip install -e ".[dev]"
pytest tests/
```

**All checks should pass!** ✅

---

## Verification Checklist

Use this checklist to verify scaffold completion:

### Pre-Creation Checks

- [ ] Component name decided (beast-{name})
- [ ] Purpose clearly defined
- [ ] Name available on GitHub
- [ ] Name available on PyPI (if publishing)
- [ ] gh CLI installed and authenticated
- [ ] GITHUB_TOKEN in ~/.env
- [ ] SONAR_TOKEN in ~/.env

### Post-Creation Checks

- [ ] Repository created on GitHub
- [ ] Structure copied from template
- [ ] pyproject.toml created and customized
- [ ] sonar-project.properties created
- [ ] .gitignore created
- [ ] README.md created and customized
- [ ] AGENT.md updated with component info
- [ ] CHANGELOG.md created
- [ ] Python package stubs created
- [ ] Initial commit pushed to main
- [ ] SONAR_TOKEN secret set
- [ ] SonarCloud project created (manual)
- [ ] New code definition set (30 days)
- [ ] Smoke tests created
- [ ] First workflow triggered
- [ ] Workflow passed ✅
- [ ] SonarCloud received analysis

### Quality Checks

- [ ] No linter errors in scaffolded files
- [ ] All Python files have proper docstrings
- [ ] pyproject.toml has correct package name
- [ ] All placeholders replaced
- [ ] Tests can be run locally
- [ ] Package can be imported

---

## Troubleshooting

### Issue: Repository creation fails

**Error:** `already exists` or `permission denied`

**Solution:**
- Check name isn't taken: `gh repo view nkllon/{name}`
- Verify gh authentication: `gh auth status`
- Check org membership: `gh org list`

### Issue: Workflow fails on first run

**Error:** Various workflow failures

**Solutions:**
- Check SONAR_TOKEN is set: `gh secret list`
- Verify sonar-project.properties has correct project key
- Check SonarCloud project was created
- View workflow logs: `gh run view --log-failed`

### Issue: SonarCloud shows no project

**Error:** Project doesn't appear in SonarCloud

**Solution:**
- Log into SonarCloud manually
- Click "+" to add project
- Select repository from list
- Follow setup wizard

### Issue: Tests fail locally

**Error:** Import errors or missing dependencies

**Solution:**
```bash
# Install in editable mode
pip install -e ".[dev]"

# Verify installation
pip show beast-{component-name}

# Run tests
pytest tests/ -v
```

---

## What to Do Next

After scaffold is complete, the next AI agent should:

1. **Create First Specification**
   - Write `.spec-workflow/specs/001-{feature}/requirements.md`
   - Define what to build and why

2. **Write Design Document**
   - Write `.spec-workflow/specs/001-{feature}/design.md`
   - Define how to build it

3. **Implement with TDD**
   - Write tests first
   - Implement to pass tests
   - Document thoroughly

4. **Maintain Quality**
   - Keep coverage ≥ 85%
   - Pass SonarCloud quality gate
   - Update CHANGELOG.md

---

## Summary

This procedure creates a **production-ready repository scaffold** in ~15 minutes:

**What you get:**
- ✅ Clean repository structure
- ✅ Quality tooling configured
- ✅ CI/CD passing
- ✅ SonarCloud integrated
- ✅ Ready for spec-driven development

**What's NOT included:**
- ❌ Implementation (that's the next phase)
- ❌ Specifications (to be written)
- ❌ Tests (beyond smoke tests)
- ❌ Documentation (beyond README)

**The scaffold is the foundation. The specifications are the blueprint. The implementation is the house.**

---

## Change Log

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2025-10-14 | 0.1.0 | Reverse-engineered from beast-mailbox-agent | AI Agent |

---

**End of Design Specification**

