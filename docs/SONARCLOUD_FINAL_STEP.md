# SonarCloud - One Final Manual Step Required

## Current Status

✅ **What's Working:**
- Project created and PUBLIC
- "master" branch is Main branch
- Git's "main" branch analyzes and reports to SonarCloud's "master"
- Analysis runs successfully on every push
- Metrics collected: bugs, code_smells, coverage, ncloc

❌ **What's Missing:**
- Quality Gate not assigned to project
- Badges show "not computed"

## The Issue

The API token doesn't have permissions to assign Quality Gates. This requires **one manual step in the SonarCloud UI**.

## The Fix (30 seconds)

### Step 1: Log into SonarCloud
- Go to: https://sonarcloud.io/project/overview?id=nkllon_beast-mailbox-core
- Click "Log in" (top right)

### Step 2: Assign Quality Gate
1. Once logged in, look for **"Project Settings"** or **"Administration"** tab
2. Navigate to **"Quality Gates"**
3. Select **"Sonar way"** (the default quality gate)
4. Click **"Set as default"** or **"Save"**

### Step 3: Verify
- Go back to project overview
- Quality Gate should now show a status
- Badges will update within 1-2 minutes

## Expected Result

After assigning the quality gate:
- ✅ Quality Gate badge: Shows "Passed" or "Failed" (likely Passed with 2 bugs, 4 code smells)
- ✅ Coverage badge: Shows "0%" (we have no tests yet)

## Current Configuration

**Branch Mapping:**
```
Git Repository    →    SonarCloud
main              →    master (Main branch)
```

**Workflow Configuration:**
```yaml
SONAR_SCANNER_OPTS: -Dsonar.branch.name=master
```

This tells the scanner to report analyses of Git's "main" branch under the name "master" in SonarCloud, which aligns with SonarCloud's default main branch naming.

## Why This Works

- SonarCloud defaults to "master" as the main branch name
- Our Git repo uses "main" (modern standard)
- The workflow maps one to the other
- Once Quality Gate is assigned, badges will work

## Verification

After completing the manual step, these should work:
```
https://sonarcloud.io/api/project_badges/measure?project=nkllon_beast-mailbox-core&metric=alert_status
https://sonarcloud.io/api/project_badges/measure?project=nkllon_beast-mailbox-core&metric=coverage
```

---

**This is the ONLY remaining blocker for SonarCloud badges to be fully operational.**

