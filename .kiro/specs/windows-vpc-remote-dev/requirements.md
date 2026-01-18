# Requirements Document

## Introduction
Beast Snow maintainers need a preconfigured Windows-based VPC workstation that runs Cursor or vanilla VS Code with the Beast toolchain and Kiro workflows, enabling remote contributors to develop against the shared Beast cluster without manual environment setup.

## Requirements

### Requirement 1: Windows Beast Toolchain Provisioning
**Objective:** As a Beast platform engineer, I want the Windows VPC image to ship with the Beast development toolchain, so that remote developers can begin coding immediately.

#### Acceptance Criteria
1. WHEN the golden Windows image is built THEN the Beast Windows Provisioner SHALL install Python 3.11.x and run `pip install -e ".[dev]"` inside the repository workspace.
2. WHEN the golden Windows image is built THEN the Beast Windows Provisioner SHALL install Node.js 20.x and configure the `cc-sdd` CLI with `/kiro` commands accessible from PowerShell.
3. IF the Windows host supports WSL2 THEN the Beast Windows Provisioner SHALL enable WSL and install Ubuntu with mirrored Beast dependencies for developers who prefer Linux shells.
4. WHERE the Beast workspace resides THE Beast Windows Provisioner SHALL clone `beast-mailbox-core` to `C:\Workspaces\beast-mailbox-core` with write permissions for the developer account.

### Requirement 2: Cursor and VS Code Runtime Experience
**Objective:** As a Beast Snow developer, I want Cursor and VS Code preinstalled and configured, so that I can choose my editor without extra setup.

#### Acceptance Criteria
1. WHEN the developer signs in to the Windows VPC THEN the Editor Experience Manager SHALL launch Cursor with the workspace `C:\Workspaces\beast-mailbox-core`.
2. IF Cursor authentication fails THEN the Editor Experience Manager SHALL present documentation for generating a Cursor token and store credentials securely in Windows Credential Manager.
3. WHEN the developer prefers VS Code THEN the Editor Experience Manager SHALL provide a desktop shortcut that opens VS Code against the same workspace with synced settings and extensions.
4. WHERE editor extensions are required THE Editor Experience Manager SHALL preinstall Python, Git, and Kiro helper extensions across both editors.

### Requirement 3: Cluster Connectivity & Security
**Objective:** As a Beast SRE, I want the Windows VPC to connect securely to the Beast cluster, so that development traffic stays private.

#### Acceptance Criteria
1. WHEN the workstation boots THEN the Secure Network Layer SHALL establish a WireGuard or IPSec tunnel to the home-cluster gateway with only Beast service subnets routed.
2. IF the secure tunnel drops THEN the Secure Network Layer SHALL block outbound Beast ports and notify the developer via Windows notifications.
3. WHEN the secure tunnel is active THEN the Secure Network Layer SHALL expose DNS entries for Beast cluster services via the private resolver.
4. WHERE firewall policies are applied THE Secure Network Layer SHALL restrict inbound traffic to RDP/management addresses and enforce Windows Defender.

### Requirement 4: Operational Safeguards and Support
**Objective:** As a Beast operations engineer, I want the Windows VPC to stay maintainable, so that we can keep the environment aligned with the devcontainer and cluster.

#### Acceptance Criteria
1. WHEN the system logs in a developer account THEN the Support Automations SHALL run `/kiro/steering` and refresh `/kiro` commands nightly.
2. WHEN Windows Update requires reboots THEN the Support Automations SHALL schedule maintenance windows and warn the developer 24 hours in advance.
3. WHILE the workstation is active THE Support Automations SHALL stream logs of Cursor, VS Code, and tunnel health to the shared monitoring endpoint.
4. IF the local Beast workspace diverges from the main branch THEN the Support Automations SHALL offer a guided sync workflow before the next coding session.


