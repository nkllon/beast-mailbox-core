# Setting Up Apple Developer Credentials

**Goal:** Configure ~/.env with Apple Developer credentials for App Store submission

---

## Step 1: Create ~/.env File

```bash
# Copy the example template
cp observatory/swift/.env.example ~/.env

# Or create manually
nano ~/.env
```

The file should be in your home directory: `~/.env`

---

## Step 2: Get Your Team ID

**Option A: From Apple Developer Website**
1. Go to: https://developer.apple.com/account
2. Sign in
3. Click on your team/organization
4. Team ID is shown in the top right or Membership section

**Option B: From Xcode**
1. Open Xcode
2. Xcode > Preferences > Accounts
3. Select your Apple ID
4. Select your team
5. Team ID is shown in the details

**Fill in ~/.env:**
```bash
export TEAM_ID="ABC123DEF4"  # Your actual Team ID
```

---

## Step 3: Get App-Specific Password

**Why App-Specific Password?**
- Apple requires 2FA for App Store Connect
- Can't use your regular Apple ID password
- App-Specific Password is a one-time-use password for API access

**How to Generate:**
1. Go to: https://appleid.apple.com
2. Sign in with your Apple ID
3. Go to: **Sign-In and Security** > **App-Specific Passwords**
4. Click **Generate an app-specific password...**
5. Label it: "App Store Connect API" or "Beast Observatory Submission"
6. Click **Create**
7. **Copy the password immediately** (you won't see it again!)
8. Fill in ~/.env:
   ```bash
   export APP_STORE_PASSWORD="abcd-efgh-ijkl-mnop"  # Your generated password
   ```

**Alternative: Use API Key**
- More secure
- Doesn't require App-Specific Password
- See Step 4 below

---

## Step 4: Get API Key (Optional, Recommended)

**Why API Key?**
- More secure than App-Specific Password
- Can be revoked individually
- Better for automation

**How to Generate:**
1. Go to: https://appstoreconnect.apple.com/access/api
2. Click **Generate API Key** or **+**
3. Fill in:
   - **Name:** "Beast Observatory Submission" (or whatever you want)
   - **Access:** **Admin** (for app submission)
4. Click **Generate**
5. **Download the .p8 key file immediately** (can't download again!)
6. Save it securely: `~/.appstoreconnect/api_key.p8`
7. Copy the **Key ID** and **Issuer ID**
8. Fill in ~/.env:
   ```bash
   export API_KEY_ID="ABC123DEF4"  # Your Key ID
   export API_ISSUER_ID="12345678-1234-1234-1234-123456789012"  # Your Issuer ID
   export API_KEY_PATH="$HOME/.appstoreconnect/api_key.p8"  # Path to .p8 file
   ```

**Store .p8 File Securely:**
```bash
mkdir -p ~/.appstoreconnect
# Move your downloaded .p8 file there
mv ~/Downloads/AuthKey_ABC123DEF4.p8 ~/.appstoreconnect/api_key.p8
chmod 600 ~/.appstoreconnect/api_key.p8  # Secure permissions
```

---

## Step 5: Fill in Apple ID

**In ~/.env:**
```bash
export APPLE_ID="your-apple-id@example.com"
```

This is the email you use to sign in to Apple Developer and App Store Connect.

---

## Step 6: Verify Setup

```bash
# Source the .env file
source ~/.env

# Verify variables are set
echo "Team ID: $TEAM_ID"
echo "Apple ID: $APPLE_ID"
echo "Has Password: $([ -n "$APP_STORE_PASSWORD" ] && echo "Yes" || echo "No")"
echo "Has API Key: $([ -n "$API_KEY_ID" ] && echo "Yes" || echo "No")"
```

**Expected Output:**
```
Team ID: ABC123DEF4
Apple ID: your-email@example.com
Has Password: Yes
Has API Key: No  (or Yes if you set it up)
```

---

## Step 7: Test Credentials

**Test Team ID:**
```bash
# Should show your certificates
security find-identity -v -p codesigning | grep "$TEAM_ID"
```

**Test App Store Connect Access:**
```bash
# List providers (tests authentication)
if [ -n "$API_KEY_ID" ] && [ -n "$API_ISSUER_ID" ]; then
    xcrun altool --list-providers \
        --apiKey "$API_KEY_ID" \
        --apiIssuer "$API_ISSUER_ID"
else
    xcrun altool --list-providers \
        -u "$APPLE_ID" \
        -p "$APP_STORE_PASSWORD"
fi
```

**If successful:** You'll see your team/provider listed.

**If failed:** Check credentials in ~/.env

---

## Complete ~/.env Example

```bash
# Apple Developer Account
export TEAM_ID="ABC123DEF4"
export APPLE_ID="your-apple-id@example.com"

# Option 1: App-Specific Password
export APP_STORE_PASSWORD="abcd-efgh-ijkl-mnop"

# Option 2: API Key (preferred)
# export API_KEY_ID="ABC123DEF4"
# export API_ISSUER_ID="12345678-1234-1234-1234-123456789012"
# export API_KEY_PATH="$HOME/.appstoreconnect/api_key.p8"

# App Configuration
export PROJECT_NAME="ObservatoryApp"
export SCHEME="ObservatoryApp"
export BUNDLE_ID="com.nkllon.ObservatoryApp"
```

---

## Security Notes

1. **Never commit ~/.env to git**
   - It's in your home directory, not the project
   - Already in .gitignore

2. **Protect .p8 key files**
   ```bash
   chmod 600 ~/.appstoreconnect/api_key.p8
   ```

3. **Rotate credentials periodically**
   - App-Specific Passwords: Generate new ones every 6-12 months
   - API Keys: Revoke and regenerate as needed

4. **Backup securely**
   - Keep encrypted backup of credentials
   - Store .p8 files in password manager

---

## Troubleshooting

### "Invalid credentials"
**Fix:** 
- Verify Team ID is correct
- Check App-Specific Password was copied correctly (no spaces)
- Verify API Key ID and Issuer ID if using API Key

### "Team not found"
**Fix:**
- Check Team ID matches your Apple Developer account
- Verify you have Admin access to the team

### "Authentication failed"
**Fix:**
- App-Specific Password might have expired (generate new one)
- API Key might be revoked (check App Store Connect)
- Verify .p8 file path is correct if using API Key

---

## Next Steps

Once ~/.env is configured:

```bash
cd observatory/swift
source ~/.env
./submit_to_appstore.sh
```

**Status:** Ready to fill in credentials together! 🚀

