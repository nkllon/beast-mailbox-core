# Implementation Plan

- [ ] 1. Harden Windows golden image with Beast toolchain
- [ ] 1.1 Install core Beast dependencies on base image
  - Execute Python 3.11 installer silently and confirm `python --version` returns expected build.
  - Install Node.js 20 LTS, ensure npm on PATH, and run `npm install -g cc-sdd`.
  - Clone `beast-mailbox-core` into `C:\Workspaces\beast-mailbox-core` and run `pip install -e ".[dev]"` using an elevated PowerShell session.
  - _Requirements: 1.1, 1.2, 1.4_
- [ ] 1.2 Enable optional WSL2 companion environment
  - Turn on required Windows features (`VirtualMachinePlatform`, `Microsoft-Windows-Subsystem-Linux`) and reboot the image builder if necessary.
  - Deploy Ubuntu distribution, mirror Python/Node/cc-sdd installation, and validate `/kiro` commands operate from WSL shell.
  - Document environment toggle script so provisioning pipeline can skip WSL on hosts without virtualization.
  - _Requirements: 1.3_
- [ ] 1.3 Bake editor runtimes into the image
  - Install Cursor and pin default workspace to `C:\Workspaces\beast-mailbox-core`.
  - Install VS Code with required extensions (Python, Git, Kiro helpers) and export synced settings into the workspace.
  - Seed Windows Credential Manager helper scripts for storing Cursor token securely at first run.
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 2. Configure secure cluster connectivity
- [ ] 2.1 Install and configure WireGuard tunnel
  - Install WireGuard for Windows silently and import `beast.conf` peer configuration.
  - Script health check that validates handshake and routes only Beast subnets through the tunnel.
  - Set up Windows toast notification for tunnel failure with remediation guidance.
  - _Requirements: 3.1, 3.2_
- [ ] 2.2 Harden Windows firewall and DNS routing
  - Author firewall baseline that allows inbound RDP from trusted CIDRs and blocks Beast ports when tunnel is down.
  - Configure DNS override scripts to use cluster resolver while tunnel is active and revert cleanly when inactive.
  - Validate antivirus/Defender policies remain enabled post-configuration.
  - _Requirements: 3.3, 3.4_

- [ ] 3. Implement runtime experience orchestration
- [ ] 3.1 Build login automation for editors and `/kiro` tooling
  - Create Task Scheduler or Run registry scripts to launch Cursor at login, fallback to VS Code if Cursor not authenticated.
  - Verify `/kiro` commands are on PATH for PowerShell and optional WSL sessions; trigger `/kiro/steering` on first login.
  - Provide quick actions for switching editors while preserving shared workspace settings.
  - _Requirements: 2.1, 2.3, 3.1, 4.1_
- [ ] 3.2 Implement repo divergence assistant
  - Develop script that detects local branch divergence from origin/main and prompts guided sync steps.
  - Integrate with login automation to surface warnings before coding sessions.
  - Ensure sync workflow logs outcomes for Support Automations telemetry.
  - _Requirements: 4.4_

- [ ] 4. Build support and monitoring automations
- [ ] 4.1 Nightly maintenance scheduler
  - Define scheduled task that runs maintenance script (cc-sdd refresh, `/kiro/steering`, log collection) at 02:00.
  - Handle Windows Update coordination with postponement prompts and advance notifications.
  - Ensure script fails fast with actionable logging and does not interrupt active sessions.
  - _Requirements: 4.1, 4.2_
- [ ] 4.2 Log forwarding and health reporting
  - Collect Cursor, VS Code, WireGuard, and system health logs; forward to Beast monitoring endpoint securely.
  - Emit Prometheus-style metrics or REST payload with tunnel state, steering freshness, and update status.
  - Create alert hooks for repeated tunnel failures or maintenance script errors.
  - _Requirements: 3.2, 4.3_

- [ ] 5. Testing and validation
- [ ] 5.1 Provisioning validation suite
  - Author Pester tests to confirm Python/Node installation, repo setup, and `/kiro` command availability.
  - Script automated sanity check ensuring Cursor/VS Code launch successfully post-image capture.
  - Validate WireGuard tunnel connectivity against staging Beast cluster endpoints in CI pipeline.
  - _Requirements: 1.1, 1.2, 1.3, 3.1_
- [ ] 5.2 End-to-end experience walkthrough
  - Execute first-login scenario with seeded account, verifying MFA, tunnel, Cursor launch, and repo sync prompts.
  - Simulate tunnel outage to confirm fail-closed behavior and notification handling.
  - Run nightly maintenance job in staging to ensure logs and updates flow correctly.
  - _Requirements: 2.1, 3.2, 4.1, 4.3_

