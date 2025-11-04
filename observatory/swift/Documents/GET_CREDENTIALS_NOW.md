# Get Apple Developer Credentials - Quick Guide

**Goal:** Get all credentials needed for App Store submission  
**Time:** ~10 minutes  
**All on the web:** ✅ Yes!

---

## What You Need

1. **Apple ID** ✅ (you probably already have this)
2. **Apple Developer Team ID** (from developer.apple.com)
3. **App-Specific Password** (from appleid.apple.com)
4. **OR API Key** (from appstoreconnect.apple.com - optional)

---

## Step 1: Get Your Apple ID

**Do you already have an Apple ID?**
- The email you use for iCloud, App Store, etc.
- If yes: ✅ You're done with Step 1!
- If no: Go to https://appleid.apple.com and create one

**Fill in ~/.env:**
```bash
export APPLE_ID="your-email@example.com"  # Your actual Apple ID email
```

---

## Step 2: Get Apple Developer Team ID

**Do you have an Apple Developer account?**

### Option A: Already Have Developer Account

1. **Go to:** https://developer.apple.com/account
2. **Sign in** with your Apple ID
3. **Click** "Membership" (left sidebar)
4. **Find** "Team ID" — it's a 10-character code like `ABC123DEF4`
5. **Copy it**

**OR**

1. **Open Xcode** (if installed)
2. **Xcode > Preferences > Accounts** (or Settings > Accounts)
3. **Select** your Apple ID
4. **Select** your team
5. **Team ID** is shown in the details

### Option B: Need to Sign Up

1. **Go to:** https://developer.apple.com/programs/
2. **Click** "Enroll"
3. **Sign in** with your Apple ID
4. **Choose** Individual or Organization ($99/year)
5. **Complete** enrollment
6. **Wait** for approval (usually instant, but can take up to 48 hours)
7. **Then** follow Option A above to get Team ID

**Fill in ~/.env:**
```bash
export TEAM_ID="ABC123DEF4"  # Your actual Team ID (10 characters)
```

---

## Step 3: Get App-Specific Password

**Why?** Apple requires 2FA, so you can't use your regular password for API access.

1. **Go to:** https://appleid.apple.com
2. **Sign in** with your Apple ID
3. **Click** "Sign-In and Security" (left sidebar)
4. **Scroll down** to "App-Specific Passwords"
5. **Click** "Generate an app-specific password..."
6. **Label it:** "App Store Connect API" (or "Beast Observatory")
7. **Click** "Create"
8. **Copy the password immediately** — you won't see it again!
   - It looks like: `abcd-efgh-ijkl-mnop` (4 groups of 4 characters)
9. **Click** "Done"

**Fill in ~/.env:**
```bash
export APP_STORE_PASSWORD="abcd-efgh-ijkl-mnop"  # Your generated password
```

**Important:** No spaces! Just the password exactly as shown.

---

## Step 4: Verify App Store Connect Access (Optional Check)

**Make sure you can access App Store Connect:**

1. **Go to:** https://appstoreconnect.apple.com
2. **Sign in** with your Apple ID
3. **Should see:** Your dashboard
4. **If not:** You may need to accept terms or set up your account

**That's it!** If you can sign in, you're good.

---

## Alternative: Use API Key (Optional, More Secure)

**If you prefer API Key over App-Specific Password:**

### Get API Key

1. **Go to:** https://appstoreconnect.apple.com/access/api
2. **Sign in** with your Apple ID
3. **Click** "Generate API Key" or "+"
4. **Fill in:**
   - **Name:** "Beast Observatory" (or whatever you want)
   - **Access:** "Admin" (for app submission)
5. **Click** "Generate"
6. **Download the .p8 key file immediately** — can't download again!
   - Save it: `~/.appstoreconnect/api_key.p8`
7. **Copy the Key ID** (shown on the page)
8. **Copy the Issuer ID** (shown on the page)

**Secure the .p8 file:**
```bash
mkdir -p ~/.appstoreconnect
mv ~/Downloads/AuthKey_ABC123DEF4.p8 ~/.appstoreconnect/api_key.p8
chmod 600 ~/.appstoreconnect/api_key.p8
```

**Fill in ~/.env:**
```bash
# Uncomment these if using API Key instead of App-Specific Password
export API_KEY_ID="ABC123DEF4"  # Your Key ID
export API_ISSUER_ID="12345678-1234-1234-1234-123456789012"  # Your Issuer ID
export API_KEY_PATH="$HOME/.appstoreconnect/api_key.p8"  # Path to .p8 file
```

**Then comment out the App-Specific Password:**
```bash
# export APP_STORE_PASSWORD="..."  # Not needed if using API Key
```

---

## Quick Checklist

- [ ] Apple ID (email you use for Apple services)
- [ ] Apple Developer account enrolled ($99/year if needed)
- [ ] Team ID (from developer.apple.com/account)
- [ ] App-Specific Password (from appleid.apple.com)
- [ ] OR API Key (from appstoreconnect.apple.com - optional)
- [ ] App Store Connect access verified

---

## Fill in ~/.env

**Edit the file:**
```bash
nano ~/.env
# or
code ~/.env
# or
open -e ~/.env
```

**Replace the stubs with your actual values:**
```bash
export TEAM_ID="ABC123DEF4"  # Your actual Team ID
export APPLE_ID="your-actual-email@example.com"  # Your Apple ID
export APP_STORE_PASSWORD="abcd-efgh-ijkl-mnop"  # Your App-Specific Password
```

**Save and exit.**

---

## Test Your Credentials

**Verify everything works:**
```bash
source ~/.env

# Test Team ID
echo "Team ID: $TEAM_ID"
echo "Apple ID: $APPLE_ID"

# Test App Store Connect access
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

**If successful:** You'll see your team/provider listed! ✅

**If failed:** Check credentials in ~/.env match what you copied.

---

## Direct Links

**All on the web:**
- Apple ID: https://appleid.apple.com
- Apple Developer: https://developer.apple.com/account
- App Store Connect: https://appstoreconnect.apple.com
- App Store Connect API: https://appstoreconnect.apple.com/access/api
- App-Specific Passwords: https://appleid.apple.com (Sign-In and Security)

---

## Common Issues

### "Team ID not found"
**Fix:** Make sure you're enrolled in Apple Developer Program ($99/year)

### "App-Specific Password invalid"
**Fix:** 
- Make sure you copied it exactly (no spaces)
- Generate a new one if needed

### "Cannot access App Store Connect"
**Fix:**
- Make sure you've accepted terms in App Store Connect
- Verify your Apple Developer account is active

---

## That's It!

**Once you have:**
- ✅ Apple ID
- ✅ Team ID
- ✅ App-Specific Password (or API Key)

**Fill in ~/.env and you're ready to submit!**

```bash
source ~/.env
cd observatory/swift
./submit_to_appstore.sh
```

---

**Status:** Ready to get credentials! All on the web! 🚀

