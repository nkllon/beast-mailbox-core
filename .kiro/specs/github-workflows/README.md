# GitHub Workflows System Specification

## Overview

This specification defines the complete architecture, dependencies, and behavior of the GitHub Actions workflow system for the beast-mailbox-core project.

## Documents

### Core Workflow Specifications
1. **requirements.md**: Comprehensive functional requirements for all workflows (includes Dependabot requirements merged from dependabot-requirements.md)
2. **dag.md**: Dependency graph (DAG) visualization and analysis
3. **design.md**: Architectural design and implementation details
4. **release-workflow-analysis.md**: Analysis of current release process
5. **release-workflow-design.md**: Design specification for release workflow
6. **conflicts-and-issues.md**: Issues and recommendations
7. **tasks.md**: Implementation tasks for workflow system
8. **summary.md**: Summary of workflow system

### Dependabot PR Fix Specifications
9. **dependabot-requirements.md**: ⚠️ **SUPERSEDED** - Requirements merged into `requirements.md` (kept for historical reference)
10. **dependabot-design.md**: ⚠️ **SUPERSEDED** - Design merged into `design.md` (kept for historical reference)
11. **dependabot-tasks.md**: Implementation plan for Dependabot PR fix
12. **dependabot-review.md**: Spec review and compliance analysis
13. **dependabot-investigation-report.md**: Investigation report for PR #10
14. **dependabot-implementation-summary.md**: Summary of implementation completion
15. **dependabot-system-test-report.md**: Comprehensive system test results
16. **dependabot-testing-plan.md**: Testing strategy for Dependabot fixes

### Reference
17. **README.md**: This overview document

## Quick Reference

### Workflow Dependencies
```
Dependabot → PRs → SonarCloud Analysis → Quality Metrics → Prometheus Export
                                    ↓
                              Prometheus Export
```

### External Services
- **SonarCloud**: Code quality analysis
- **Prometheus Pushgateway**: Metrics collection
- **PyPI**: Package publishing
- **GitHub**: Repository hosting and API

### Key Issues Identified
1. Prometheus export triggers multiple times per push
2. Artifact action version mismatch (v4 vs v5) - **FIXED** (see dependabot-investigation-report.md)
3. Quality metrics commit conflicts - **FIXED** (permissions added to workflow)
4. Missing branch protection rules
5. Swift metrics not tracked
6. Swift workflow build cache issues - **FIXED** (see dependabot-implementation-summary.md)

## Dependabot PR Fix Status

**Status:** ✅ **COMPLETE** (see dependabot-implementation-summary.md)

The Dependabot PR #10 fix has been completed. Key achievements:
- ✅ Fixed Swift workflow build cache issues
- ✅ Added build artifact cleanup
- ✅ Added project type detection (Swift PM vs Xcode)
- ✅ Updated AGENT.md with troubleshooting guidance

For details, see:
- `dependabot-investigation-report.md` - Root cause analysis
- `dependabot-implementation-summary.md` - Implementation summary
- `dependabot-system-test-report.md` - Test validation results

## Next Steps

1. Review and approve this specification
2. Implement remaining fixes for identified issues
3. Add branch protection rules
4. Update workflow documentation
5. Test end-to-end workflow execution

