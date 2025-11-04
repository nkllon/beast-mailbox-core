# GitHub Actions Widget in Observatory App

## What It Does

The Observatory app now monitors GitHub Actions workflows directly in the menu bar!

**Features:**
- ✅ Shows latest 2 workflow runs
- ✅ Real-time status (queued, in progress, completed)
- ✅ Status colors (green=success, red=failure, blue=running)
- ✅ Click to open workflow in browser
- ✅ **Trigger workflows** (re-run button right in menu!)
- ✅ Auto-updates every 60 seconds
- ✅ Shows workflow name and status

## Setup

### 1. Get GitHub Token

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name: `Observatory Actions Monitor`
4. Select scope: **`repo`** (or `public_repo` if private repos not needed)
   - ✅ **`repo` scope required for triggering workflows!**
   - ✅ `repo` gives read/write access to repository actions
5. Generate and copy token

### 2. Add Token to ~/.env

```bash
echo "GITHUB_TOKEN=ghp_your_token_here" >> ~/.env
```

### 3. Restart Observatory App

The app will automatically:
- Load token from `~/.env`
- Start monitoring workflows
- Display status in menu bar

## Menu Bar Display

When you click the menu bar icon, you'll see:

```
┌─────────────────────────┐
│ Beast Observatory       │
│ Last Sync: 2m ago       │
├─────────────────────────┤
│ GitHub Actions          │
│ ✅ SonarCloud Analysis 🔄 │
│    Completed            │
│ 🔄 Build Tests          │
│    In Progress          │
├─────────────────────────┤
│ Sync Now                │
│ Open Dashboard          │
│ ...                     │
└─────────────────────────┘
```

## Workflow Status Colors

- 🟢 **Green** = Success
- 🔴 **Red** = Failure
- 🔵 **Blue** = In Progress
- ⚪ **Gray** = Queued/Skipped/Cancelled

## Click to Open

Click any workflow name to open it in your browser.

## Trigger Workflows

Click the 🔄 button next to any workflow to **re-run it**! Perfect for:
- Re-running failed builds
- Triggering tests
- Manually starting workflows

The workflow will be triggered and the menu will auto-refresh to show the new run status.

## Customization

Edit `GitHubActionsMonitor.swift` to:
- Change update interval (default: 60 seconds)
- Monitor specific workflow by name
- Monitor different repository
- Change number of workflows displayed

## Troubleshooting

**Token not found:**
- Check `~/.env` exists and has `GITHUB_TOKEN=...`
- Restart app after adding token

**No workflows shown:**
- Check token has `repo` scope
- Check repository name is correct (default: `nkllon/beast-mailbox-core`)

**API errors:**
- Check token is valid
- Check rate limits (GitHub allows 5000 requests/hour)

## Future Enhancements

- [ ] macOS widget (separate from menu bar)
- [ ] iOS widget support
- [ ] Notifications on workflow failures
- [ ] Workflow filtering
- [ ] Custom refresh interval
