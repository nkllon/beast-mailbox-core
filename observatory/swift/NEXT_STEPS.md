# Next Steps for Observatory App

## Immediate Priorities

### 1. Wire Up Apple Intelligence ⚡ HIGH PRIORITY
**Status**: Currently stubbed with placeholder responses

**Tasks**:
- [ ] Test QueryAppleIntelligenceIntent in isolation
- [ ] Verify AppIntents permissions are correct
- [ ] Implement proper error handling for AppIntents
- [ ] Add fallback handling if Apple Intelligence unavailable
- [ ] Test with real queries (code review, error diagnosis)

**Files to modify**:
- `Sources/ObservatoryApp/Intelligence/AppleIntelligenceAgent.swift`
- `Sources/ObservatoryApp/Chat/ChatView.swift`
- `Sources/ObservatoryApp/Chat/ChatViewModel.swift`

### 2. Improve HTTP Server 🚀 MEDIUM PRIORITY
**Status**: Basic implementation works

**Tasks**:
- [ ] Add proper JSON request parsing
- [ ] Add CORS headers for cross-origin requests
- [ ] Implement request timeout handling
- [ ] Add authentication (API key or basic auth)
- [ ] Better error responses with details

**Files to modify**:
- `Sources/ObservatoryApp/Services/SimpleHTTPServer.swift`

### 3. Add Proper Logging 📝 MEDIUM PRIORITY
**Status**: Using print() statements

**Tasks**:
- [ ] Replace print() with OSLog
- [ ] Add structured logging
- [ ] Add log levels (debug, info, warning, error)
- [ ] Create log file output
- [ ] Add log rotation

**Files to modify**:
- All files using print()
- Create `Sources/ObservatoryApp/Utilities/Logger.swift`

### 4. Window Management Abstraction 🏗️ LOW PRIORITY
**Status**: Working but could be cleaner

**Tasks**:
- [ ] Create WindowManager class
- [ ] Abstract window creation logic
- [ ] Add window state persistence
- [ ] Support multiple instances

**Files to create**:
- `Sources/ObservatoryApp/Utilities/WindowManager.swift`

### 5. Add Unit Tests 🧪 LOW PRIORITY
**Status**: No tests currently

**Tasks**:
- [ ] Set up test target
- [ ] Add tests for ChatViewModel
- [ ] Add tests for AppleIntelligenceProcessor
- [ ] Add tests for HTTP server

## Apple Intelligence Integration Details

### Current Architecture
```
ChatView → ChatViewModel → AppleIntelligenceChat → AppleIntelligenceProcessor
                                                         ↓
                                              QueryAppleIntelligenceIntent
                                                         ↓
                                              Apple Intelligence (stubbed)
```

### What Needs to Happen

1. **QueryAppleIntelligenceIntent** must be properly configured:
   - Verify AppIntents framework is linked
   - Check macOS version requirements (Sequoia 15.0+)
   - Verify permissions in Info.plist

2. **AppleIntelligenceProcessor.process()** needs:
   - Real AppIntents calls
   - Error handling for unavailable AI
   - Fallback to HTTP server if direct AppIntents fail

3. **Testing**:
   - Test on actual macOS 15.0+ device
   - Verify AppIntents permissions
   - Test with actual queries

### macOS Requirements
- **Minimum**: macOS Sequoia 15.0 (for AppIntents with Apple Intelligence)
- **Recommended**: macOS 15.1+ for best compatibility

## Code Quality Improvements

### Swift Best Practices Checklist
- [ ] Add MARK comments for code organization
- [ ] Extract magic numbers to constants
- [ ] Add documentation comments (@param, @returns)
- [ ] Run SwiftLint and fix issues
- [ ] Add @available annotations where needed
- [ ] Ensure all public APIs are documented

## Testing Strategy

### Manual Testing
- [ ] Test chat window opening/closing
- [ ] Test Apple Intelligence query flow
- [ ] Test HTTP server endpoints
- [ ] Test error scenarios
- [ ] Test window state persistence

### Automated Testing
- [ ] Unit tests for business logic
- [ ] Integration tests for HTTP server
- [ ] UI tests for chat flow
- [ ] Performance tests for concurrent queries

## Documentation

### User Documentation
- [ ] Quick start guide
- [ ] Apple Intelligence setup guide
- [ ] Troubleshooting guide
- [ ] FAQ

### Developer Documentation
- [ ] Architecture overview
- [ ] API documentation
- [ ] Contributing guidelines
- [ ] Build instructions
