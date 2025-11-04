# Branch Protection and Monitoring Configuration

This document describes the recommended branch protection rules and monitoring setup for the beast-mailbox-core repository.

## Branch Protection Rules

### Main Branch Protection

**Location**: GitHub Repository Settings → Branches → Branch protection rules

#### Recommended Settings

1. **Require a pull request before merging**
   - ✅ Enabled
   - Require approvals: **1**
   - Dismiss stale pull request approvals when new commits are pushed: ✅ Enabled
   - Require review from Code Owners: ⚠️ Optional (if CODEOWNERS file exists)

2. **Require status checks to pass before merging**
   - ✅ Enabled
   - Required status checks:
     - ✅ `SonarCloud Analysis` (Python workflow)
     - ✅ `Release Validation` (if applicable)
   - Require branches to be up to date before merging: ✅ Enabled

3. **Require conversation resolution before merging**
   - ✅ Enabled
   - All comments must be resolved

4. **Do not allow bypassing the above settings**
   - ✅ Enabled (for administrators)
   - ⚠️ Consider allowing bypass for emergencies (with audit trail)

5. **Require linear history**
   - ⚠️ Optional (prefer rebase/merge, not squash)

6. **Include administrators**
   - ✅ Enabled (apply rules to administrators)

### Dependabot PR Requirements

Dependabot PRs must:
- ✅ Pass all required status checks
- ✅ Pass SonarCloud Quality Gate
- ✅ Have test coverage ≥ 85%
- ✅ Have zero bugs and zero code smells

### Branch Protection Configuration Commands

```bash
# View current branch protection (requires GitHub CLI)
gh api repos/:owner/:repo/branches/main/protection

# Set branch protection (requires GitHub CLI and admin access)
gh api repos/:owner/:repo/branches/main/protection \
  -X PUT \
  -f required_status_checks='{"strict":true,"contexts":["SonarCloud Analysis"]}' \
  -f enforce_admins=true \
  -f required_pull_request_reviews='{"dismissal_restrictions":{},"dismiss_stale_reviews":true,"require_code_owner_reviews":false,"required_approving_review_count":1}' \
  -f restrictions=null
```

**Note**: Branch protection rules are repository settings, not code. They must be configured via GitHub UI or API.

---

## Workflow Monitoring

### Current Monitoring Capabilities

1. **Prometheus Metrics Export**
   - Workflow metrics exported to Prometheus Pushgateway
   - Includes: workflow runs, duration, status, branch
   - Location: `.github/workflows/prometheus-metrics.yml`

2. **Quality Metrics Tracking**
   - Quality metrics committed to `metrics/history.json`
   - Includes: coverage, bugs, vulnerabilities, code smells
   - Location: `.github/workflows/quality-metrics.yml`

3. **GitHub Actions Dashboard**
   - Built-in workflow run history
   - URL: `https://github.com/[owner]/[repo]/actions`

### Monitoring Setup

#### 1. Prometheus Monitoring

**Prerequisites**:
- Prometheus server configured
- Pushgateway endpoint available
- Secrets configured: `PROMETHEUS_PUSHGATEWAY_URL`, `PROMETHEUS_PUSHGATEWAY_AUTH`

**Metrics Available**:
- `github_workflow_runs_total` - Total workflow runs by status
- `github_workflow_duration_seconds` - Workflow execution duration
- `sonarcloud_coverage_percent` - Code coverage percentage
- `sonarcloud_bugs_total` - Total bugs
- `sonarcloud_quality_gate_status` - Quality gate status (1=OK, 0=ERROR)

**Query Examples**:
```promql
# Workflow failure rate
rate(github_workflow_runs_total{status="failure"}[5m])

# Average workflow duration
avg(github_workflow_duration_seconds)

# Quality gate status
sonarcloud_quality_gate_status
```

#### 2. Grafana Dashboard

**Recommended Panels**:
- Workflow success/failure rate
- Average workflow duration
- SonarCloud quality metrics
- Test coverage trends
- Bug count over time

**Dashboard JSON**: Available in `docs/grafana-quality-dashboard.json`

