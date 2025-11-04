# GitHub Workflows System Specification

## Overview

This specification defines the complete architecture, dependencies, and behavior of the GitHub Actions workflow system for the beast-mailbox-core project.

## Documents

1. **requirements.md**: Functional requirements for all workflows
2. **dag.md**: Dependency graph (DAG) visualization and analysis
3. **design.md**: Architectural design and implementation details
4. **release-workflow-analysis.md**: Analysis of current release process
5. **release-workflow-design.md**: Design specification for release workflow
6. **conflicts-and-issues.md**: Issues and recommendations
7. **README.md**: This overview document

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
2. Artifact action version mismatch (v4 vs v5)
3. Quality metrics commit conflicts
4. Missing branch protection rules
5. Swift metrics not tracked

## Next Steps

1. Review and approve this specification
2. Implement fixes for identified issues
3. Add branch protection rules
4. Update workflow documentation
5. Test end-to-end workflow execution

