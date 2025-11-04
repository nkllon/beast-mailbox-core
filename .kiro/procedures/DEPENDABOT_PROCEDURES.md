# Dependabot PR Procedures

This document provides comprehensive procedures for handling Dependabot PR failures, following AGENT.md requirements-first principles.

## Overview

When a Dependabot PR fails, follow these procedures systematically to investigate, resolve, and prevent future failures.

## Procedure 4.3: Dependabot PR Failure Investigation

### Purpose

Systematically identify the root cause of Dependabot PR failures.

### Tools Available

- `scripts/diagnose_pr.py` - Comprehensive PR diagnostic tool
- `scripts/analyze_dependencies.py` - Dependency constraint analyzer
- GitHub CLI (`gh`) - Repository and PR queries
- SonarCloud API - Quality gate status

### Investigation Steps

1. **Verify PR Existence and State**
   ```bash
   # Use diagnostic tool
   python scripts/diagnose_pr.py <pr_number>
   
   # Or manually
   gh pr view <pr_number>
   ```

2. **Analyze Dependency Changes**
   ```bash
   # Use diagnostic tool (includes dependency analysis)
   python scripts/diagnose_pr.py <pr_number> --json > pr_analysis.json
   
   # Or analyze current dependencies
   python scripts/analyze_dependencies.py
   ```

3. **Check CI Pipeline Status**
   ```bash
   # Diagnostic tool includes workflow failures
   python scripts/diagnose_pr.py <pr_number>
   
   # Or manually check workflow runs
   gh run list --workflow="SonarCloud Analysis"
   ```

4. **Check SonarCloud Quality Gate**
   ```bash
   # Diagnostic tool checks quality gate
   python scripts/diagnose_pr.py <pr_number>
   
   # Or check manually
   curl -s "https://sonarcloud.io/api/measures/component?component=nkllon_beast-mailbox-core&metricKeys=alert_status" \
     -u "$SONAR_TOKEN:"
   ```

5. **Identify Test Failures**
   - Review workflow logs for failed tests
   - Check test output in CI logs
   - Identify specific test failures

6. **Document Root Cause**
   - Create investigation report: `.kiro/specs/dependabot-pr-[number]/investigation.md`
   - Document:
     - PR details
     - Dependency changes
     - Workflow failures
     - Test failures
     - Quality gate status
     - Root cause analysis

### Investigation Report Template

```markdown
# Dependabot PR #X Investigation Report

**Date**: [Date]
**PR**: #[number] - [Title]
**Status**: [Investigation Complete/Failed]

## Executive Summary
[Brief summary of findings]

## PR Details
- Number: #[number]
- Title: [Title]
- Author: Dependabot
- State: [open/closed]
- URL: [URL]

## Dependency Changes
[From diagnose_pr.py output]

## Workflow Failures
[From diagnose_pr.py output]

## Test Failures
[Specific test failures identified]

## SonarCloud Quality Gate
[Status and metrics]

## Root Cause Analysis
[Detailed root cause]

## Recommended Fixes
[Proposed solutions]
```

---

## Procedure 4.4: Dependabot PR Resolution

### Purpose

Resolve Dependabot PR failures systematically.

### Resolution Steps

1. **Ensure Test Suite Passes**
   ```bash
   # Run tests locally with updated dependencies
   pip install -e ".[dev]"
   pytest tests/ --cov=src/beast_mailbox_core
   
   # Check coverage meets 85% threshold
   coverage report --fail-under=85
   ```

2. **Fix Dependency Conflicts**
   ```bash
   # Analyze conflicts
   python scripts/analyze_dependencies.py
   
   # Update pyproject.toml with compatible versions
   # Strategy: relaxation → pinning → exclusion
   ```

3. **Update Code for API Changes**
   - Review dependency changelogs
   - Update code to match new API
   - Update tests if needed

4. **Verify SonarCloud Quality Gate**
   ```bash
   # Check quality gate after fixes
   python scripts/diagnose_pr.py <pr_number>
   ```

5. **Ensure Coverage ≥ 85%**
   ```bash
   pytest tests/ --cov=src/beast_mailbox_core --cov-report=term
   # Verify coverage ≥ 85%
   ```

6. **Create Actionable Feedback**
   - Update PR with clear status
   - Document fixes made
   - Provide clear next steps if additional fixes needed

### Resolution Checklist

- [ ] All tests pass locally
- [ ] Coverage ≥ 85%
- [ ] SonarCloud quality gate passes
- [ ] Dependency conflicts resolved
- [ ] Code updated for API changes
- [ ] PR updated with status

---

## Procedure 4.5: Preventive Measures

### Purpose

Prevent similar Dependabot failures in the future.

### Preventive Steps

1. **Address Root Cause Completely**
   - Fix underlying issues, not just symptoms
   - Update configurations to prevent recurrence
   - Document lessons learned

2. **Maintain Backward Compatibility**
   - Test with existing codebase
   - Ensure no breaking changes
   - Document migration notes if needed

3. **Update Configuration**
   - Update `pyproject.toml` with compatible versions
   - Update workflow files if needed
   - Document configuration decisions

4. **Validate Fixes**
   ```bash
   # Run full validation
   pytest tests/ --cov=src/beast_mailbox_core
   black --check .
   ruff check .
   ```

5. **Document Preventive Measures**
   - Update AGENT.md if needed
   - Document in investigation report
   - Create procedures if recurring issue

---

## Procedure 4.6: Quality Assurance

### Purpose

Ensure dependency updates maintain code quality standards.

### Quality Checks

1. **Test Coverage ≥ 85%**
   ```bash
   pytest tests/ --cov=src/beast_mailbox_core --cov-report=term
   coverage report --fail-under=85
   ```

