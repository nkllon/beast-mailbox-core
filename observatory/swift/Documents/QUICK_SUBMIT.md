# Quick App Store Submission - Beast Mode

**Complete command-line submission in 5 minutes!**

---

## Setup (One Time)

### 1. Get Credentials

**Team ID:**
```bash
# Find at: developer.apple.com/account
# Or check in Xcode: Preferences > Accounts > Select team
```

**App-Specific Password:**
```bash
# Generate at: appleid.apple.com > App-Specific Passwords
```

**Or API Key:**
```bash
# Generate at: appstoreconnect.apple.com/access/api
# Download .p8 key file
# Save Key ID and Issuer ID
```

### 2. Create .env File

```bash
cd observatory/swift
cp .env.example .env
# Edit .env with your credentials
```

**Fill in:**
```bash
export TEAM_ID="YOUR_TEAM_ID"
export APPLE_ID="your-apple-id@example.com"
export APP_STORE_PASSWORD="your-app-specific-password"
```

### 3. Verify Xcode Project Exists

```bash
# Must have ObservatoryApp.xcodeproj
ls ObservatoryApp.xcodeproj/project.pbxproj
```

If missing, create it in Xcode first (see CREATE_XCODE_PROJECT.md).

---

## Submit (Every Time)

### Run Script

```bash
cd observatory/swift
source .env
./submit_to_appstore.sh
```

**That's it!** Script will:
1. ✅ Clean and build
2. ✅ Create archive
3. ✅ Export for App Store
4. ✅ Validate
5. ✅ Upload

---

## After Upload

1. **Go to App Store Connect:**
   - appstoreconnect.apple.com
   - My Apps > ObservatoryApp

2. **Wait for Processing:**
   - Usually 15-30 minutes
   - Status: "Processing" → "Ready to Submit"

3. **Submit for Review:**
   - Version > Build > Select your uploaded build
   - Submit for Review

---

## Troubleshooting

### "Xcode project not found"
**Fix:** Create Xcode project first (see CREATE_XCODE_PROJECT.md)

### "Code signing failed"
**Fix:** Check TEAM_ID in .env matches your Apple Developer account

### "Upload failed"
**Fix:** Verify credentials in .env are correct

---

**Total Time:** ~5 minutes from script run to upload complete! 🚀

