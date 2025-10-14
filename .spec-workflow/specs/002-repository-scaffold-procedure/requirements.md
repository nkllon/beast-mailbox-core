# Requirements: Repository Scaffold Procedure

**Spec ID:** 002  
**Status:** Implemented (Reverse-Engineered)  
**Created:** 2025-10-14  
**Owner:** AI Agent Maintainer  
**Priority:** High (Process Documentation)

---

## Problem Statement

### The Need for Repeatable Repository Creation

The **Beast Mode** ecosystem consists of multiple related components:
- `beast-mailbox-core` - Core messaging infrastructure
- `beast-mailbox-agent` - LLM agent that uses mailbox
- Future components - Additional services and tools

Each new component should maintain the **same high quality standards** established in beast-mailbox-core:
- ✅ 85%+ test coverage
- ✅ Zero defects (SonarCloud)
- ✅ Comprehensive documentation  
- ✅ Spec-driven development
- ✅ AI-maintainer friendly

**Without a documented procedure**, creating new repositories results in:
- ❌ Inconsistent project structure
- ❌ Missing quality tooling
- ❌ Incomplete CI/CD setup
- ❌ Lost tribal knowledge
- ❌ Manual, error-prone process

**With a documented procedure**, any AI agent can:
- ✅ Create a new repository with proper structure
- ✅ Maintain consistency across components
- ✅ Include all quality tooling from day one
- ✅ Follow established patterns
- ✅ Execute repeatably without human guidance

---

## Current State

### What Exists

**beast-mailbox-core** - The template repository with:
- Proven project structure
- Quality tooling (SonarCloud, GitHub Actions)
- Comprehensive documentation (AGENT.md)
- Spec-driven development framework (.spec-workflow/)
- Testing infrastructure (pytest, coverage)
- Build system (pyproject.toml)

**What Was Just Created:**

**beast-mailbox-agent** - Successfully scaffolded following an ad-hoc procedure:
1. Created repository via `gh repo create`
2. Copied structure from beast-mailbox-core
3. Modified metadata for new purpose
4. Set up SonarCloud
5. Triggered initial workflow
6. Verified everything works

**What's Missing:**

❌ **No documented procedure** - The steps exist only in conversation history  
❌ **No checklist** - Easy to forget steps  
❌ **No validation** - No way to verify completeness  
❌ **Not repeatable** - Next AI agent must reinvent

---

## Requirements

### REQ-001: Documented Scaffold Procedure

**Requirement:** Create a comprehensive, step-by-step procedure for scaffolding new Beast component repositories.

**Acceptance Criteria:**
- ✅ All steps documented in order
- ✅ Commands provided (copy-paste ready)
- ✅ Explanations for each step
- ✅ Success criteria defined
- ✅ Verification steps included

**Priority:** P0 (Critical)

### REQ-002: Template Structure Definition

**Requirement:** Document what to keep vs. what to change when scaffolding.

**Acceptance Criteria:**
- ✅ List of files/directories to copy
- ✅ List of files to modify
- ✅ List of metadata to update
- ✅ Clear decision tree
- ✅ Examples provided

**Priority:** P0 (Critical)

### REQ-003: Quality Tooling Setup

**Requirement:** Document how to configure SonarCloud and GitHub Actions.

**Acceptance Criteria:**
- ✅ SonarCloud project creation steps
- ✅ Token configuration procedure
- ✅ Workflow verification steps
- ✅ Troubleshooting guidance
- ✅ Success indicators

**Priority:** P0 (Critical)

### REQ-004: Verification Checklist

**Requirement:** Provide a checklist to verify scaffold completion.

**Acceptance Criteria:**
- ✅ Pre-flight checks
- ✅ Post-creation checks
- ✅ Workflow validation
- ✅ SonarCloud validation
- ✅ Clear pass/fail criteria

**Priority:** P1 (High)

### REQ-005: Troubleshooting Guide

**Requirement:** Document common issues and solutions.

**Acceptance Criteria:**
- ✅ Common failure modes
- ✅ Error messages explained
- ✅ Recovery procedures
- ✅ When to ask for help
- ✅ Related documentation links

**Priority:** P1 (High)

---

## Use Cases

### Use Case 1: Creating a New Beast Component

**Actor:** AI Agent Maintainer

**Preconditions:**
- beast-mailbox-core exists and is production-ready
- User has requested a new component
- Component purpose is defined

**Flow:**
1. AI agent reads this specification
2. Follows documented procedure
3. Creates new repository
4. Copies appropriate structure
5. Configures tooling
6. Verifies setup
7. Reports completion to user

**Postconditions:**
- New repository exists with proper structure
- Quality tooling configured
- CI/CD passing
- SonarCloud integrated
- Ready for specification and implementation

### Use Case 2: Auditing Repository Setup

**Actor:** AI Agent or Human Reviewer

