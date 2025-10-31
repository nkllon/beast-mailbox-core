#!/bin/bash
# Update ~/.env with API Key credentials
# Usage: ./UPDATE_ENV_API_KEY.sh

set -e

ENV_FILE="$HOME/.env"
API_KEY_ID="9822DWD339"
API_KEY_PATH="$HOME/.appleDeveloper/api_key.p8"

# Check if .p8 file exists
if [ ! -f "$API_KEY_PATH" ]; then
    echo "⚠️  Warning: $API_KEY_PATH not found"
    echo "   Make sure you moved AuthKey_9822DWD339.p8 to ~/.appleDeveloper/api_key.p8"
    exit 1
fi

# Read existing .env or create template
if [ ! -f "$ENV_FILE" ]; then
    echo "⚠️  ~/.env not found, creating from template..."
    cd observatory/swift 2>/dev/null || cd "$(dirname "$0")"
    ./setup_env.sh
fi

# Backup existing .env
cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"

# Update API Key settings
echo "🔧 Updating ~/.env with API Key credentials..."

# Comment out App-Specific Password if present
sed -i.bak 's/^export APP_STORE_PASSWORD=/# export APP_STORE_PASSWORD=/' "$ENV_FILE" 2>/dev/null || \
sed -i '' 's/^export APP_STORE_PASSWORD=/# export APP_STORE_PASSWORD=/' "$ENV_FILE" 2>/dev/null || true

# Add/update API Key settings
if grep -q "^export API_KEY_ID=" "$ENV_FILE"; then
    # Update existing
    sed -i.bak "s|^export API_KEY_ID=.*|export API_KEY_ID=\"$API_KEY_ID\"|" "$ENV_FILE" 2>/dev/null || \
    sed -i '' "s|^export API_KEY_ID=.*|export API_KEY_ID=\"$API_KEY_ID\"|" "$ENV_FILE" 2>/dev/null || true
else
    # Add new (find where to insert - after API Key section comments)
    if grep -q "# API Key ID" "$ENV_FILE"; then
        # Insert after comment
        sed -i.bak "/# API Key ID/a\\
export API_KEY_ID=\"$API_KEY_ID\"
" "$ENV_FILE" 2>/dev/null || \
        sed -i '' "/# API Key ID/a\\
export API_KEY_ID=\"$API_KEY_ID\"
" "$ENV_FILE" 2>/dev/null || true
    else
        # Append to end
        echo "" >> "$ENV_FILE"
        echo "# API Key (Active)" >> "$ENV_FILE"
        echo "export API_KEY_ID=\"$API_KEY_ID\"" >> "$ENV_FILE"
    fi
fi

# Update API_KEY_PATH
if grep -q "^export API_KEY_PATH=" "$ENV_FILE"; then
    sed -i.bak "s|^export API_KEY_PATH=.*|export API_KEY_PATH=\"$API_KEY_PATH\"|" "$ENV_FILE" 2>/dev/null || \
    sed -i '' "s|^export API_KEY_PATH=.*|export API_KEY_PATH=\"$API_KEY_PATH\"|" "$ENV_FILE" 2>/dev/null || true
else
    if grep -q "export API_KEY_ID=" "$ENV_FILE"; then
        # Insert after API_KEY_ID
        sed -i.bak "/export API_KEY_ID=/a\\
export API_KEY_PATH=\"$API_KEY_PATH\"
" "$ENV_FILE" 2>/dev/null || \
        sed -i '' "/export API_KEY_ID=/a\\
export API_KEY_PATH=\"$API_KEY_PATH\"
" "$ENV_FILE" 2>/dev/null || true
    else
        echo "export API_KEY_PATH=\"$API_KEY_PATH\"" >> "$ENV_FILE"
    fi
fi

# Clean up backup files
rm -f "$ENV_FILE.bak" "$ENV_FILE".bak.* 2>/dev/null || true

echo "✅ Updated ~/.env with API Key:"
echo "   API_KEY_ID: $API_KEY_ID"
echo "   API_KEY_PATH: $API_KEY_PATH"
echo ""
echo "📋 Next step: Get Issuer ID from App Store Connect"
echo "   1. Go to: appstoreconnect.apple.com/access/api"
echo "   2. Find 'Issuer ID' (UUID format)"
echo "   3. Add to ~/.env: export API_ISSUER_ID=\"your-issuer-id\""
echo ""
echo "Or edit ~/.env manually:"
echo "   export API_ISSUER_ID=\"your-issuer-id-here\""

