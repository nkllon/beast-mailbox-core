# ⚠️ CORRECTED: Python Package Release Procedure

**Last Updated:** 2025-10-10  
**Status:** MANDATORY - This procedure must be followed without exception  
**Supersedes:** Any previous informal or incorrect release procedures

## Incident Report

**Date:** 2025-10-10  
**Package:** beast-mailbox-core  
**Severity:** Critical

### What Happened
Version 0.2.0 was published to PyPI without committing changes to the repository,
creating a complete break in version control integrity and violating supply chain security.

### Lesson Learned
**NEVER publish a package without committing, tagging, and pushing to the repository first.**

---

## The ONLY Correct Release Procedure

### Pre-Release Requirements

Before you even THINK about publishing:

1. ✅ All code changes are committed and pushed to GitHub
2. ✅ All changes have gone through pull request review
3. ✅ All tests pass
4. ✅ No linter errors
5. ✅ Working in the CANONICAL repository (not a fork or alternate clone)

### Release Steps (Must Follow in Order)

#### Step 1: Prepare Release Branch
```bash
# Ensure you're in the correct repository
pwd  # Verify this is the canonical repo location
git remote -v  # Verify origin points to correct GitHub repo

# Update main branch
git checkout main
git pull origin main

# Create release branch
git checkout -b release/v0.X.Y
```

#### Step 2: Update Version and Changelog
```bash
# Edit pyproject.toml - update version line
# Edit CHANGELOG.md - add release notes

git add pyproject.toml CHANGELOG.md
git commit -m "Bump version to 0.X.Y"
git push origin release/v0.X.Y
```

#### Step 3: Create Pull Request
- Create PR from release/v0.X.Y to main
- Title: "Release v0.X.Y"
- Wait for review and approval
- Merge PR

#### Step 4: Tag the Release
```bash
# Pull the merged changes
git checkout main
git pull origin main

# Verify version in pyproject.toml matches intended release
grep "^version" pyproject.toml

# Create annotated tag
git tag -a v0.X.Y -m "Release version 0.X.Y"

# Push tag
git push origin v0.X.Y

# VERIFY tag is on GitHub
git ls-remote --tags origin | grep v0.X.Y
```

#### Step 5: Build Package
```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Install build tools
pip install --upgrade build twine

# Build
python -m build

# Verify built package
tar -tzf dist/beast-mailbox-core-0.X.Y.tar.gz | head -20
```

#### Step 6: Test Publication (REQUIRED)
```bash
# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# Install from Test PyPI and verify
pip install --index-url https://test.pypi.org/simple/ beast-mailbox-core==0.X.Y

# Test basic functionality
beast-mailbox-service --help
beast-mailbox-send --help
```

#### Step 7: Publish to PyPI
```bash
# Only proceed if Test PyPI worked
twine upload dist/*

# Verify on PyPI
pip install beast-mailbox-core==0.X.Y
pip show beast-mailbox-core
```

#### Step 8: Create GitHub Release
```bash
# Use GitHub CLI
gh release create v0.X.Y \
  --title "v0.X.Y" \
  --notes-file CHANGELOG.md

# Or manually:
# Go to https://github.com/nkllon/beast-mailbox-core/releases/new
# - Select tag: v0.X.Y
# - Release title: v0.X.Y
# - Description: Copy from CHANGELOG.md
# - Publish release
```

#### Step 9: Verify Everything
```bash
# Repository check
git log --oneline -5
git tag | grep v0.X.Y

# PyPI check
pip index versions beast-mailbox-core

# GitHub check - verify release exists
gh release view v0.X.Y
```

---

## Critical Rules

### ❌ NEVER DO THESE:

1. **NEVER** publish without pushing commits first
2. **NEVER** publish without creating a git tag
3. **NEVER** publish from a directory that isn't the main repository
4. **NEVER** skip the Test PyPI step
5. **NEVER** skip code review (even for version bumps)
6. **NEVER** rush a release
7. **NEVER** assume you remember the correct procedure

### ✅ ALWAYS DO THESE:

1. **ALWAYS** verify you're in the correct repository directory
2. **ALWAYS** check that git status is clean before tagging
3. **ALWAYS** use Test PyPI first
4. **ALWAYS** verify the tag is pushed before publishing
5. **ALWAYS** create a GitHub Release after publishing
6. **ALWAYS** follow the checklist completely
7. **ALWAYS** update CHANGELOG.md

---

## Verification Questions

Before publishing, answer YES to all:

- [ ] Are all my changes committed?
- [ ] Are all my changes pushed to GitHub?
- [ ] Have my changes been reviewed in a PR?
- [ ] Is the PR merged to main?
- [ ] Am I working in the canonical repository?
- [ ] Have I created and pushed the git tag?
- [ ] Does the tag match the version in pyproject.toml?
- [ ] Have I tested on Test PyPI?
- [ ] Have I verified the package contents?

**If ANY answer is NO, STOP and complete that step first.**

---

## Emergency Contact

If confused or uncertain at ANY point:
1. STOP immediately
2. Do NOT publish
3. Ask for help
4. Review this document again

---

## Automation (Future)

To prevent human error, we should implement:
- GitHub Actions to automate releases from tags
- Pre-commit hooks to verify version consistency
- Automated tests on release branches
- Automated GitHub Release creation

Until automation is in place, follow this manual procedure without deviation.

---

## Incident Timeline - v0.2.0

**What went wrong:**
- v0.2.0 was built and published from non-canonical directory
- No commits pushed to repository
- No git tag created
- No GitHub release
- Source code unavailable for 4 hours

**How it was fixed:**
1. Identified source location of v0.2.0 code
2. Created fix/sync-repo-with-v0.2.0 branch
3. Applied all changes with proper documentation
4. Created PR #1 with full accountability
5. Merged PR to restore integrity
6. Created v0.2.0 tag retroactively
7. Created GitHub Release with full transparency
8. Updated release procedures (this document)

**Lessons learned:**
- Git-first principle is non-negotiable
- Multiple directory clones are dangerous
- Need automated guardrails
- Process documentation is critical

---

**This procedure was created in response to a critical incident on 2025-10-10.**  
**Following it is not optional.**

**Completed remediation:**
- ✅ Repository synchronized with PyPI
- ✅ Git tag v0.2.0 created and pushed
- ✅ GitHub Release created
- ✅ Corrected procedures documented
- ✅ Incident transparently documented in CHANGELOG


