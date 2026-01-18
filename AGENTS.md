# AI-DLC and Spec-Driven Development

Kiro-style Spec Driven Development implementation on AI-DLC (AI Development Life Cycle)

## Project Context

### Paths
- Steering: `.kiro/steering/`
- Specs: `.kiro/specs/`

### Steering vs Specification

**Steering** (`.kiro/steering/`) - Guide AI with project-wide rules and context
**Specs** (`.kiro/specs/`) - Formalize development process for individual features

### Active Specifications
- Check `.kiro/specs/` for active specifications
- Use `/kiro/spec-status [feature-name]` to check progress

## Development Guidelines
- Think in English, generate responses in English

## Tooling Requirements
- `cc-sdd` is installed locally at `/Volumes/lemon/cursor/cc-sdd`; use the packaged CLI (`node /Volumes/lemon/cursor/cc-sdd/tools/cc-sdd/dist/cli.js`) if the workflow needs to be refreshed.
- All specification work **must** flow through the `/kiro:*` commands provided under `.cursor/commands/kiro/`; never hand-edit `.kiro/specs/` outside that pipeline.
- Keep `.kiro/settings/` templates in sync with process updates and run `/kiro/steering` when onboarding new context so every agent shares the same project memory.
- When new repositories consume this core, document the requirement to install the same cc-sdd tooling so cross-repo agents stay aligned.

## Minimal Workflow
- Phase 0 (optional): `/kiro/steering`, `/kiro/steering-custom`
- Phase 1 (Specification):
  - `/kiro/spec-init "description"`
  - `/kiro/spec-requirements {feature}`
  - `/kiro/validate-gap {feature}` (optional: for existing codebase)
  - `/kiro/spec-design {feature} [-y]`
  - `/kiro/validate-design {feature}` (optional: design review)
  - `/kiro/spec-tasks {feature} [-y]`
- Phase 2 (Implementation): `/kiro/spec-impl {feature} [tasks]`
  - `/kiro/validate-impl {feature}` (optional: after implementation)
- Progress check: `/kiro/spec-status {feature}` (use anytime)

## Development Rules
- 3-phase approval workflow: Requirements → Design → Tasks → Implementation
- Human review required each phase; use `-y` only for intentional fast-track
- Keep steering current and verify alignment with `/kiro/spec-status`

## Steering Configuration
- Load entire `.kiro/steering/` as project memory
- Default files: `product.md`, `tech.md`, `structure.md`
- Custom files are supported (managed via `/kiro/steering-custom`)

## Terminology
- Treat the shared observability and infrastructure stack as **Yay Verily RPG2K** to keep naming consistent across agents and tools (including Whisper).
