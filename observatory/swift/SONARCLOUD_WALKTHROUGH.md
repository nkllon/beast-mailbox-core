# SonarCloud Project Creation - Step-by-Step Walkthrough

## Step-by-Step Guide to Create SonarCloud Project for Swift App

### Step 1: Go to SonarCloud
1. Open your browser
2. Navigate to: **https://sonarcloud.io/**
3. You should see the SonarCloud homepage

### Step 2: Log In
1. Click **"Log in"** button (top right)
2. Choose **"Log in with GitHub"**
3. Authorize SonarCloud to access your GitHub account
4. You'll be redirected back to SonarCloud

### Step 3: Navigate to Projects
1. Once logged in, look at the top navigation bar
2. Click **"Projects"** (or you might see "My Account" or your organization name)
3. You should see a list of your projects (including `nkllon_beast-mailbox-core`)

### Step 4: Create New Project
1. Look for a button that says:
   - **"Analyze new project"** OR
   - **"Add project"** OR
   - **"Create project"** OR
   - A **"+"** icon
2. Click it

### Step 5: Select GitHub Repository
1. You should see a list of your GitHub repositories
2. Look for: **`beast-mailbox-core`** or **`nkllon/beast-mailbox-core`**
3. Click on it to select it
4. Click **"Next"** or **"Set up"** or similar

### Step 6: Configure Project
You'll see configuration options. Fill these in:

**Project Key:**
- **Enter exactly:** `nkllon_beast-observatory-swift`
- ⚠️ This MUST match exactly (case-sensitive)

**Project Name:**
- Can be: `Beast Observatory Swift` or leave default

**Organization:**
- Should default to: `nkllon`
- Verify it's correct

**Language/Type:**
- Look for a dropdown or category selection
- Choose: **"Other"** (for Swift - it's not in the main language list)
- Or if you see **"Swift"** as an option, choose that

### Step 7: Select Analysis Method
You'll see options like:
- **"GitHub Actions"** ← Choose this (we already set up the workflow)
- "Automatic" 
- "Manual"

Click **"GitHub Actions"** if available, or proceed with the default.

### Step 8: Review Configuration
You should see:
- ✅ Project Key: `nkllon_beast-observatory-swift`
- ✅ Organization: `nkllon`
- ✅ Repository: `beast-mailbox-core`
- ✅ Analysis method: GitHub Actions

### Step 9: Finalize Setup
1. Click **"Set up"** or **"Create project"** or **"Finish"**
2. SonarCloud will create the project
3. You might see a message about "Waiting for first analysis"

### Step 10: Verify Project Created
1. You should be redirected to the project page
2. URL should be: `https://sonarcloud.io/project/overview?id=nkllon_beast-observatory-swift`
3. You might see: **"No analysis has been performed yet"** - this is normal!

### Step 11: Verify GitHub Secret (Important!)
1. Go to your GitHub repository: `https://github.com/nkllon/beast-mailbox-core`
2. Click **Settings** (top right)
3. Click **Secrets and variables** → **Actions**
4. Verify you have: **`SONAR_TOKEN`** secret
   - If it exists, you're good!
   - If not, we need to add it (next steps)

### Step 12: Verify Token (Should Already Exist!)
**Since this is in the `beast-mailbox-core` repo, you can use the existing token:**

1. Go to: `https://github.com/nkllon/beast-mailbox-core/settings/secrets/actions`
2. Verify **`SONAR_TOKEN`** exists
   - ✅ If it exists: You're done! No need to create a new one.
   - ❌ If it doesn't exist: Follow steps below

**If token doesn't exist (unlikely):**

1. Go back to SonarCloud
2. Click your profile icon (top right)
3. Click **"My Account"**
4. Go to **"Security"** tab
5. Find **"Generate Token"** section
6. Enter a name: `beast-mailbox-core-swift`
7. Click **"Generate"**
8. **Copy the token** (you won't see it again!)

### Step 13: Add Token to GitHub (Only If Needed)
If token doesn't exist:

1. Go to: `https://github.com/nkllon/beast-mailbox-core/settings/secrets/actions`
2. Click **"New repository secret"**
3. Name: `SONAR_TOKEN`
4. Value: Paste the token you copied
5. Click **"Add secret"**

**Note:** When Observatory splits to its own repo (`beast-observatory`), it will need its own token. See `SONARCLOUD_MIGRATION.md` for details.

### Step 14: Trigger First Analysis
Now we can trigger the first analysis:

1. Make a small change to any Swift file
2. Commit and push:
   ```bash
   cd observatory/swift
   # Make a small comment change
   git add .
   git commit -m "chore: Trigger SonarCloud Swift analysis"
   git push
   ```

OR

1. Go to GitHub Actions
2. Manually trigger the workflow (if enabled)

### Step 15: Monitor Analysis
1. Go to **GitHub Actions** tab in your repository
2. Look for workflow: **"SonarCloud Analysis - Swift"**
3. Click on it to see progress
4. Wait for it to complete

### Step 16: View Results
1. Go back to SonarCloud
2. Navigate to your project: `nkllon_beast-observatory-swift`
3. You should see:
   - Code quality ratings
   - Code smells
   - Bugs
   - Security issues
   - Coverage (if configured)

## What to Look For

### ✅ Success Indicators:
- Project appears in SonarCloud with your project key
- GitHub Actions workflow runs successfully
- Analysis completes without errors
- Results appear in SonarCloud dashboard

### ⚠️ Common Issues:

**"Project not found"**
- Check project key matches exactly: `nkllon_beast-observatory-swift`
- Verify organization name: `nkllon`

**"Analysis failed - no token"**
- Check `SONAR_TOKEN` secret exists in GitHub
- Verify token is valid in SonarCloud

**"No files analyzed"**
- Check `sonar.sources` path in `sonar-project.properties`
- Verify Swift files are in `Sources/ObservatoryApp/`

**"Swift version error"**
- Update `sonar.swift.version` if needed
- Try `6.0` if `5.9,6.0` doesn't work

## Quick Reference

**Project Key:** `nkllon_beast-observatory-swift`  
**Organization:** `nkllon`  
**Repository:** `nkllon/beast-mailbox-core`  
**Configuration File:** `observatory/swift/sonar-project.properties`  
**Workflow File:** `.github/workflows/sonarcloud-swift.yml`  
**SonarCloud URL:** `https://sonarcloud.io/project/overview?id=nkllon_beast-observatory-swift`

## Need Help?

If you get stuck at any step, let me know:
- Which step you're on
- What you see on the screen
- Any error messages

I can guide you through it!

