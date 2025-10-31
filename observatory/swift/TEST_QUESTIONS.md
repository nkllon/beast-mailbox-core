# Test Questions for Apple Intelligence Chat

**App is running!** Here are some good questions to test the chat:

---

## Code Review Questions

1. **"Review this Swift code for issues:"**
   ```
   func syncMetrics() {
       await fetchFromSonarCloud()
       await pushToPrometheus()
   }
   ```

2. **"What's wrong with this async function?"**
   ```
   async def process_data():
       data = fetch_data()
       return transform(data)
   ```

---

## Error Diagnosis Questions

1. **"Why did this error occur?"**
   ```
   ERROR: Connection refused
   Traceback: File "sync.py", line 150
       await push_to_prometheus()
   ConnectionError: Failed to connect to localhost:9091
   ```

2. **"How do I fix this Swift build error?"**
   ```
   error: 'StatusMonitor' cannot be found in scope
   ```

---

## Architecture Questions

1. **"How should I structure a sync service for reliability?"**

2. **"What's the best way to handle errors in a SwiftUI menu bar app?"**

3. **"Should I use async/await or Combine for this networking code?"**

---

## General Development Questions

1. **"What's the best practice for error handling in Swift?"**

2. **"How do I make a menu bar app in SwiftUI?"**

3. **"What's the difference between @StateObject and @ObservedObject?"**

---

## Observatory-Specific Questions

1. **"How should I structure the Observatory sync service?"**

2. **"What's the best way to display metrics in a SwiftUI dashboard?"**

3. **"How do I integrate Apple Intelligence with a menu bar app?"**

---

## Quick Test Question (Recommended)

**Try this first:**
```
"What's the best way to handle errors in Swift async functions?"
```

**Or:**
```
"Review this code for issues: async func sync() { await fetch(); await push(); }"
```

---

**Open chat:** Click menu bar icon → Press ⌘C or click "Chat with Apple Intelligence"

