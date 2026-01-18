# Requirements Document

## Introduction
Beast Snow contributors need a reproducible remote development environment that packages the Beast Mailbox Core toolchain inside a dev container while exposing the workspace exclusively through VS Code Tunnel so collaborators without Cursor can execute the spec-driven workflow safely.

## Requirements

### Requirement 1: Containerized Beast Toolchain
**Objective:** As a Beast platform engineer, I want the dev container to package the standard Beast toolchain, so that remote contributors get a consistent environment.

#### Acceptance Criteria
1. WHEN the dev container image build runs THEN the Beast Dev Container SHALL install Python 3.11.x and execute `pip install -e ".[dev]"` to provision Beast Mailbox dependencies.
2. WHEN the dev container image build runs THEN the Beast Dev Container SHALL install Node.js 20.x and globally install the `cc-sdd` CLI required for `/kiro` commands.
3. IF the container host exposes NVIDIA GPUs THEN the Beast Dev Container SHALL install the CUDA runtime and drivers compatible with the host toolkit version.
4. WHERE the workspace is mounted THE Beast Dev Container SHALL place `beast-mailbox-core` at `/workspace/beast-mailbox-core` with writable permissions for the VS Code Tunnel user.

### Requirement 2: VS Code Tunnel Exposure
**Objective:** As a remote Beast Snow developer, I want to connect through VS Code Tunnel, so that I can edit and run commands without relying on Cursor.

#### Acceptance Criteria
1. WHEN the container entrypoint completes environment bootstrap THEN the VS Code Tunnel Agent SHALL start `code tunnel` with the workspace name `beast-mailbox-remote`.
2. IF GitHub authentication for the VS Code Tunnel Agent fails THEN the agent SHALL exit with a non-zero status and log remediation steps for obtaining valid credentials.
3. WHEN the VS Code Tunnel Agent reports a ready state THEN it SHALL print the connect URL and listening ports to the container logs.
4. WHERE the VS Code Tunnel Agent accepts inbound sessions THE container firewall SHALL permit traffic only through the tunnel’s reverse proxy endpoints.

### Requirement 3: Spec-Driven Workflow Enablement
**Objective:** As a Beast maintainer, I want the remote container to automate spec tooling, so that contributors can follow the Kiro process without manual setup.

#### Acceptance Criteria
1. WHEN the container initializes a shell session THEN the Dev Workflow Toolkit SHALL source the project virtualenv and append `/kiro` commands to `PATH`.
2. WHEN the container startup hooks run THEN the Dev Workflow Toolkit SHALL execute `/kiro/steering` to sync steering memory into the active session.
3. WHEN a developer runs `npm run kiro:status <feature>` THEN the Dev Workflow Toolkit SHALL invoke `/kiro/spec-status <feature>` and stream the output in the terminal.
4. IF a developer launches the provided VS Code task `Run Tests` THEN the Dev Workflow Toolkit SHALL execute `pytest tests/ --cov` inside the container.

### Requirement 4: Security and Observability Guardrails
**Objective:** As a Beast SRE, I want remote access to stay secure and auditable, so that the tunnel deployment satisfies operational policies.

#### Acceptance Criteria
1. WHEN the container boots THEN the Security Guard SHALL disable SSH password authentication and leave the VS Code Tunnel as the sole remote entry point.
2. IF secrets are provided via environment variables THEN the Security Guard SHALL inject them using `remoteEnv` without writing plaintext to the filesystem.
3. WHILE the VS Code Tunnel Agent is running THE Observability Monitor SHALL emit heartbeat logs at 60-second intervals indicating tunnel health.
4. WHERE runtime logs are generated THE Security Guard SHALL forward them to the configured RunPod persistent log target or external aggregator.


