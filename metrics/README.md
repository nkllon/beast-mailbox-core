# Quality Metrics History

This directory tracks quality metrics over time from SonarCloud analysis.

## Current Status

**Last Updated:** 2025-11-04 16:25:25 UTC

| Metric | Current Value | Target | Status |
|--------|--------------|--------|--------|
| Coverage | 89.5% | ≥ 80% | ✅ |
| Bugs | 0 | 0 | ✅ |
| Vulnerabilities | 0 | 0 | ✅ |
| Code Smells | 0 | 0 | ✅ |
| Reliability | A | ≤ A | ✅ |
| Security | A | ≤ A | ✅ |
| Maintainability | A | ≤ A | ✅ |

## Data Files

- `history.json` - Complete metrics history (JSON format, last 100 entries)
- `README.md` - This summary (auto-generated on each SonarCloud run)

## Usage

To view recent trends:
```bash
cat metrics/history.json | jq '.history | .[-10:] | .[] | {date: .timestamp, coverage: .metrics.coverage, bugs: .metrics.bugs}'
```

To plot coverage over time:
```bash
cat metrics/history.json | jq -r '.history[] | "\(.timestamp),\(.metrics.coverage)"'
```

To see all entries:
```bash
cat metrics/history.json | jq '.history | length'
```
