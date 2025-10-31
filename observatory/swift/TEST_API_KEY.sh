#!/bin/bash
# Test API Key authentication with App Store Connect
# Usage: ./TEST_API_KEY.sh

set -e

# Load credentials
source ~/.env

echo "🧪 Testing API Key authentication..."
echo ""

# Verify credentials are set
if [ -z "$API_KEY_ID" ]; then
    echo "❌ Error: API_KEY_ID not set in ~/.env"
    exit 1
fi

if [ -z "$API_ISSUER_ID" ]; then
    echo "❌ Error: API_ISSUER_ID not set in ~/.env"
    exit 1
fi

if [ -z "$API_KEY_PATH" ] || [ ! -f "$API_KEY_PATH" ]; then
    echo "❌ Error: API_KEY_PATH not set or file not found"
    exit 1
fi

echo "✅ Credentials loaded:"
echo "   API Key ID: $API_KEY_ID"
echo "   Issuer ID: $API_ISSUER_ID"
echo "   Key Path: $API_KEY_PATH"
echo ""

# Test App Store Connect access
echo "🔍 Testing App Store Connect access..."
xcrun altool --list-providers \
    --apiKey "$API_KEY_ID" \
    --apiIssuer "$API_ISSUER_ID" || {
    echo ""
    echo "❌ Authentication failed"
    echo "   Check:"
    echo "   - API Key ID is correct"
    echo "   - Issuer ID is correct"
    echo "   - .p8 key file is valid"
    exit 1
}

echo ""
echo "✅ Authentication successful!"
echo "   API Key is working - ready to submit to App Store!"
echo ""

