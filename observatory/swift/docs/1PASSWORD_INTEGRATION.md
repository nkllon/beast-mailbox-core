# 1Password Integration (Optional)

**Goal:** Use 1Password to securely manage Apple Developer credentials  
**When:** When you get a "round-tuit" 😉

---

## Why Use 1Password?

- ✅ **Secure Storage** - Encrypted, synced across devices
- ✅ **Secure Notes** - Store .p8 key files as attachments
- ✅ **Auto-Fill** - Easy to copy credentials when needed
- ✅ **Sharing** - Share with team securely
- ✅ **Audit Trail** - See when credentials were last used/rotated

---

## What to Store in 1Password

### 1. App-Specific Password
**Item Type:** Password  
**Fields:**
- Title: "Apple Developer - App Store Connect API"
- Username: Your Apple ID email
- Password: App-Specific Password (from appleid.apple.com)
- URL: appstoreconnect.apple.com

### 2. Team ID
**Item Type:** Secure Note or Password  
**Fields:**
- Title: "Apple Developer - Team ID"
- Secure Note: Your Team ID
- Tags: `apple-developer`, `app-store-connect`

### 3. API Key (.p8 file)
**Item Type:** Secure Note  
**Fields:**
- Title: "Apple Developer - API Key"
- Secure Note: 
  - Key ID
  - Issuer ID
- Attachments: Upload the .p8 key file
- Tags: `apple-developer`, `api-key`

---

## Optional: 1Password CLI Integration

**If you want to use 1Password CLI for automation:**

```bash
# Install 1Password CLI (if not installed)
# brew install 1password-cli

# Sign in
op signin

# Create .env from 1Password
op read "op://Apple Developer/App Store Connect API/username" > /tmp/apple_id.txt
op read "op://Apple Developer/App Store Connect API/password" > /tmp/app_store_password.txt
op read "op://Apple Developer/Team ID/password" > /tmp/team_id.txt

# Fill in ~/.env
export APPLE_ID="$(cat /tmp/apple_id.txt)"
export APP_STORE_PASSWORD="$(cat /tmp/app_store_password.txt)"
export TEAM_ID="$(cat /tmp/team_id.txt)"

# Clean up
rm /tmp/apple_id.txt /tmp/app_store_password.txt /tmp/team_id.txt
```

**Or create a helper script:**
```bash
#!/bin/bash
# Load credentials from 1Password
source <(op inject -i ~/.env.template)
```

---

## Current Setup (Manual)

**For now, just:**
1. Fill in `~/.env` manually when connecting with Apple
2. Store the same values in 1Password for backup
3. When you get a "round-tuit" → Set up 1Password CLI integration

**That's fine!** ~/.env works great for now. 1Password is for secure backup and future automation.

---

## Quick 1Password Setup (When Ready)

**1. Create Items in 1Password:**
- App Store Connect Password (Password item)
- Team ID (Secure Note)
- API Key (Secure Note with .p8 attachment)

**2. Tag Them:**
- `apple-developer`
- `app-store-connect`
- `beast-observatory`

**3. That's It!**
- Credentials stored securely
- Accessible when needed
- Can set up CLI integration later

---

**Status:** Current setup works fine! 1Password = nice-to-have for later! 😄

