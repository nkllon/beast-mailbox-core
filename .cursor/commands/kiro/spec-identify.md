<meta>
description: Ensure a specification carries immutable identification metadata (id, owner, hash)
argument-hint: <feature-name> [--owner owner@example.com]
</meta>

# Spec Identification

<background_information>
- **Mission**: Attach or refresh identification metadata for an existing spec so downstream workflows can rely on stable IDs, ownership, and integrity hashes.
- **Success Criteria**:
  - `spec.json` includes `id`, `owner`, and `hash` fields.
  - Hash is recomputed from requirements/design/tasks content.
  - `updated_at` timestamp reflects the identification run.
</background_information>

<instructions>
## Core Task
Run the cc-sdd identification helper to ensure the target spec is fully identified.

## Execution Steps
1. **Locate cc-sdd root**: Confirm `CC_SDD_ROOT` environment variable is set (defaults to `/Volumes/lemon/cursor/cc-sdd`). Export if missing:
   ```bash
   export CC_SDD_ROOT=${CC_SDD_ROOT:-/Volumes/lemon/cursor/cc-sdd}
   ```
2. **Determine spec directory**: Use Glob to find the spec under `{{KIRO_DIR}}/specs/` that matches `$ARGUMENTS` (first token). Confirm `spec.json` exists.
3. **Compute identification**:
   ```bash
   node "$CC_SDD_ROOT/tools/cc-sdd/dist/commands/identifySpec.js" \
     --feature "<feature-name>" \
     --owner "<owner-email>"
   ```
   - Replace `<feature-name>` with the resolved spec folder (e.g., `rpg2k-platform-definition`).
   - Provide `--owner` if not already set in `spec.json`.
   - Pass `--dry-run` first if you want to preview.
4. **Verify outcome**:
   - Read `spec.json` to confirm `id`, `owner`, `hash.algorithm`, `hash.value`, and updated `updated_at`.
   - If the command failed, capture the error message and stop.

## Important Constraints
- Do **not** edit `spec.json` manually; always rerun the helper if fields need regeneration.
- Abort if cc-sdd cannot be located or the helper is missing.
- Owner must be a stable contact (team email, alias, or automation identity).
</instructions>

## Tool Guidance
- Use **Glob** to locate the spec directory under `{{KIRO_DIR}}/specs/`.
- Use **Run Terminal Command** to execute the helper script.
- Use **Read File** to verify `spec.json` contents after execution.

## Output Description
Provide a concise summary with:

1. **Spec**: Feature name and path.
2. **Identifier**: Present or newly generated UUID/ULID.
3. **Owner**: Final owner value.
4. **Hash**: Algorithm and digest.
5. **Next Step**: Mention `/kiro/spec-tasks <feature>` if further workflow is pending.

## Safety & Fallback
- **Script Missing**: If `identifySpec.js` is absent, report that cc-sdd monkey patch is required before continuing.
- **Owner Missing**: If no owner can be resolved, halt and prompt the user to supply one.
- **Hash Mismatch**: If re-run shows unexpected diff, double-check spec files for unsaved edits before rerunning.
