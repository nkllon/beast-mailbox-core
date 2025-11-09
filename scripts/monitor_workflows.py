#!/usr/bin/env python3
"""
Workflow Monitoring Script

Monitors GitHub Actions workflow status and quality metrics.

Usage:
    python scripts/monitor_workflows.py status
    python scripts/monitor_workflows.py quality
    python scripts/monitor_workflows.py alerts
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    print("ERROR: 'requests' library required. Install with: pip install requests")
    sys.exit(1)


class WorkflowMonitor:
    """Monitor GitHub Actions workflows"""

    def __init__(self, repo: str, token: Optional[str] = None):
        self.repo = repo
        self.token = token or os.getenv("GITHUB_TOKEN")

        if not self.token:
            print(
                "WARNING: GITHUB_TOKEN not set. Some operations may be limited.",
                file=sys.stderr,
            )

        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

        self.api_base = f"https://api.github.com/repos/{self.repo}"

    def get_recent_workflow_runs(self, limit: int = 10) -> List[Dict]:
        """Get recent workflow runs"""
        url = f"{self.api_base}/actions/runs"
        params = {"per_page": limit}

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json().get("workflow_runs", [])

    def get_workflow_status(self, workflow_name: Optional[str] = None) -> Dict:
        """Get workflow status summary"""
        runs = self.get_recent_workflow_runs(limit=50)

        if workflow_name:
            runs = [r for r in runs if r["name"] == workflow_name]

        status_summary = {
            "total": len(runs),
            "success": 0,
            "failure": 0,
            "cancelled": 0,
            "in_progress": 0,
            "recent_failures": [],
        }

        for run in runs:
            conclusion = run.get("conclusion")
            if conclusion == "success":
                status_summary["success"] += 1
            elif conclusion == "failure":
                status_summary["failure"] += 1
                if len(status_summary["recent_failures"]) < 5:
                    status_summary["recent_failures"].append(
                        {
                            "workflow": run["name"],
                            "run_id": run["id"],
                            "url": run["html_url"],
                            "created_at": run["created_at"],
                        }
                    )
            elif conclusion == "cancelled":
                status_summary["cancelled"] += 1
            elif conclusion is None:
                status_summary["in_progress"] += 1

        return status_summary

    def check_quality_metrics(self) -> Dict:
        """Check quality metrics from history.json"""
        metrics_file = Path(__file__).parent.parent / "metrics" / "history.json"

        if not metrics_file.exists():
            return {"error": "metrics/history.json not found"}

        with open(metrics_file, "r") as f:
            data = json.load(f)

        history = data.get("history", [])
        if not history:
            return {"error": "No metrics history"}

        latest = history[-1]
        metrics = latest.get("metrics", {})

        return {
            "timestamp": latest.get("timestamp"),
            "version": latest.get("version"),
            "coverage": metrics.get("coverage"),
            "bugs": metrics.get("bugs"),
            "vulnerabilities": metrics.get("vulnerabilities"),
            "code_smells": metrics.get("code_smells"),
            "quality_gate": metrics.get("quality_gate", "UNKNOWN"),
        }

    def check_sonarcloud_quality_gate(self) -> Dict:
        """Check SonarCloud quality gate status"""
        sonar_token = os.getenv("SONAR_TOKEN")
        if not sonar_token:
            return {"error": "SONAR_TOKEN not set"}

        url = "https://sonarcloud.io/api/measures/component"
        params = {
            "component": "nkllon_beast-mailbox-core",
            "metricKeys": "alert_status,coverage,bugs,vulnerabilities,code_smells",
        }

        try:
            response = requests.get(url, params=params, auth=(sonar_token, ""))
            response.raise_for_status()
            data = response.json()

            measures = {
                m["metric"]: m.get("value", "N/A")
                for m in data.get("component", {}).get("measures", [])
            }

            return {
                "quality_gate": measures.get("alert_status", "UNKNOWN"),
                "coverage": measures.get("coverage", "N/A"),
                "bugs": measures.get("bugs", "N/A"),
                "vulnerabilities": measures.get("vulnerabilities", "N/A"),
                "code_smells": measures.get("code_smells", "N/A"),
            }
        except Exception as e:
            return {"error": str(e)}

    def check_alerts(self) -> Dict:
        """Check for alert conditions"""
        alerts = []

        # Check workflow failures
        status = self.get_workflow_status()
        failure_rate = status["failure"] / status["total"] if status["total"] > 0 else 0
        if failure_rate > 0.1:  # > 10% failure rate
            alerts.append(
                {
                    "type": "workflow_failure_rate",
                    "severity": "warning",
                    "message": f"High workflow failure rate: {failure_rate:.1%}",
                    "details": status,
                }
            )

        # Check quality metrics
        quality = self.check_quality_metrics()
        if "error" not in quality:
            if quality.get("coverage") and float(quality["coverage"]) < 85:
                alerts.append(
                    {
                        "type": "coverage_below_threshold",
                        "severity": "error",
                        "message": f"Coverage below threshold: {quality['coverage']}% (required: 85%)",
                        "details": quality,
                    }
                )

            if quality.get("bugs") and int(quality["bugs"]) > 0:
                alerts.append(
                    {
                        "type": "bugs_detected",
                        "severity": "error",
                        "message": f"Bugs detected: {quality['bugs']}",
                        "details": quality,
                    }
                )

            if quality.get("quality_gate") != "OK":
                alerts.append(
                    {
                        "type": "quality_gate_failed",
                        "severity": "error",
                        "message": f"Quality gate failed: {quality['quality_gate']}",
                        "details": quality,
                    }
                )

        return {"total_alerts": len(alerts), "alerts": alerts}

    def print_status(self, status: Dict):
        """Print workflow status"""
        print("\n" + "=" * 80)
        print("Workflow Status Summary")
        print("=" * 80)

        print(f"\nTotal Runs: {status['total']}")
        print(f"  ✅ Success: {status['success']}")
        print(f"  ❌ Failure: {status['failure']}")
        print(f"  ⏸️  Cancelled: {status['cancelled']}")
        print(f"  🔄 In Progress: {status['in_progress']}")

        if status["recent_failures"]:
            print("\nRecent Failures:")
            for failure in status["recent_failures"]:
                print(f"  ❌ {failure['workflow']} - {failure['url']}")

    def print_quality(self, quality: Dict):
        """Print quality metrics"""
        print("\n" + "=" * 80)
        print("Quality Metrics")
        print("=" * 80)

        if "error" in quality:
            print(f"❌ Error: {quality['error']}")
            return

        status_icon = "✅" if quality.get("quality_gate") == "OK" else "❌"
        print(f"\n{status_icon} Quality Gate: {quality.get('quality_gate', 'UNKNOWN')}")
        print(f"  Coverage: {quality.get('coverage', 'N/A')}%")
        print(f"  Bugs: {quality.get('bugs', 'N/A')}")
        print(f"  Vulnerabilities: {quality.get('vulnerabilities', 'N/A')}")
        print(f"  Code Smells: {quality.get('code_smells', 'N/A')}")
        print(f"  Version: {quality.get('version', 'N/A')}")
        print(f"  Last Updated: {quality.get('timestamp', 'N/A')}")

    def print_alerts(self, alerts: Dict):
        """Print alerts"""
        print("\n" + "=" * 80)
        print(f"Alerts ({alerts['total_alerts']})")
        print("=" * 80)

        if alerts["total_alerts"] == 0:
            print("\n✅ No alerts")
            return

        for alert in alerts["alerts"]:
            severity_icon = "🔴" if alert["severity"] == "error" else "🟡"
            print(f"\n{severity_icon} {alert['type']}: {alert['message']}")


def main():
    parser = argparse.ArgumentParser(description="Monitor GitHub Actions workflows")
    parser.add_argument(
        "command", choices=["status", "quality", "alerts"], help="Command to execute"
    )
    parser.add_argument(
        "--repo", default="nkllon/beast-mailbox-core", help="Repository (owner/repo)"
    )
    parser.add_argument("--workflow", help="Workflow name (for status command)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--token", help="GitHub token (or set GITHUB_TOKEN env var)")

    args = parser.parse_args()

    monitor = WorkflowMonitor(args.repo, args.token)

    try:
        if args.command == "status":
            status = monitor.get_workflow_status(args.workflow)
            if args.json:
                print(json.dumps(status, indent=2))
            else:
                monitor.print_status(status)

        elif args.command == "quality":
            quality = monitor.check_quality_metrics()
            sonar = monitor.check_sonarcloud_quality_gate()

            if args.json:
                print(json.dumps({"metrics": quality, "sonarcloud": sonar}, indent=2))
            else:
                monitor.print_quality(quality)
                if "error" not in sonar:
                    print("\nSonarCloud Status:")
                    print(f"  Quality Gate: {sonar.get('quality_gate', 'N/A')}")
                    print(f"  Coverage: {sonar.get('coverage', 'N/A')}%")

        elif args.command == "alerts":
            alerts = monitor.check_alerts()
            if args.json:
                print(json.dumps(alerts, indent=2))
            else:
                monitor.print_alerts(alerts)
                if alerts["total_alerts"] > 0:
                    sys.exit(1)  # Exit with error code if alerts exist

    except requests.exceptions.HTTPError as e:
        print(f"ERROR: GitHub API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
