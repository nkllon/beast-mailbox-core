# Cursor Workspace Rules

1. **Specs = deterministic slash commands.** Treat the `/kiro:` commands under `.cursor/commands/kiro/` as the only editor for `.kiro/specs/`. Run them for every phase (steering, requirements, design, tasks, implementation) and never hand-edit the Markdown or `spec.json` outputs.
2. **Maintain shared project memory.** Run `/kiro/steering` (and `/kiro/steering-custom` as needed) whenever context changes so new guidance lands in `.kiro/steering/`.
3. **Keep cc-sdd in sync.** The canonical installer lives at `/Volumes/lemon/cursor/cc-sdd`. Re-run `node /Volumes/lemon/cursor/cc-sdd/tools/cc-sdd/dist/cli.js --cursor --lang en --yes` if commands or templates drift.
4. **Document deviations.** If a workflow step cannot use `/kiro`, record the exception in `AGENTS.md` and propose a template update instead of ad-hoc edits.
5. **Respect phase gates.** Each `/kiro/spec-*` phase requires human approval unless explicitly bypassed with `-y`; mirror that process during maintenance.

