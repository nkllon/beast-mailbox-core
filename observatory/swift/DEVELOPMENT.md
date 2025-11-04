# Developer Setup and DX Rationale

## Overview

This document outlines the rationale behind our developer setup choices and provides guidance on how to set up your environment for the best development experience (DX).

---

## Platform and Language Requirements

- **macOS 15+**: We require macOS 15 or later because:
  - It offers the most up-to-date SDK features and system libraries.
  - Ensures compatibility with the latest Swift 6 toolchain and dependencies.
  - Benefits from improved performance, security, and stability on recent macOS versions.
  
- **Swift 6**: We use Swift 6 to:
  - Leverage the newest language features and performance improvements.
  - Maintain forward compatibility with upcoming Swift ecosystem changes.
  - Align with the latest Apple SDKs and tooling.

---

## Shell-Agnostic Scripts

- Our scripts avoid relying on any shell-specific behavior (e.g., zsh-only features).
- This ensures compatibility regardless of the developer’s shell environment (bash, zsh, fish, etc.).
- We use POSIX-compliant shell scripting to maximize portability and reduce environment-specific bugs.

---

## Homebrew Notes

- We recommend installing packages via Homebrew on macOS for convenience.
- However, Homebrew is **not required**; developers can use alternative package managers or manual installations.
- Our setup scripts and instructions aim to work independently of Homebrew to avoid introducing unnecessary dependencies.

---

## Troubleshooting Common Errors

### 1. Toolchain Mismatch

- **Symptoms**: Compilation errors referencing unsupported Swift versions or unexpected syntax errors.
- **Fix**: Ensure you have the correct Swift 6 toolchain installed and selected.
  - Use `swift --version` to verify your version.
  - If using Xcode, ensure the correct Command Line Tools version is selected in Preferences.
  - Consider using `xcode-select` to point to the correct developer directory.

### 2. SDK Not Found

- **Symptoms**: Errors during build about missing SDKs or unable to find headers.
- **Fix**:
  - Verify that your Xcode installation is complete and updated.
  - Run `xcode-select --install` to install Command Line Tools if missing.
  - Ensure your environment variables (e.g., `SDKROOT`) are set correctly or unset if overridden.
  - Confirm you’re running on macOS 15+ as older versions may lack required SDKs.

---

## Mapping Requirements to Tooling

| Requirement                         | Provided Tooling / Support                        |
|-----------------------------------|-------------------------------------------------|
| Swift 6 Compatibility             | Project uses Swift 6 features; CI runs Swift 6   |
| macOS 15+ Requirement             | CI runners and docs specify macOS 15+            |
| Shell-Agnostic Scripts            | Makefile and shell scripts use POSIX syntax      |
| Code Formatting                   | SwiftFormat integrated; formatting scripts provided |
| Continuous Integration (CI)       | GitHub Actions runs tests and formatting checks  |
| Testing                          | Unit tests included and run by CI                 |
| Package Management                | Homebrew recommended but not required             |

---

## Summary

Our developer experience is designed to be modern, robust, and portable by targeting the latest macOS and Swift versions, supporting multiple shells, and providing clear troubleshooting guidance. The included tools and CI workflows ensure consistency and reliability across all contributors.

For any questions or help, please reach out to the maintainers.
