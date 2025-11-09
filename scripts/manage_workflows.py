#!/usr/bin/env python3
"""
CI Configuration Management Tool

Reads, analyzes, and updates GitHub Actions workflow configurations.

Usage:
    python scripts/manage_workflows.py list
    python scripts/manage_workflows.py analyze <workflow-name>
    python scripts/manage_workflows.py update-action <workflow-name> <action> <version>
    python scripts/manage_workflows.py validate
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
except ImportError:
    print("ERROR: 'pyyaml' library required. Install with: pip install pyyaml")
    sys.exit(1)


class WorkflowManager:
    """Manage GitHub Actions workflows"""

    def __init__(self, workflows_dir: Optional[Path] = None):
        self.workflows_dir = (
            workflows_dir or Path(__file__).parent.parent / ".github" / "workflows"
        )
        if not self.workflows_dir.exists():
            raise FileNotFoundError(
                f"Workflows directory not found: {self.workflows_dir}"
            )

    def list_workflows(self) -> List[Dict[str, str]]:
        """List all workflow files"""
        workflows = []
        for workflow_file in sorted(self.workflows_dir.glob("*.yml")):
            with open(workflow_file, "r") as f:
                try:
                    data = yaml.safe_load(f)
                    workflows.append(
                        {
                            "file": workflow_file.name,
                            "name": data.get("name", "Unknown"),
                            "path": str(workflow_file),
                        }
                    )
                except Exception as e:
                    workflows.append(
                        {
                            "file": workflow_file.name,
                            "name": f"Error: {e}",
                            "path": str(workflow_file),
                        }
                    )
        return workflows

    def read_workflow(self, workflow_name: str) -> Dict:
        """Read and parse a workflow file"""
        workflow_file = self.workflows_dir / f"{workflow_name}.yml"
        if not workflow_file.exists():
            # Try without .yml extension
            workflow_file = self.workflows_dir / workflow_name
            if not workflow_file.exists():
                raise FileNotFoundError(f"Workflow not found: {workflow_name}")

        with open(workflow_file, "r") as f:
            return yaml.safe_load(f)

    def analyze_workflow(self, workflow_name: str) -> Dict:
        """Analyze workflow structure"""
        workflow = self.read_workflow(workflow_name)

        analysis = {
            "name": workflow.get("name", "Unknown"),
            "triggers": {},
            "jobs": {},
            "actions_used": [],
            "permissions": {},
            "external_services": [],
        }

        # Analyze triggers
        on = workflow.get("on", {})
        if isinstance(on, dict):
            for trigger_type, config in on.items():
                if trigger_type == "workflow_run":
                    analysis["triggers"]["workflow_run"] = config
                elif trigger_type == "workflow_dispatch":
                    analysis["triggers"]["workflow_dispatch"] = config
                elif trigger_type in ["push", "pull_request", "release"]:
                    analysis["triggers"][trigger_type] = config
                else:
                    analysis["triggers"][trigger_type] = config

        # Analyze jobs
        jobs = workflow.get("jobs", {})
        for job_name, job_config in jobs.items():
            job_analysis = {
                "runs_on": job_config.get("runs-on", "unknown"),
                "permissions": job_config.get("permissions", {}),
                "steps": len(job_config.get("steps", [])),
                "uses_actions": [],
            }

            # Extract actions used
            for step in job_config.get("steps", []):
                if "uses" in step:
                    action = step["uses"]
                    job_analysis["uses_actions"].append(action)
                    if action not in analysis["actions_used"]:
                        analysis["actions_used"].append(action)

            # Check for external services
            if "services" in job_config:
                for service_name in job_config["services"].keys():
                    if service_name not in analysis["external_services"]:
                        analysis["external_services"].append(service_name)

            analysis["jobs"][job_name] = job_analysis

        # Check for external service references
        workflow_str = yaml.dump(workflow)
        if "sonarcloud" in workflow_str.lower() or "sonar" in workflow_str.lower():
            if "SonarCloud" not in analysis["external_services"]:
                analysis["external_services"].append("SonarCloud")
        if "prometheus" in workflow_str.lower():
            if "Prometheus" not in analysis["external_services"]:
                analysis["external_services"].append("Prometheus")
        if "pypi" in workflow_str.lower():
            if "PyPI" not in analysis["external_services"]:
                analysis["external_services"].append("PyPI")

        return analysis

    def update_action_version(
        self, workflow_name: str, action: str, version: str, dry_run: bool = False
    ) -> Dict:
        """Update action version in workflow"""
        workflow_file = self.workflows_dir / f"{workflow_name}.yml"
        if not workflow_file.exists():
            workflow_file = self.workflows_dir / workflow_name

        with open(workflow_file, "r") as f:
            content = f.read()

        # Find and replace action version
        lines = content.split("\n")
        updated = False
        new_lines = []

        for line in lines:
            if action in line and "uses:" in line:
                # Extract current action
                if action in line:
                    # Replace version
                    if "@" in line:
                        # Extract action name (before @)
                        action_name = line.split("@")[0].strip().split(":")[-1].strip()
                        if action_name == action or action in action_name:
                            if "uses:" in line:
                                new_line = line.split("@")[0] + f"@{version}"
                                new_lines.append(new_line)
                                updated = True
                                continue

            new_lines.append(line)

        if not updated:
            return {"error": f"Action '{action}' not found in workflow"}

        if not dry_run:
            with open(workflow_file, "w") as f:
                f.write("\n".join(new_lines))

        return {
            "updated": updated,
            "dry_run": dry_run,
            "workflow": workflow_name,
            "action": action,
            "version": version,
        }

    def validate_workflows(self) -> Dict:
        """Validate all workflows"""
        results = {"total": 0, "valid": 0, "invalid": 0, "errors": []}

        for workflow_file in self.workflows_dir.glob("*.yml"):
            results["total"] += 1
            try:
                with open(workflow_file, "r") as f:
                    yaml.safe_load(f)
                results["valid"] += 1
            except Exception as e:
                results["invalid"] += 1
                results["errors"].append({"file": workflow_file.name, "error": str(e)})

        return results

    def get_action_versions(self, workflow_name: str) -> List[Dict[str, str]]:
        """Get all action versions used in workflow"""
        workflow = self.read_workflow(workflow_name)
        actions = []

        for job_name, job_config in workflow.get("jobs", {}).items():
            for step in job_config.get("steps", []):
                if "uses" in step:
                    action = step["uses"]
                    if "@" in action:
                        action_name, version = action.split("@", 1)
                        actions.append(
                            {
                                "action": action_name.strip(),
                                "version": version.strip(),
                                "job": job_name,
                                "step": step.get("name", "unnamed"),
                            }
                        )

        return actions


def main():
    parser = argparse.ArgumentParser(description="Manage GitHub Actions workflows")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # List command
    list_parser = subparsers.add_parser("list", help="List all workflows")
    list_parser.add_argument("--json", action="store_true", help="Output JSON")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a workflow")
    analyze_parser.add_argument("workflow", help="Workflow name (without .yml)")
    analyze_parser.add_argument("--json", action="store_true", help="Output JSON")

    # Update action command
    update_parser = subparsers.add_parser("update-action", help="Update action version")
    update_parser.add_argument("workflow", help="Workflow name (without .yml)")
    update_parser.add_argument("action", help="Action name (e.g., actions/checkout)")
    update_parser.add_argument("version", help="New version (e.g., v4)")
    update_parser.add_argument(
        "--dry-run", action="store_true", help="Don't actually update"
    )

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate all workflows")
    validate_parser.add_argument("--json", action="store_true", help="Output JSON")

    # Versions command
    versions_parser = subparsers.add_parser("versions", help="List action versions")
    versions_parser.add_argument("workflow", help="Workflow name (without .yml)")
    versions_parser.add_argument("--json", action="store_true", help="Output JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    manager = WorkflowManager()

    try:
        if args.command == "list":
            workflows = manager.list_workflows()
            if args.json:
                print(json.dumps(workflows, indent=2))
            else:
                print("\nGitHub Actions Workflows:")
                print("=" * 80)
                for wf in workflows:
                    print(f"  {wf['file']:30} {wf['name']}")

        elif args.command == "analyze":
            analysis = manager.analyze_workflow(args.workflow)
            if args.json:
                print(json.dumps(analysis, indent=2))
            else:
                print(f"\nWorkflow Analysis: {analysis['name']}")
                print("=" * 80)
                print("\nTriggers:")
                for trigger, config in analysis["triggers"].items():
                    print(f"  {trigger}: {config}")
                print(f"\nJobs: {len(analysis['jobs'])}")
                for job_name, job_info in analysis["jobs"].items():
                    print(f"  {job_name}:")
                    print(f"    Runs on: {job_info['runs_on']}")
                    print(f"    Steps: {job_info['steps']}")
                print(f"\nActions Used: {len(analysis['actions_used'])}")
                for action in analysis["actions_used"][:10]:
                    print(f"  {action}")
                print(
                    f"\nExternal Services: {', '.join(analysis['external_services']) or 'None'}"
                )

        elif args.command == "update-action":
            result = manager.update_action_version(
                args.workflow, args.action, args.version, dry_run=args.dry_run
            )
            if "error" in result:
                print(f"ERROR: {result['error']}", file=sys.stderr)
                sys.exit(1)
            if args.dry_run:
                print(
                    f"DRY RUN: Would update {result['action']} to {result['version']} in {result['workflow']}"
                )
            else:
                print(
                    f"✅ Updated {result['action']} to {result['version']} in {result['workflow']}"
                )

        elif args.command == "validate":
            results = manager.validate_workflows()
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print("\nWorkflow Validation:")
                print("=" * 80)
                print(f"Total: {results['total']}")
                print(f"Valid: {results['valid']}")
                print(f"Invalid: {results['invalid']}")
                if results["errors"]:
                    print("\nErrors:")
                    for error in results["errors"]:
                        print(f"  {error['file']}: {error['error']}")

        elif args.command == "versions":
            versions = manager.get_action_versions(args.workflow)
            if args.json:
                print(json.dumps(versions, indent=2))
            else:
                print(f"\nAction Versions in {args.workflow}:")
                print("=" * 80)
                for v in versions:
                    print(
                        f"  {v['action']:40} @ {v['version']:15} ({v['job']}/{v['step']})"
                    )

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
