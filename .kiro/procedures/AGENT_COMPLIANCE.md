# AGENT.md Compliance Procedures

This document provides procedural guidance for ensuring AGENT.md compliance when making changes to the beast-mailbox-core repository.

## Overview

Per AGENT.md requirements-first principles, all changes must follow this sequence:
1. **Requirements** → Gather and document requirements
2. **Design** → Propose solution design
3. **Implementation** → Implement the solution

## Procedure 0.1: Requirements-First Approach

### Checklist

Before proposing any solution, ensure:

- [ ] **Requirements Documented**: All requirements are explicitly documented in a requirements file
- [ ] **Requirements Referenced**: Design documents reference specific requirement IDs (e.g., REQ-1.1, REQ-2.3)
- [ ] **No Assumptions**: Requirements are based on actual needs, not assumptions
- [ ] **Requirements Reviewed**: Requirements are reviewed and approved before design begins

### Template: Requirements Document

Create a requirements file (e.g., `.kiro/specs/[feature]/requirements.md`) with this structure:

```markdown
# Requirements: [Feature Name]

## Introduction
[Context and user story]

## Glossary
[Key terms and definitions]

## Requirements

### Requirement X
**User Story:** As a [role], I want [goal], so that [benefit].

#### Acceptance Criteria
1. THE [System] SHALL [requirement]
2. WHEN [condition], THE [System] SHALL [requirement]
3. ...

#### Requirements
- REQ-X.1: [Specific requirement]
- REQ-X.2: [Specific requirement]
```

### Procedure Steps

1. **Gather Requirements**
   ```bash
   # Before starting work, document requirements
   # 1. Identify user story
   # 2. List acceptance criteria
   # 3. Define specific requirements with IDs
   ```

2. **Document Requirements**
   - Create requirements file in `.kiro/specs/[feature]/requirements.md`
   - Use consistent requirement ID format: `REQ-X.Y`
   - Include glossary for domain-specific terms

3. **Review Requirements**
   - Verify requirements are complete
   - Ensure no assumptions are made
   - Get approval (if needed) before proceeding

4. **Reference Requirements**
   - All design documents must reference requirement IDs
   - Implementation tasks must reference requirement IDs
   - Traceability must be maintained

---

## Procedure 0.2: Workflow Verification

### Purpose

Before modifying workflows, verify existing workflow state to avoid duplication and understand dependencies.

### Procedure Steps

1. **List All Workflows**
   ```bash
   # List all workflow files
   ls -la .github/workflows/*.yml
   
   # Or use the diagnostic tool
   python scripts/diagnose_pr.py --list-workflows  # (if implemented)
   ```

2. **Read Each Workflow**
   ```bash
   # Read workflow files
   cat .github/workflows/sonarcloud.yml
   cat .github/workflows/quality-metrics.yml
   # ... etc
   ```

3. **Document Workflow State**
   - Create or update `.kiro/specs/github-workflows/workflow-state.md`
   - Document:
     - Workflow triggers
     - Dependencies between workflows
     - Artifact names and retention
     - Required permissions
     - External service dependencies

4. **Understand Triggers**
   - Document what events trigger each workflow
   - Identify path filters and conditional execution
   - Note workflow dependencies (workflow_run triggers)

5. **Check Dependencies**
   - Map artifact dependencies
   - Identify workflow_run dependencies
   - Document any circular dependencies (should be avoided)

### Template: Workflow State Document

```markdown
# Workflow State Documentation

## Workflows

### workflow-name.yml
- **Triggers**: [push, pull_request, workflow_run, etc.]
- **Dependencies**: [upstream workflows]
- **Artifacts**: [artifact names]
- **Permissions**: [required permissions]
- **External Services**: [SonarCloud, Prometheus, etc.]
```

### Tools Available

- `scripts/diagnose_pr.py` - Can fetch workflow run information
- `.github/workflows/README.md` - Comprehensive workflow documentation

---

## Procedure 0.3: System State Verification

### Purpose

