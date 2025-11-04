# Release Workflow: Authentication Note

## Context

During the implementation of the release validation workflow, it was noted that the `quality-metrics.yml` workflow had authentication errors that were fixed by:

1. Adding `permissions: contents: write` to the job
2. Adding `persist-credentials: true` to the checkout step
3. Explicitly passing `token: ${{ secrets.GITHUB_TOKEN }}` to checkout

## Reference

**File**: `.github/workflows/quality-metrics.yml`
**Commit**: `fea0355` - "fix: Pass metrics via environment variables in workflow"

**Changes Applied**:
```yaml
permissions:
  contents: write

- uses: actions/checkout@v4
  with:
    fetch-depth: 0
    token: ${{ secrets.GITHUB_TOKEN }}
    persist-credentials: true
```

## Application to Release Validation Workflow

The release validation workflow (`release-validation.yml`) is configured with:
- `permissions: contents: read` (read-only since it doesn't commit)
- `token: ${{ secrets.GITHUB_TOKEN }}` in checkout (for authentication)

This ensures the workflow can:
- Checkout code
- Read repository contents
- Check git status
- Verify tags exist
- Avoid authentication errors

## Lesson Learned

When creating workflows that interact with the repository:
1. **Always specify permissions** explicitly - don't rely on defaults
2. **Use token in checkout** if you need to access repository information
3. **Read-only permissions** are sufficient for validation workflows
4. **Write permissions** only needed if workflow commits changes

## Related Workflows

- **Quality Metrics Tracking**: Requires `contents: write` (commits metrics)
- **Release Validation**: Requires `contents: read` (only reads/validates)
- **Publish to PyPI**: May require `contents: read` (reads version/tag info)