2. **SonarCloud Quality Gate**
   - Zero bugs
   - Zero code smells
   - Coverage ≥ 85%
   - Ratings: A for reliability, security, maintainability

3. **Comment Density ≥ 25%**
   - Check SonarCloud metrics
   - Add comments if needed

4. **Security Vulnerabilities**
   ```bash
   # Check for vulnerabilities
   python scripts/analyze_dependencies.py --check-security
   
   # Or use pip-audit directly
   pip-audit
   ```

5. **Code Quality Metrics**
   - Check SonarCloud dashboard
   - Verify no regressions
   - Maintain quality thresholds

### Quality Checklist

- [ ] Test coverage ≥ 85%
- [ ] Zero bugs (SonarCloud)
- [ ] Zero code smells (SonarCloud)
- [ ] Comment density ≥ 25%
- [ ] No security vulnerabilities
- [ ] Quality ratings: A/A/A

---

## Procedure 4.7: Error Recovery Strategies

### Purpose

Systematic recovery strategies for different failure types.

### Recovery Strategies by Failure Type

#### 1. Dependency Version Conflicts

**Strategy**: Relaxation → Pinning → Exclusion

1. **Relaxation** (First attempt)
   ```toml
   # Change from
   package>=1.0.0,<2.0.0
   # To
   package>=1.0.0,<3.0.0
   ```

2. **Pinning** (If relaxation fails)
   ```toml
   # Pin to specific version
   package==1.2.3
   ```

3. **Exclusion** (Last resort)
   ```toml
   # Exclude problematic dependency
   # Or use alternative package
   ```

#### 2. Test Failures (API Changes)

1. **Update Test Mocks**
   - Review dependency changelog
   - Update mocks to match new API
   - Update assertions

2. **Update Code**
   - Update code to match new API
   - Maintain backward compatibility if possible

#### 3. Non-Critical Test Failures

1. **Skip with TODO**
   ```python
   @pytest.mark.skip(reason="TODO: Fix after dependency update")
   def test_something():
       ...
   ```

2. **Document in Investigation Report**
   - Explain why test is skipped
   - Plan fix for next iteration

#### 4. SonarCloud Quality Gate Failures

1. **Critical Bugs** (Immediate)
   - Fix bugs immediately
   - Block merge until fixed

2. **Code Smells** (Planned)
   - Document in investigation report
   - Plan fix for next iteration
   - Don't block merge if non-critical

#### 5. CI Configuration Issues

1. **Update GitHub Actions Versions**
   ```yaml
   # Update action versions
   - uses: actions/checkout@v4  # Update to latest
   ```

2. **Fallback to Previous Working Config**
   - If update fails, revert to previous working version
   - Document issue for future investigation

#### 6. Clear Commit History

- One commit per fix type
- Clear commit messages
- Easy rollback if needed

---

## Procedure 4.8: Testing and Validation

### Purpose

Comprehensive testing of dependency updates.

### Testing Steps

1. **Local Testing**
   ```bash
   # Install updated dependencies
   pip install -e ".[dev]"
   
   # Run tests
   pytest tests/ --cov=src/beast_mailbox_core
   
   # Check formatting
   black --check .
   ruff check .
   ```

2. **Dependency Compatibility**
   ```bash
   # Analyze dependencies
   python scripts/analyze_dependencies.py
   
   # Check lock file
   uv sync --dry-run
   ```

3. **API Compatibility**
   - Review dependency changelogs
   - Check for breaking changes
   - Test public API usage

4. **Integration Testing**
   - Run full test suite
   - Test end-to-end workflows
   - Verify CI pipeline

5. **Regression Testing**
   - Run existing tests
   - Verify no functionality regressions
   - Check performance

6. **Security Testing**
   ```bash
   # Check vulnerabilities
   python scripts/analyze_dependencies.py --check-security
   ```

### Validation Checklist

- [ ] All tests pass locally
- [ ] Dependencies compatible
- [ ] No API breaking changes
- [ ] Integration tests pass
- [ ] No regressions
- [ ] No security vulnerabilities

---

## Procedure 4.9: Risk Mitigation

### Purpose

Mitigate risks associated with dependency updates.

### Risk Mitigation Strategies

1. **Version Compatibility Matrix**
   - Document known compatible versions
   - Maintain in `.kiro/docs/dependency-compatibility.md`

2. **Comprehensive Regression Testing**
   - Full test suite execution
   - Integration tests
   - Performance tests

3. **Quality Gate Monitoring**
   - Monitor SonarCloud metrics
   - Set up alerts for quality regressions

4. **Prioritize Critical Fixes**
   - Fix critical bugs first
   - Defer nice-to-have improvements

5. **Small, Testable Increments**
   - One dependency update per PR
   - Test each update individually
   - Avoid large batch updates

### Risk Mitigation Checklist

- [ ] Compatibility matrix updated
- [ ] Regression tests executed
- [ ] Quality gates monitored
- [ ] Critical fixes prioritized
- [ ] Changes in small increments

---

## Quick Reference

### Investigation Tools
- `scripts/diagnose_pr.py <pr_number>` - PR diagnostic
- `scripts/analyze_dependencies.py` - Dependency analysis

### Quality Checks
- `pytest tests/ --cov` - Test coverage
- `black --check .` - Formatting
- `ruff check .` - Linting
- SonarCloud dashboard - Quality gate

### Recovery Priority
1. Critical bugs (blocking)
2. Test failures (blocking)
3. Dependency conflicts (blocking)
4. Code smells (non-blocking)
5. Nice-to-have improvements (non-blocking)

---

**Last Updated**: 2025-01-31  
**Maintained By**: Project maintainers

