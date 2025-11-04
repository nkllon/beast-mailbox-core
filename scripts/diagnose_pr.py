#!/usr/bin/env python3
"""
Dependabot PR Diagnostic Tool

This script provides comprehensive diagnostic information about a GitHub PR,
including PR details, CI pipeline status, dependency changes, and test failures.

Usage:
    python scripts/diagnose_pr.py <pr_number>
    python scripts/diagnose_pr.py <pr_number> --json  # JSON output
"""

import argparse
import json
import os
import subprocess
import sys
from typing import Dict, List, Optional, Any

try:
    import requests
except ImportError:
    print("ERROR: 'requests' library required. Install with: pip install requests")
    sys.exit(1)


class PRDiagnostic:
    """Diagnostic tool for GitHub PRs"""
    
    def __init__(self, repo: str, pr_number: int, token: Optional[str] = None):
        self.repo = repo
        self.pr_number = pr_number
        self.token = token or os.getenv("GITHUB_TOKEN")
        
        if not self.token:
            print("WARNING: GITHUB_TOKEN not set. Some operations may be limited.")
            print("Set GITHUB_TOKEN environment variable or pass --token")
        
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
        
        self.api_base = f"https://api.github.com/repos/{self.repo}"
    
    def get_pr_info(self) -> Dict[str, Any]:
        """Fetch PR information"""
        url = f"{self.api_base}/pulls/{self.pr_number}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_pr_files(self) -> List[Dict[str, Any]]:
        """Fetch PR file changes"""
        url = f"{self.api_base}/pulls/{self.pr_number}/files"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_workflow_runs(self) -> List[Dict[str, Any]]:
        """Fetch workflow runs for this PR"""
        url = f"{self.api_base}/actions/runs"
        params = {
            "head_sha": self.get_pr_info()["head"]["sha"],
            "per_page": 100
        }
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json().get("workflow_runs", [])
    
    def get_workflow_run_logs(self, run_id: int) -> Optional[str]:
        """Fetch workflow run logs"""
        if not self.token:
            return None
        
        url = f"{self.api_base}/actions/runs/{run_id}/logs"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.text
        return None
    
    def analyze_dependency_changes(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze dependency version changes"""
        dependency_changes = {
            "pyproject_toml": [],
            "workflow_files": [],
            "other": []
        }
        
        for file in files:
            filename = file["filename"]
            patch = file.get("patch", "")
            
            if filename == "pyproject.toml":
                # Extract version changes from patch
                lines = patch.split("\n")
                for line in lines:
                    if line.startswith("+") and "=" in line and ("version" in line.lower() or "==" in line or ">=" in line):
                        dependency_changes["pyproject_toml"].append({
                            "line": line.strip(),
                            "change": "added"
                        })
                    elif line.startswith("-") and "=" in line and ("version" in line.lower() or "==" in line or ">=" in line):
                        dependency_changes["pyproject_toml"].append({
                            "line": line.strip(),
                            "change": "removed"
                        })
            
            elif filename.endswith(".yml") and ".github/workflows/" in filename:
                # Extract GitHub Actions version changes
                lines = patch.split("\n")
                for line in lines:
                    if "uses:" in line or "@" in line:
                        dependency_changes["workflow_files"].append({
                            "file": filename,
                            "line": line.strip(),
                            "change": "added" if line.startswith("+") else "removed" if line.startswith("-") else "modified"
                        })
            
            elif any(ext in filename for ext in [".lock", "requirements", "poetry.lock"]):
                dependency_changes["other"].append({
                    "file": filename,
                    "status": file["status"],
                    "changes": file["additions"] - file["deletions"]
                })
        
        return dependency_changes
    
    def check_sonarcloud_quality_gate(self, pr_info: Dict[str, Any]) -> Dict[str, Any]:
        """Check SonarCloud quality gate status"""
        sonar_token = os.getenv("SONAR_TOKEN")
        if not sonar_token:
            return {"error": "SONAR_TOKEN not set"}
        
        project_key = "nkllon_beast-mailbox-core"
        url = f"https://sonarcloud.io/api/measures/component"
        params = {
            "component": project_key,
            "metricKeys": "alert_status,coverage,bugs,vulnerabilities,code_smells"
        }
        
        try:
            response = requests.get(url, params=params, auth=(sonar_token, ""))
            response.raise_for_status()
            data = response.json()
            
            measures = {m["metric"]: m.get("value", "N/A") for m in data.get("component", {}).get("measures", [])}
            
            return {
                "quality_gate": measures.get("alert_status", "UNKNOWN"),
                "coverage": measures.get("coverage", "N/A"),
                "bugs": measures.get("bugs", "N/A"),
                "vulnerabilities": measures.get("vulnerabilities", "N/A"),
                "code_smells": measures.get("code_smells", "N/A")
            }
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_workflow_failures(self, runs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze workflow run failures"""
        failures = []
        
        for run in runs:
            if run["conclusion"] not in ["success", "skipped"]:
                failure = {
                    "workflow": run["name"],
                    "status": run["conclusion"],
                    "run_id": run["id"],
                    "url": run["html_url"],
                    "created_at": run["created_at"],
                    "updated_at": run["updated_at"]
                }
                
                # Try to get job failures
                if self.token:
                    try:
                        jobs_url = f"{self.api_base}/actions/runs/{run['id']}/jobs"
                        jobs_response = requests.get(jobs_url, headers=self.headers)
                        if jobs_response.status_code == 200:
                            jobs = jobs_response.json().get("jobs", [])
                            failed_jobs = [j for j in jobs if j["conclusion"] == "failure"]
                            if failed_jobs:
                                failure["failed_jobs"] = [
                                    {
                                        "name": j["name"],
                                        "url": j["html_url"],
                                        "steps": [
                                            s["name"] for s in j["steps"] 
                                            if s["conclusion"] == "failure"
                                        ]
                                    }
                                    for j in failed_jobs
                                ]
                    except Exception:
                        pass
                
                failures.append(failure)
        
        return {
            "total_runs": len(runs),
            "failed_runs": len(failures),
            "failures": failures
        }
    
    def diagnose(self) -> Dict[str, Any]:
        """Run full diagnostic"""
        print(f"🔍 Diagnosing PR #{self.pr_number}...", file=sys.stderr)
        
        # Get PR info
        pr_info = self.get_pr_info()
        files = self.get_pr_files()
        runs = self.get_workflow_runs()
        
        # Analyze
        dependency_changes = self.analyze_dependency_changes(files)
        workflow_failures = self.analyze_workflow_failures(runs)
        quality_gate = self.check_sonarcloud_quality_gate(pr_info)
        
        return {
            "pr_info": {
                "number": pr_info["number"],
                "title": pr_info["title"],
                "state": pr_info["state"],
                "author": pr_info["user"]["login"],
                "created_at": pr_info["created_at"],
                "updated_at": pr_info["updated_at"],
                "head_sha": pr_info["head"]["sha"],
                "base_sha": pr_info["base"]["sha"],
                "url": pr_info["html_url"]
            },
            "dependency_changes": dependency_changes,
            "workflow_status": workflow_failures,
            "sonarcloud_quality_gate": quality_gate,
            "files_changed": {
                "total": len(files),
                "files": [
                    {
                        "name": f["filename"],
                        "status": f["status"],
                        "additions": f["additions"],
                        "deletions": f["deletions"]
                    }
                    for f in files[:20]  # Limit to first 20 files
                ]
            }
        }
    
    def print_report(self, report: Dict[str, Any]):
        """Print human-readable report"""
        print("\n" + "="*80)
        print(f"PR #{report['pr_info']['number']}: {report['pr_info']['title']}")
        print("="*80)
        
        print(f"\n📋 PR Information:")
        print(f"  State: {report['pr_info']['state']}")
        print(f"  Author: {report['pr_info']['author']}")
        print(f"  Created: {report['pr_info']['created_at']}")
        print(f"  Updated: {report['pr_info']['updated_at']}")
        print(f"  Head SHA: {report['pr_info']['head_sha'][:7]}")
        print(f"  URL: {report['pr_info']['url']}")
        
        print(f"\n📦 Dependency Changes:")
        if report['dependency_changes']['pyproject_toml']:
            print("  pyproject.toml:")
            for change in report['dependency_changes']['pyproject_toml']:
                print(f"    {change['change'].upper()}: {change['line']}")
        
        if report['dependency_changes']['workflow_files']:
            print("  Workflow Files:")
            for change in report['dependency_changes']['workflow_files']:
                print(f"    {change['file']}: {change['line']}")
        
        if not any(report['dependency_changes'].values()):
            print("  No dependency changes detected")
        
        print(f"\n🔄 Workflow Status:")
        print(f"  Total Runs: {report['workflow_status']['total_runs']}")
        print(f"  Failed Runs: {report['workflow_status']['failed_runs']}")
        
        if report['workflow_status']['failures']:
            print("\n  Failed Workflows:")
            for failure in report['workflow_status']['failures']:
                print(f"    ❌ {failure['workflow']} ({failure['status']})")
                print(f"       URL: {failure['url']}")
                if 'failed_jobs' in failure:
                    for job in failure['failed_jobs']:
                        print(f"       Job: {job['name']}")
                        if job['steps']:
                            print(f"         Failed Steps: {', '.join(job['steps'])}")
        
        print(f"\n🔍 SonarCloud Quality Gate:")
        if 'error' in report['sonarcloud_quality_gate']:
            print(f"  ⚠️  {report['sonarcloud_quality_gate']['error']}")
        else:
            qg = report['sonarcloud_quality_gate']
            status_icon = "✅" if qg.get('quality_gate') == 'OK' else "❌"
            print(f"  {status_icon} Quality Gate: {qg.get('quality_gate', 'UNKNOWN')}")
            print(f"     Coverage: {qg.get('coverage', 'N/A')}%")
            print(f"     Bugs: {qg.get('bugs', 'N/A')}")
            print(f"     Vulnerabilities: {qg.get('vulnerabilities', 'N/A')}")
            print(f"     Code Smells: {qg.get('code_smells', 'N/A')}")
        
        print(f"\n📁 Files Changed: {report['files_changed']['total']}")
        if report['files_changed']['files']:
            print("  Key files:")
            for file in report['files_changed']['files'][:10]:
                print(f"    {file['status']}: {file['name']} (+{file['additions']}, -{file['deletions']})")
        
        print("\n" + "="*80)


def main():
    parser = argparse.ArgumentParser(description="Diagnose GitHub PR failures")
    parser.add_argument("pr_number", type=int, help="PR number to diagnose")
    parser.add_argument("--repo", default="nkllon/beast-mailbox-core", help="Repository (owner/repo)")
    parser.add_argument("--token", help="GitHub token (or set GITHUB_TOKEN env var)")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of human-readable")
    
    args = parser.parse_args()
    
    diagnostic = PRDiagnostic(args.repo, args.pr_number, args.token)
    
    try:
        report = diagnostic.diagnose()
        
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            diagnostic.print_report(report)
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: GitHub API error: {e}", file=sys.stderr)
        if e.response.status_code == 404:
            print(f"PR #{args.pr_number} not found or not accessible", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

