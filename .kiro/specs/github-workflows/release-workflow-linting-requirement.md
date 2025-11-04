# Release Workflow: Linting Requirement

## Problem Statement

**User Requirement**: If you commit anything with Black or Ruff errors, the commit trigger will stop it. So unless you're sure that you're clean before you commit and push, you cannot cut a release.

## Current State

### Linting Enforcement
- **Black**: Formatting tool (Python code formatter)
- **Ruff**: Linting tool (Python linter)
- **Current Behavior**: Commits with Black/Ruff errors are blocked by CI/CD
- **Impact on Releases**: Cannot cut a release if code has linting errors

### Missing from Release Validation
- **No explicit Black check** in release workflow
- **No explicit Ruff check** in release workflow
- **Risk**: Attempting to cut a release with linting errors will fail

## Requirement

### REQ-L1: Linting Validation in Release Workflow
- **REQ-L1.1**: Release validation workflow MUST check Black formatting
- **REQ-L1.2**: Release validation workflow MUST check Ruff linting
- **REQ-L1.3**: Release validation MUST FAIL if Black or Ruff errors exist
- **REQ-L1.4**: Release validation MUST provide clear error messages for linting failures
- **REQ-L1.5**: Release validation SHOULD suggest how to fix linting errors

## Implementation

### Black Check
```yaml
- name: Check Black formatting
  run: |
    pip install black
    black --check .
```

**Failure Behavior**: 
- Workflow fails if Black finds formatting issues
- User must run `black .` to fix, then re-run validation

### Ruff Check
```yaml
- name: Check Ruff linting
  run: |
    pip install ruff
    ruff check .
```

**Failure Behavior**:
- Workflow fails if Ruff finds linting issues
- User must fix issues, then re-run validation

### Combined Check (Recommended)
```yaml
- name: Install linting tools
  run: |
    pip install black ruff

- name: Check code formatting and linting
  run: |
    echo "Checking Black formatting..."
    black --check . || (echo "❌ Black formatting errors found. Run 'black .' to fix." && exit 1)
    
    echo "Checking Ruff linting..."
    ruff check . || (echo "❌ Ruff linting errors found. Run 'ruff check . --fix' or fix manually." && exit 1)
    
    echo "✅ All linting checks passed"
```

## Integration with Release Validation

### Workflow Order
1. Install dependencies (including Black and Ruff)
2. Run Black check
3. Run Ruff check
4. Run tests
5. Check coverage
6. Check SonarCloud Quality Gate
7. Validate version/changelog
8. Validate git state

### Failure Handling
- **If Black fails**: Workflow stops, user fixes formatting, re-runs validation
- **If Ruff fails**: Workflow stops, user fixes linting, re-runs validation
- **Clear error messages**: Tell user exactly what failed and how to fix

## Benefits

1. **Prevents Bad Releases**: Cannot cut release with linting errors
2. **Early Detection**: Catches linting issues before release attempt
3. **Consistency**: Ensures all releases have clean, formatted code
4. **Developer Experience**: Clear error messages guide fixing

## Dependencies

### Required Tools
- **Black**: Python code formatter
- **Ruff**: Python linter

### Installation
- Add to `dev` dependencies in `pyproject.toml` (if not already present)
- Install in workflow: `pip install black ruff`

## Configuration

### Black Configuration
- Uses default Black settings
- Checks all Python files in repository
- Can be configured via `pyproject.toml` `[tool.black]` section

### Ruff Configuration
- Uses default Ruff settings
- Checks all Python files in repository
- Can be configured via `pyproject.toml` `[tool.ruff]` section

## Questions to Resolve

1. **Should Black/Ruff be in dev dependencies?**
   - **Recommendation**: YES - add to `[project.optional-dependencies.dev]` in `pyproject.toml`

2. **Should we auto-fix linting errors?**
   - **Recommendation**: NO - validation should check only, user fixes manually
   - **Rationale**: Prevents unexpected changes, maintains control

3. **Should we check Swift linting?**
   - **Recommendation**: YES - if Swift code exists, add Swift linting checks too
   - **Implementation**: Add SwiftLint or similar if Swift code is present

4. **Should linting checks run on every push?**
   - **Recommendation**: YES - add linting workflow that runs on push/PR
   - **Current**: Linting may be enforced by branch protection or other CI
   - **Action**: Investigate existing linting enforcement mechanism

## Next Steps

1. ✅ Add Black/Ruff checks to release validation workflow design
2. ⚠️ **Investigate**: How are Black/Ruff currently enforced? (pre-commit? workflow? branch protection?)
3. ⚠️ **Update**: Add linting validation to release workflow implementation
4. ⚠️ **Consider**: Add standalone linting workflow for push/PR events