**Purpose:** Verify a repository was created correctly

**Flow:**
1. Open verification checklist from spec
2. Check each item
3. Run verification commands
4. Identify any gaps
5. Remediate if needed

**Outcome:** Confidence that repository meets standards

### Use Case 3: Updating Scaffold Procedure

**Actor:** AI Agent Maintainer (Future)

**Trigger:** Learned something new or found an improvement

**Flow:**
1. Read current spec
2. Identify improvement
3. Update spec document
4. Test updated procedure
5. Document change in changelog
6. Commit updated spec

**Outcome:** Procedure improves over time

---

## Constraints

### Technical Constraints

1. **GitHub API Access**
   - Requires `gh` CLI installed
   - Requires GitHub token with appropriate permissions

2. **Repository Naming**
   - Must follow `beast-*` naming convention
   - Should be descriptive and lowercase
   - Should use hyphens not underscores

3. **Python Packaging**
   - Package name should match repo name with underscores
   - Must follow PEP 8 naming conventions
   - Must be unique on PyPI (check before creating)

### Operational Constraints

1. **SonarCloud Limits**
   - Free tier has limits on projects
   - Requires manual project creation in UI
   - Requires organization membership

2. **Token Management**
   - SONAR_TOKEN must be set per repository
   - GitHub token must have repo permissions
   - Tokens stored in ~/.env for reuse

### Quality Constraints

1. **Consistency**
   - All Beast components must have same structure
   - All must meet same quality standards
   - All must use same tooling

2. **Documentation**
   - Every repo must have AGENT.md
   - Every repo must have .spec-workflow/
   - Every repo must have comprehensive README

---

## Success Criteria

### Minimum Viable Specification

1. ✅ Procedure documented step-by-step
2. ✅ Commands copy-paste ready
3. ✅ Checklist provided
4. ✅ Verified with beast-mailbox-agent creation
5. ✅ Stored in .spec-workflow/specs/002-repository-scaffold-procedure/

### Long-Term Success

1. ✅ Used to create 3+ repositories successfully
2. ✅ AI agents can execute without human intervention
3. ✅ New repositories pass all quality gates
4. ✅ Procedure updated based on lessons learned
5. ✅ Zero scaffold-related bugs or gaps

---

## Out of Scope

### Not Included

1. ❌ Implementation of new component (separate spec)
2. ❌ Specification writing for new component
3. ❌ Design decisions for new component
4. ❌ Release procedures (covered elsewhere)
5. ❌ Package publication (separate concern)

---

## Dependencies

### Required Tools

1. **gh CLI** - GitHub command-line tool
2. **git** - Version control
3. **GitHub token** - Classic token with repo permissions
4. **SonarCloud account** - With nkllon organization access
5. **SONAR_TOKEN** - SonarCloud authentication token

### Required Knowledge

1. Beast-mailbox-core structure
2. Python packaging basics
3. GitHub Actions basics
4. SonarCloud basics
5. Git workflows

---

## Risk Assessment

### High Risk

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| Missing critical step | High | Medium | Comprehensive checklist, verification |
| Outdated procedure | High | Medium | Version the spec, update regularly |
| Tool changes | High | Low | Document tool versions, update as needed |

### Medium Risk

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| Token issues | Medium | Medium | Clear token setup docs, troubleshooting |
| SonarCloud confusion | Medium | Low | Step-by-step SonarCloud section |
| Naming conflicts | Medium | Low | Check PyPI before creating |

### Low Risk

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| Incomplete docs | Low | Medium | Iterate based on usage |
| Unclear instructions | Low | Low | Test with fresh eyes |

---

## Related Documents

- **Design Spec:** `./design.md` (includes detailed procedure)
- **AGENT.md:** `/AGENT.md` (updated with reference to this spec)
- **Example:** `beast-mailbox-agent` repository

---

## Approval Status

- [x] **Implementation Complete** - Procedure executed successfully for beast-mailbox-agent
- [ ] **Documentation Complete** - This spec documents the procedure
- [ ] **Tested** - To be validated with next repository creation
- [ ] **Approved** - Pending review

---

## Change Log

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2025-10-14 | 0.1.0 | Reverse-engineered from beast-mailbox-agent creation | AI Agent |

---

## Notes

### Why Reverse-Engineer?

This specification was created **after** successfully creating beast-mailbox-agent. The procedure existed only in:
- Conversation history
- Command history
- The resulting repository

By reverse-engineering it into a formal specification, we:
1. **Captured the knowledge** before it was lost
2. **Made it repeatable** for future components
3. **Enabled validation** via checklist
4. **Documented decisions** and rationale
5. **Created a living document** that can evolve

### Philosophy

> "The best time to document a procedure is right after executing it successfully. The second best time is now."

Requirements truly ARE the solution. This spec enables any AI agent to create a new Beast component repository without human guidance.

---

**End of Requirements Specification**

