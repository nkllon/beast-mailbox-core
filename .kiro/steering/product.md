# Product Overview

Beast Mailbox Core delivers reliable, agent-to-agent messaging primitives for the Beast ecosystem. It currently ships Redis-backed mailboxes and is expanding to pluggable backends (filesystem, Firestore) so deployments can pick the persistence layer that matches their environment.

## Core Capabilities

- Durable direct messaging between Beast agents with async handler support.
- Pluggable mailbox backends selected via Beast Mailbox Core configuration.
- CLI utilities for sending, inspecting, and managing agent inboxes.
- High observability standards (90 % coverage, SonarCloud gating, rich docs).

## Target Use Cases

- Coordinating Beast agents across hosts (Redis, Firestore backends).
- Local development or constrained environments (filesystem mailbox).
- Emerging GCP-native deployments that prefer pay-per-use persistence.

## Value Proposition

- Maintains production-grade quality metrics while remaining agent-friendly (doc-dense, strongly typed interfaces).
- Provides a single abstraction that can be adapted to multiple infrastructures without forcing callers to change.
- Enforces spec-driven delivery so every enhancement carries clear requirements, design, and test expectations.

---
_Focus on patterns and purpose, not exhaustive feature lists_

