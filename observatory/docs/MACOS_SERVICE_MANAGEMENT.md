# macOS Native Service Management

**Status:** ✅ Recommended for macOS Client Host  
**Date:** 2025-10-31  
**Target:** Client-side services running on Herbert (macOS development machine)

---

## Why macOS Native?

**For client-side services** (not server/CI):

✅ **Better Integration:**
- Runs as native macOS daemon (launchd)
- Integrates with macOS system lifecycle
- Logs go to standard macOS log locations (`~/Library/Logs`)
- Auto-restarts on crash
- Respects system sleep/wake

✅ **Resource Management:**
- macOS knows about the service
- Better CPU/energy management
- Throttling support built-in

✅ **User Experience:**
- Start/stop via standard macOS tools (`launchctl`)
- Works with system preferences
- No Docker overhead for simple Python scripts

✅ **IDE Integration:**
- Can run alongside Cursor IDE
- Doesn't interfere with Docker (for server services)
- Better for development workflow

---

## Architecture

### Server Services (Docker - Ubuntu)
**Run in:** Docker Compose (Prometheus, Grafana, Pushgateway)  
**Why:** Cross-platform, matches production/CI environment  
**Location:** `observatory/docker/docker-compose.yml`

### Client Services (macOS Native - launchd)
**Run in:** macOS launchd (sync service, local monitoring)  
**Why:** Better macOS integration, no Docker overhead  
**Location:** `~/Library/LaunchAgents/com.nkllon.beast-observatory-sync.plist`

---

## Installation

### 1. Install Sync Service as macOS Daemon

```bash
cd observatory
chmod +x scripts/install_sync_service_macos.sh
./scripts/install_sync_service_macos.sh
```

**What it does:**
- Creates plist in `~/Library/LaunchAgents/`
- Sets up log directory `~/Library/Logs/beast-observatory/`
- Loads and starts the service

### 2. Verify Installation

```bash
# Check service status
launchctl list | grep beast-observatory

# View logs
tail -f ~/Library/Logs/beast-observatory/sync.log

# Check for errors
tail -f ~/Library/Logs/beast-observatory/sync.error.log
```

---

## Service Management

### Start/Stop

```bash
# Start service
launchctl start com.nkllon.beast-observatory-sync

# Stop service
launchctl stop com.nkllon.beast-observatory-sync

# Restart service
launchctl stop com.nkllon.beast-observatory-sync
launchctl start com.nkllon.beast-observatory-sync
```

### Unload/Reload (After Config Changes)

```bash
# Unload service (stops and removes from launchd)
launchctl unload ~/Library/LaunchAgents/com.nkllon.beast-observatory-sync.plist

# Reload service (after updating plist)
launchctl unload ~/Library/LaunchAgents/com.nkllon.beast-observatory-sync.plist
launchctl load ~/Library/LaunchAgents/com.nkllon.beast-observatory-sync.plist
```

### Status

```bash
# List all beast-observatory services
launchctl list | grep beast-observatory

# Detailed status
launchctl list com.nkllon.beast-observatory-sync
```

---

## Configuration

### Environment Variables

Edit `~/Library/LaunchAgents/com.nkllon.beast-observatory-sync.plist`:

```xml
<key>EnvironmentVariables</key>
<dict>
    <key>SONARCLOUD_PROJECT_KEY</key>
    <string>nkllon_beast-mailbox-core</string>
    <key>PROMETHEUS_PUSHGATEWAY_URL</key>
    <string>http://localhost:9091</string>
    <key>SYNC_INTERVAL_HOURS</key>
    <string>1</string>
    <key>SONARCLOUD_TOKEN</key>
    <string>your-token-here</string>
</dict>
```

**After editing:** Reload service (see above)

### Sync Interval

**Current:** Runs every hour (`StartInterval: 3600`)

**To change:**
1. Edit plist: `nano ~/Library/LaunchAgents/com.nkllon.beast-observatory-sync.plist`
2. Change `<integer>3600</integer>` to desired seconds
3. Reload service

---

## Logs

**Location:** `~/Library/Logs/beast-observatory/`

**Files:**
- `sync.log` - Standard output
- `sync.error.log` - Standard error

**View Logs:**
```bash
# Follow logs
tail -f ~/Library/Logs/beast-observatory/sync.log

# Last 50 lines
tail -n 50 ~/Library/Logs/beast-observatory/sync.log

# Search for errors
grep -i error ~/Library/Logs/beast-observatory/sync.error.log
```

**macOS Console App:**
- Open Console.app
- Search for "beast-observatory" or "beast-observatory-sync"

---

## Uninstallation

```bash
# Stop service
launchctl stop com.nkllon.beast-observatory-sync

# Unload service
launchctl unload ~/Library/LaunchAgents/com.nkllon.beast-observatory-sync.plist

# Remove plist
rm ~/Library/LaunchAgents/com.nkllon.beast-observatory-sync.plist

# (Optional) Remove logs
rm -rf ~/Library/Logs/beast-observatory/
```

---

## Comparison: macOS Native vs Docker vs Bash Script

| Feature | macOS launchd | Docker | Bash Script |
|---------|--------------|--------|-------------|
| **OS Integration** | ✅ Native | ⚠️ Container | ❌ None |
| **Auto-restart** | ✅ Yes | ✅ Yes | ❌ Manual |
| **System lifecycle** | ✅ Sleep/wake aware | ❌ No | ❌ No |
| **Log management** | ✅ Native logs | ⚠️ Docker logs | ⚠️ Manual |
| **Resource mgmt** | ✅ macOS manages | ⚠️ Docker manages | ❌ None |
| **Cross-platform** | ❌ macOS only | ✅ Linux/macOS | ✅ All |
| **Overhead** | ✅ Minimal | ⚠️ Docker overhead | ✅ Minimal |
| **Best for** | Client macOS | Server/CI | Quick tests |

**Recommendation:**
- **Client-side services on macOS:** Use launchd ✅
- **Server services:** Use Docker Compose ✅
- **CI/CD:** Use Docker/Ubuntu ✅
- **Quick testing:** Use bash script ✅

---

## Troubleshooting

### Service Won't Start

```bash
# Check for errors
tail -20 ~/Library/Logs/beast-observatory/sync.error.log

# Verify plist syntax
plutil -lint ~/Library/LaunchAgents/com.nkllon.beast-observatory-sync.plist

# Check if executable exists
which beast-observatory-sync
# Or check Python path in plist
```

### Service Crashes

```bash
# Check crash logs
tail -50 ~/Library/Logs/beast-observatory/sync.error.log

# Verify environment variables
launchctl getenv SONARCLOUD_PROJECT_KEY

# Test manually
beast-observatory-sync
```

### Permission Issues

```bash
# Ensure plist is owned by you
chown $(whoami) ~/Library/LaunchAgents/com.nkllon.beast-observatory-sync.plist

# Ensure executable has correct permissions
chmod +x /usr/local/bin/beast-observatory-sync
```

---

## Integration with Development Workflow

### Cursor IDE Integration

The sync service runs as a background daemon, independent of Cursor:
- ✅ Doesn't interfere with Cursor
- ✅ Runs even when Cursor is closed
- ✅ Logs separate from IDE logs

### When to Use macOS Native

✅ **Use launchd for:**
- Long-running sync services
- Services that should survive IDE restarts
- Services that need macOS integration

❌ **Use Docker for:**
- Server services (Prometheus, Grafana)
- Services that need to match production
- Services shared with CI/CD

❌ **Use bash scripts for:**
- One-time scripts
- Testing/debugging
- Quick manual runs

---

**Status:** ✅ macOS native service management ready for client-side services

