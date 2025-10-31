# SonarCloud Migration Guide - When Splitting to Separate Repo

## Current State (beast-mailbox-core)

**Status:** Using shared SonarCloud setup
- ✅ Can use existing `SONAR_TOKEN` from GitHub Secrets
- ✅ Project: `nkllon_beast-observatory-swift` (within same org)
- ✅ No additional setup needed now

## Future State (beast-observatory repo)

When Observatory is split to `github.com/nkllon/beast-observatory`:

### What Changes

1. **New SonarCloud Project**
   - Will need its own project: `nkllon_beast-observatory`
   - Or: `nkllon_observatory` (shorter)
   - Cannot reuse `beast-mailbox-core` project

2. **New GitHub Token**
   - Cannot use `SONAR_TOKEN` from `beast-mailbox-core` repo
   - Must create new token in SonarCloud
   - Must add to new repo's GitHub Secrets

3. **Configuration Files**
   - `sonar-project.properties` stays the same (just update project key)
   - GitHub Actions workflow stays the same (just update paths)

## Migration Steps (When Ready to Split)

### Step 1: Create New SonarCloud Project

1. Go to https://sonarcloud.io/
2. Log in with GitHub
3. Click "Analyze new project"
4. Select: `nkllon/beast-observatory` (new repo)
5. Choose: "Other" (for Swift)
6. **Project Key:** `nkllon_beast-observatory` (or preferred name)
7. **Organization:** `nkllon`

### Step 2: Generate New Token

1. SonarCloud → My Account → Security
2. Generate new token: `beast-observatory`
3. Copy token (you won't see it again!)

### Step 3: Add Token to New Repo

1. Go to: `https://github.com/nkllon/beast-observatory/settings/secrets/actions`
2. Add new secret:
   - Name: `SONAR_TOKEN`
   - Value: Token from Step 2
3. Save

### Step 4: Update Configuration

**Update `sonar-project.properties`:**
```properties
sonar.projectKey=nkllon_beast-observatory  # Changed!
sonar.organization=nkllon
# Rest stays the same
```

**Update `.github/workflows/sonarcloud-swift.yml`:**
```yaml
# Paths change if structure changes
# working-directory: .  # If repo root is observatory/swift
# OR
# working-directory: swift  # If structure is different
```

### Step 5: Verify

1. Push to new repo
2. Check GitHub Actions runs
3. Verify SonarCloud shows new project

## Token Management Best Practices

### Option 1: Per-Repo Tokens (Recommended)
- ✅ Each repo has its own token
- ✅ Isolation: if one token compromised, others safe
- ✅ Clear audit trail per project
- ⚠️ More tokens to manage

### Option 2: Shared Org Token
- ✅ One token for all repos in org
- ✅ Easier management
- ❌ Security risk: one breach affects all
- ❌ Harder to audit

**Recommendation:** Use per-repo tokens for better security.

## Configuration After Split

### File Structure (Assumed)
```
beast-observatory/
├── swift/
│   ├── sonar-project.properties  # Project key updated
│   └── Sources/
├── python/
└── .github/
    └── workflows/
        └── sonarcloud-swift.yml    # Paths may need update
```

### Updated `sonar-project.properties`
```properties
sonar.projectKey=nkllon_beast-observatory
sonar.organization=nkllon
sonar.sources=swift/Sources/ObservatoryApp
sonar.tests=swift/Tests
sonar.swift.version=5.9,6.0
sonar.exclusions=**/.build/**,**/Package.swift,**/.swiftpm/**
```

### Updated Workflow Paths
```yaml
- name: Build
  working-directory: swift  # Updated!
  run: swift build

- name: Run Tests
  working-directory: swift  # Updated!
  run: swift test

- name: SonarCloud Scan
  uses: sonarsource/sonarcloud-github-action@master
  with:
    projectBaseDir: swift  # Updated!
```

## Checklist for Migration

- [ ] Create new SonarCloud project: `nkllon_beast-observatory`
- [ ] Generate new `SONAR_TOKEN` in SonarCloud
- [ ] Add `SONAR_TOKEN` to new repo's GitHub Secrets
- [ ] Update `sonar-project.properties` with new project key
- [ ] Update workflow paths if repo structure differs
- [ ] Test first analysis in new repo
- [ ] Verify results appear in SonarCloud
- [ ] Document new project URL for team

## Current Setup (Temporary)

**For now, in `beast-mailbox-core`:**
- Using existing `SONAR_TOKEN` ✅
- Project: `nkllon_beast-observatory-swift` ✅
- No extra setup needed ✅

**When split happens:**
- New repo needs own token ⚠️
- New project in SonarCloud ⚠️
- Follow migration steps above 📋

## Notes

- **Current:** Can piggyback on existing setup
- **Future:** Will need independent setup
- **Documentation:** This file will guide the migration
- **Timing:** Do this when splitting to separate repo