#### 3. Alerting

**Recommended Alerts**:

1. **Workflow Failure Rate**
   ```promql
   rate(github_workflow_runs_total{status="failure"}[5m]) > 0.1
   ```
   - Alert when failure rate > 10%

2. **Quality Gate Failure**
   ```promql
   sonarcloud_quality_gate_status == 0
   ```
   - Alert when quality gate fails

3. **Coverage Below Threshold**
   ```promql
   sonarcloud_coverage_percent < 85
   ```
   - Alert when coverage < 85%

4. **Bugs Detected**
   ```promql
   sonarcloud_bugs_total > 0
   ```
   - Alert when bugs detected

### Monitoring Script

A simple monitoring script can be created to check workflow status:

```python
#!/usr/bin/env python3
"""Workflow Monitoring Script"""
# See scripts/monitor_workflows.py (if created)
```

---

## Workflow Status Monitoring

### Manual Monitoring

1. **Check Workflow Runs**
   ```bash
   # List recent workflow runs
   gh run list --limit 10
   
   # View specific workflow run
   gh run view <run-id>
   
   # Watch workflow run
   gh run watch <run-id>
   ```

2. **Check Quality Metrics**
   ```bash
   # View quality metrics history
   cat metrics/history.json | jq '.history | .[-10:]'
   
   # View summary
   cat metrics/README.md
   ```

3. **Check SonarCloud Dashboard**
   - URL: `https://sonarcloud.io/project/overview?id=nkllon_beast-mailbox-core`
   - Check quality gate status
   - Review metrics trends

### Automated Monitoring

**GitHub Actions Status API**:
```bash
# Get workflow status
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/[owner]/[repo]/actions/runs
```

**SonarCloud API**:
```bash
# Get quality gate status
curl -u "$SONAR_TOKEN:" \
  "https://sonarcloud.io/api/measures/component?component=nkllon_beast-mailbox-core&metricKeys=alert_status"
```

---

## Notification Setup

### Recommended Notifications

1. **Workflow Failures**
   - GitHub email notifications (enabled by default)
   - Slack/Discord webhook (if configured)
   - Prometheus alerts (if alertmanager configured)

2. **Quality Gate Failures**
   - SonarCloud email notifications
   - GitHub status checks (visible in PR)

3. **Dependabot PR Failures**
   - GitHub email notifications
   - Use `scripts/diagnose_pr.py` for detailed analysis

### Notification Configuration

**GitHub Notifications**:
- Settings → Notifications → Actions
- Enable: Workflow runs, Failed workflows

**SonarCloud Notifications**:
- Project Settings → Notifications
- Enable: Quality gate changes, New issues

---

## Current Configuration Status

**Note**: This document describes recommended settings. Actual configuration may vary.

### Branch Protection Status

To check current branch protection:
```bash
gh api repos/:owner/:repo/branches/main/protection
```

### Monitoring Status

To check monitoring setup:
- ✅ Prometheus metrics export: Active (see `.github/workflows/prometheus-metrics.yml`)
- ✅ Quality metrics tracking: Active (see `.github/workflows/quality-metrics.yml`)
- ⚠️ Alerting: Requires Prometheus Alertmanager configuration
- ⚠️ Grafana dashboard: See `docs/grafana-quality-dashboard.json`

---

## Maintenance

### Regular Tasks

1. **Review Workflow Runs** (Weekly)
   - Check for recurring failures
   - Review performance trends
   - Update workflows if needed

2. **Review Quality Metrics** (Weekly)
   - Check coverage trends
   - Review bug/code smell counts
   - Address quality regressions

3. **Review Branch Protection** (Monthly)
   - Verify rules are still appropriate
   - Update required status checks if workflows change
   - Review bypass permissions

### Documentation Updates

- Update this document when branch protection rules change
- Update monitoring setup when new metrics are added
- Document alert thresholds and notification channels

---

**Last Updated**: 2025-01-31  
**Maintained By**: Project maintainers  
**Note**: Branch protection settings must be configured via GitHub UI/API, not in code