Before making changes, verify actual system state (don't assume).

### Procedure Steps

1. **Verify PR Existence and Status**
   ```bash
   # Use diagnose_pr.py tool
   python scripts/diagnose_pr.py <pr_number>
   
   # Or use GitHub CLI
   gh pr view <pr_number>
   ```

2. **Verify Dependency Configuration**
   ```bash
   # Check pyproject.toml
   cat pyproject.toml
   
   # Check lock file
   cat uv.lock | head -50
   
   # Use analyze_dependencies.py
   python scripts/analyze_dependencies.py
   ```

3. **Verify Workflow Status**
   ```bash
   # Check workflow runs
   gh run list --workflow="workflow-name"
   
   # Or use GitHub API via diagnose_pr.py
   ```

4. **Document Actual State**
   - Create investigation report (e.g., `.kiro/specs/[issue]/investigation.md`)
   - Document:
     - Current state (what exists)
     - Expected state (what should exist)
     - Gaps (what's missing)
     - Evidence (screenshots, logs, API responses)

### Template: System State Verification

```markdown
# System State Verification: [Issue/Feature]

## Date
[Date of verification]

## Current State

### PR Status
- PR #X: [state] - [URL]
- Last updated: [timestamp]
- Workflow status: [status]

### Dependency Configuration
- pyproject.toml version: [version]
- Key dependencies: [list]
- Lock file status: [up-to-date/out-of-date]

### Workflow State
- [Workflow name]: [status]
- [Workflow name]: [status]

## Expected State
[What should exist]

## Gaps
[What's missing or incorrect]

## Evidence
[Screenshots, logs, API responses]
```

### Tools Available

- `scripts/diagnose_pr.py` - PR verification and analysis
- `scripts/analyze_dependencies.py` - Dependency analysis
- GitHub CLI (`gh`) - Repository state queries
- GitHub API - Direct API queries

---

## Compliance Checklist

Before starting any work, verify:

- [ ] Requirements documented (Procedure 0.1)
- [ ] Workflows verified (Procedure 0.2)
- [ ] System state verified (Procedure 0.3)
- [ ] Requirements referenced in design
- [ ] Requirements referenced in implementation tasks

---

## Quick Reference

### Requirements Documentation
- Location: `.kiro/specs/[feature]/requirements.md`
- Format: User story → Acceptance criteria → Requirements (REQ-X.Y)

### Workflow Verification
- Location: `.github/workflows/`
- Documentation: `.github/workflows/README.md`
- Tool: `scripts/diagnose_pr.py`

### System State Verification
- Tools: `scripts/diagnose_pr.py`, `scripts/analyze_dependencies.py`, `gh`
- Documentation: Investigation reports in `.kiro/specs/[issue]/`

---

## Examples

### Example: Adding a New Workflow

1. **Requirements First** (Procedure 0.1)
   - Document requirements in `.kiro/specs/new-workflow/requirements.md`
   - Define REQ-1.1, REQ-1.2, etc.

2. **Workflow Verification** (Procedure 0.2)
   - List existing workflows
   - Check for similar workflows (avoid duplication)
   - Understand triggers and dependencies

3. **System State** (Procedure 0.3)
   - Verify no conflicting workflows exist
   - Check repository permissions
   - Verify external service availability

4. **Design** (Reference requirements)
   - Create design document referencing REQ-1.1, REQ-1.2, etc.

5. **Implementation** (Reference requirements)
   - Implement workflow referencing REQ-1.1, REQ-1.2, etc.

### Example: Fixing Dependabot PR Failure

1. **Requirements First** (Procedure 0.1)
   - Document requirements: REQ-4.3.1, REQ-4.3.2, etc.

2. **System State Verification** (Procedure 0.3)
   - Use `scripts/diagnose_pr.py <pr_number>` to verify PR exists
   - Check workflow failures
   - Analyze dependency changes

3. **Investigation** (Document actual state)
   - Create investigation report
   - Document root cause

4. **Resolution** (Reference requirements)
   - Fix issues referencing REQ-4.4.1, REQ-4.4.2, etc.

---

**Last Updated**: 2025-01-31  
**Maintained By**: Project maintainers

