# Get API Issuer ID - Quick Guide

**You have:**
- ✅ API Key ID: `9822DWD339`
- ✅ API Key file: `~/.appleDeveloper/api_key.p8`

**You need:**
- ⚠️ **Issuer ID** (UUID format)

---

## Where to Find Issuer ID

### Step 1: Go to App Store Connect API

**URL:** https://appstoreconnect.apple.com/access/api

### Step 2: Sign In

Sign in with your Apple ID (same one used for Developer account).

### Step 3: Find Issuer ID

**The page shows:**
- **Issuer ID:** `12345678-1234-1234-1234-123456789012` (UUID format)
- Your API keys list

**Look for:**
- It's usually at the top of the page
- It's a UUID (32 hex digits with dashes)
- Format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

### Step 4: Copy It

Copy the entire Issuer ID (including dashes).

---

## Add to ~/.env

**Edit ~/.env:**
```bash
nano ~/.env
# or
code ~/.env
```

**Add (or update) this line:**
```bash
export API_ISSUER_ID="12345678-1234-1234-1234-123456789012"  # Your actual Issuer ID
```

**Or use the script:**
```bash
cd observatory/swift
# Edit the script to add your Issuer ID, then run it
```

---

## Quick Add to ~/.env

**One-liner (replace with your Issuer ID):**
```bash
echo 'export API_ISSUER_ID="your-issuer-id-here"' >> ~/.env
```

**Or edit manually:**
```bash
# Find this section in ~/.env:
# export API_ISSUER_ID="your-issuer-id-here"

# Replace with your actual Issuer ID
export API_ISSUER_ID="12345678-1234-1234-1234-123456789012"
```

---

## Verify Setup

**Test your API Key:**
```bash
source ~/.env

# Verify variables are set
echo "API Key ID: $API_KEY_ID"
echo "Issuer ID: $API_ISSUER_ID"
echo "Key Path: $API_KEY_PATH"

# Test App Store Connect access
xcrun altool --list-providers \
    --apiKey "$API_KEY_ID" \
    --apiIssuer "$API_ISSUER_ID"
```

**If successful:** You'll see your team/provider listed! ✅

---

## Current Status

**You have:**
- ✅ API Key ID: `9822DWD339`
- ✅ API Key file: `~/.appleDeveloper/api_key.p8` (secured with 600 permissions)
- ⚠️ Issuer ID: Need to get from App Store Connect

**Next:**
1. Go to: https://appstoreconnect.apple.com/access/api
2. Copy Issuer ID (UUID)
3. Add to ~/.env: `export API_ISSUER_ID="your-issuer-id"`
4. Done! ✅

---

**Direct Link:** https://appstoreconnect.apple.com/access/api

