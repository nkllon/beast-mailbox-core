#!/bin/bash
# Setup ~/.env file with Apple Developer credential stubs
# Usage: ./setup_env.sh

set -e

ENV_FILE="$HOME/.env"

if [ -f "$ENV_FILE" ]; then
    echo "⚠️  ~/.env already exists"
    echo "   Backing up to ~/.env.backup"
    cp "$ENV_FILE" "$ENV_FILE.backup"
fi

cat > "$ENV_FILE" <<'EOF'
# Apple Developer & App Store Connect Credentials
# Fill these in when connecting with Apple
# This file is in your home directory and should NOT be committed to git

# ============================================
# Apple Developer Account
# ============================================

# Your Apple Developer Team ID
# Find at: developer.apple.com/account
# Or in Xcode: Preferences > Accounts > Select team > Team ID
export TEAM_ID="YOUR_TEAM_ID_HERE"

# Your Apple ID email (used for App Store Connect)
export APPLE_ID="your-apple-id@example.com"

# App-Specific Password (for App Store Connect API)
# Generate at: appleid.apple.com > Sign-In and Security > App-Specific Passwords
# Click "+" to generate a new password for "App Store Connect API"
export APP_STORE_PASSWORD="your-app-specific-password-here"

# ============================================
# API Key (Alternative to App-Specific Password)
# ============================================
# If you prefer using API Key instead of App-Specific Password:
# 1. Go to: appstoreconnect.apple.com/access/api
# 2. Click "Generate API Key"
# 3. Download the .p8 key file
# 4. Fill in the Key ID and Issuer ID below
# 5. Store the .p8 file securely (e.g., ~/.appstoreconnect/api_key.p8)

# API Key ID (found in App Store Connect after generating key)
# export API_KEY_ID="your-api-key-id-here"

# API Issuer ID (found in App Store Connect API Keys page)
# export API_ISSUER_ID="your-issuer-id-here"

# Path to .p8 key file (if using API Key)
# export API_KEY_PATH="$HOME/.appstoreconnect/api_key.p8"

# ============================================
# App-Specific Configuration
# ============================================

# Project name (for ObservatoryApp)
export PROJECT_NAME="ObservatoryApp"

# Scheme name (usually same as project)
export SCHEME="ObservatoryApp"

# Bundle identifier
export BUNDLE_ID="com.nkllon.ObservatoryApp"

# ============================================
# Notes
# ============================================
# 
# To use this file:
#   source ~/.env
#   ./submit_to_appstore.sh
#
# To verify credentials are loaded:
#   echo $TEAM_ID
#   echo $APPLE_ID
#
# Security:
#   - Never commit this file to git
#   - Keep .p8 key files secure
#   - Rotate passwords/keys periodically
#   - Use App-Specific Passwords (not your main Apple ID password)
EOF

chmod 600 "$ENV_FILE"

echo "✅ Created ~/.env with credential stubs"
echo ""
echo "📋 Next steps:"
echo "   1. Edit ~/.env and fill in your Apple Developer credentials"
echo "   2. See SETUP_CREDENTIALS.md for detailed instructions"
echo "   3. When ready: source ~/.env && ./submit_to_appstore.sh"
echo ""
echo "🔒 File permissions set to 600 (read/write for owner only)"

