# Diagnostic Scripts

This directory contains diagnostic and utility scripts for the beast-mailbox-core project.

## Tools Overview

### Diagnostic Tools

#### `diagnose_pr.py` - PR Failure Diagnostic Tool

Comprehensive diagnostic tool for investigating GitHub PR failures, especially Dependabot PRs.

**Features**:
- Fetches PR information and file changes
- Analyzes dependency version changes
- Checks CI workflow run status and failures
- Checks SonarCloud quality gate status
- Identifies failed workflow jobs and steps
- Provides actionable diagnostic information

**Usage**:
```bash
# Basic usage
python scripts/diagnose_pr.py <pr_number>

# JSON output
python scripts/diagnose_pr.py <pr_number> --json

# Custom repository
python scripts/diagnose_pr.py <pr_number> --repo owner/repo

# Custom token (or set GITHUB_TOKEN env var)
python scripts/diagnose_pr.py <pr_number> --token <github_token>
```

**Requirements**:
- `requests` library: `pip install requests`
- GitHub token (set `GITHUB_TOKEN` env var or use `--token`)
- SonarCloud token (set `SONAR_TOKEN` env var for quality gate checks)

**Example**:
```bash
export GITHUB_TOKEN=ghp_...
export SONAR_TOKEN=...
python scripts/diagnose_pr.py 10
```

---

#### `analyze_dependencies.py` - Dependency Conflict Analyzer

Analyzes dependency version constraints and identifies potential conflicts.

**Features**:
- Parses dependency constraints from `pyproject.toml`
- Identifies pinned versions vs range constraints
- Checks lock file status
- Optional security vulnerability checking (requires `pip-audit`)

**Usage**:
```bash
# Basic analysis
python scripts/analyze_dependencies.py

# With security check
python scripts/analyze_dependencies.py --check-security

# JSON output
python scripts/analyze_dependencies.py --json
```

**Requirements**:
- `tomli` library: `pip install tomli` (or use Python 3.11+ with built-in `tomllib`)
- Optional: `pip-audit` for security checks: `pip install pip-audit`

**Example**:
```bash
python scripts/analyze_dependencies.py --check-security
```

### Management Tools

#### `manage_workflows.py` - CI Configuration Management Tool

Manages GitHub Actions workflow configurations: reads, analyzes, and updates workflows.

**Features**:
- List all workflows
- Analyze workflow structure (triggers, jobs, actions, permissions)
- Update action versions in workflows
- Validate workflow YAML syntax
- List action versions used in workflows

**Usage**:
```bash
# List all workflows
python scripts/manage_workflows.py list

# Analyze a workflow
python scripts/manage_workflows.py analyze sonarcloud

# Update action version
python scripts/manage_workflows.py update-action sonarcloud actions/checkout v4

# Validate all workflows
python scripts/manage_workflows.py validate

# List action versions in a workflow
python scripts/manage_workflows.py versions sonarcloud
```

**Requirements**:
- `pyyaml` library: `pip install pyyaml`

---

#### `monitor_workflows.py` - Workflow Monitoring Tool

Monitors GitHub Actions workflow status and quality metrics.

**Features**:
- Check workflow run status (success/failure rates)
- Monitor quality metrics from history.json
- Check SonarCloud quality gate status
- Detect alert conditions (high failure rates, quality issues)

**Usage**:
```bash
# Check workflow status
python scripts/monitor_workflows.py status

# Check quality metrics
python scripts/monitor_workflows.py quality

# Check for alerts
python scripts/monitor_workflows.py alerts

# Monitor specific workflow
python scripts/monitor_workflows.py status --workflow "SonarCloud Analysis"

# JSON output
python scripts/monitor_workflows.py status --json
```

**Requirements**:
- `requests` library: `pip install requests`
- GitHub token (set `GITHUB_TOKEN` env var)
- SonarCloud token (set `SONAR_TOKEN` env var for quality checks)

**Example**:
```bash
export GITHUB_TOKEN=ghp_...
export SONAR_TOKEN=...
python scripts/monitor_workflows.py alerts
```

---

## Installation

Install required dependencies:

```bash
# Core dependencies
pip install requests tomli pyyaml

# Optional: for security checks
pip install pip-audit
```

## Environment Variables

Set these environment variables for full functionality:

- `GITHUB_TOKEN`: GitHub personal access token with `repo` scope
- `SONAR_TOKEN`: SonarCloud authentication token (for quality gate checks)

## Integration with CI/CD

These scripts can be used in CI/CD pipelines or locally for debugging:

```yaml
# Example GitHub Actions usage
- name: Diagnose PR
  run: |
    pip install requests tomli
    python scripts/diagnose_pr.py ${{ github.event.pull_request.number }} --json > pr_report.json
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

## Troubleshooting

### diagnose_pr.py

**Issue**: "GITHUB_TOKEN not set"
- **Solution**: Set `GITHUB_TOKEN` environment variable or use `--token` flag

**Issue**: "requests library required"
- **Solution**: Install with `pip install requests`

**Issue**: PR not found
- **Solution**: Verify PR number and repository name are correct

### analyze_dependencies.py

**Issue**: "tomli library required"
- **Solution**: Install with `pip install tomli` or use Python 3.11+

**Issue**: "pip-audit not available"
- **Solution**: Install with `pip install pip-audit` or skip `--check-security` flag

---

## Related Documentation

- [GitHub Workflows Documentation](../.github/workflows/README.md)
- [AGENT.md](../AGENT.md) - Development guidelines
- [Dependabot Troubleshooting](../AGENT.md#dependabot-pr-failures) - Troubleshooting guide

