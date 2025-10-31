# Notes for Future Improvements

**Date:** 2025-10-31  
**Context:** App Store Connect setup feedback

---

## UI/UX Improvements for Future

### App Store Connect Web Interface

**Issue:** Cells on white background are hard to see  
**Location:** App Store Connect API keys page  
**Impact:** Makes it difficult to read Issuer ID and other information

**Suggestion:**
- Use browser extension for better contrast (if available)
- Screenshot and zoom in to read values
- Use browser dev tools to inspect page elements
- Copy values immediately when visible

**For Documentation:**
- Note that white backgrounds can make text hard to read
- Recommend screenshot + zoom for reading values
- Or use browser dev tools to inspect element values

---

## Other Notes

### API Key Storage

**Current Setup:**
- ✅ API Key file: `~/.appleDeveloper/api_key.p8`
- ✅ Secure permissions: `600` (only owner can read/write)
- ✅ Organized in hidden directory

**Future:**
- Consider 1Password integration for key storage
- Or secure backup location
- Document key rotation procedure

---

**Status:** Notes captured for future reference

