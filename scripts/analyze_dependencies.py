#!/usr/bin/env python3
"""
Dependency Conflict Analysis Tool

Analyzes dependency version constraints and identifies potential conflicts.

Usage:
    python scripts/analyze_dependencies.py
    python scripts/analyze_dependencies.py --check-security
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import tomli  # Python 3.11+ or tomli for older versions
except ImportError:
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        print("ERROR: 'tomli' library required. Install with: pip install tomli")
        sys.exit(1)


class DependencyAnalyzer:
    """Analyze dependency constraints and conflicts"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.pyproject_path = self.project_root / "pyproject.toml"
        self.lock_path = self.project_root / "uv.lock"

    def read_pyproject(self) -> Dict:
        """Read and parse pyproject.toml"""
        if not self.pyproject_path.exists():
            raise FileNotFoundError(
                f"pyproject.toml not found at {self.pyproject_path}"
            )

        with open(self.pyproject_path, "rb") as f:
            try:
                return tomli.load(f)
            except NameError:
                # Fallback for tomllib
                import tomllib

                return tomllib.load(f)

    def parse_version_constraint(self, constraint: str) -> Dict[str, str]:
        """Parse version constraint string"""
        # Remove whitespace
        constraint = constraint.strip()

        # Handle different constraint formats
        if constraint.startswith("=="):
            return {"operator": "==", "version": constraint[2:].strip()}
        elif constraint.startswith(">="):
            return {"operator": ">=", "version": constraint[2:].strip()}
        elif constraint.startswith("<="):
            return {"operator": "<=", "version": constraint[2:].strip()}
        elif constraint.startswith(">"):
            return {"operator": ">", "version": constraint[1:].strip()}
        elif constraint.startswith("<"):
            return {"operator": "<", "version": constraint[1:].strip()}
        elif constraint.startswith("~="):
            return {"operator": "~=", "version": constraint[2:].strip()}
        elif constraint.startswith("^"):
            return {"operator": "^", "version": constraint[1:].strip()}
        else:
            # Assume exact version or no constraint
            return {"operator": "==", "version": constraint}

    def get_dependencies(self) -> Dict[str, Dict]:
        """Extract dependencies from pyproject.toml"""
        pyproject = self.read_pyproject()

        dependencies = {}

        # Get project dependencies
        project_deps = pyproject.get("project", {}).get("dependencies", [])
        for dep in project_deps:
            # Parse dependency string: "package>=1.0.0" or "package[extra]>=1.0.0"
            match = re.match(r"^([^\[]+)(?:\[([^\]]+)\])?\s*(.*)$", dep)
            if match:
                name = match.group(1).strip()
                constraint = match.group(3).strip() if match.group(3) else ""
                dependencies[name] = {
                    "constraint": constraint,
                    "parsed": self.parse_version_constraint(constraint),
                    "source": "project.dependencies",
                }

        # Get optional dependencies
        optional_deps = pyproject.get("project", {}).get("optional-dependencies", {})
        for group, deps in optional_deps.items():
            for dep in deps:
                match = re.match(r"^([^\[]+)(?:\[([^\]]+)\])?\s*(.*)$", dep)
                if match:
                    name = match.group(1).strip()
                    constraint = match.group(3).strip() if match.group(3) else ""
                    if name not in dependencies:
                        dependencies[name] = {
                            "constraint": constraint,
                            "parsed": self.parse_version_constraint(constraint),
                            "source": f"optional-dependencies.{group}",
                        }

        return dependencies

    def check_lock_file(self) -> Dict:
        """Check if lock file exists and is up to date"""
        result = {"lock_file_exists": self.lock_path.exists(), "status": "unknown"}

        if not result["lock_file_exists"]:
            result["status"] = "missing"
            return result

        # Try to sync to check if lock file is up to date
        try:
            proc = subprocess.run(
                ["uv", "sync", "--dry-run"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if proc.returncode == 0:
                result["status"] = "up_to_date"
            else:
                result["status"] = "out_of_date"
                result["error"] = proc.stderr
        except FileNotFoundError:
            result["status"] = "uv_not_available"
        except subprocess.TimeoutExpired:
            result["status"] = "timeout"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def analyze_constraints(self) -> Dict:
        """Analyze dependency constraints"""
        dependencies = self.get_dependencies()

        analysis = {
            "total_dependencies": len(dependencies),
            "pinned_versions": [],
            "range_constraints": [],
            "no_constraints": [],
            "dependencies": dependencies,
        }

        for name, info in dependencies.items():
            constraint = info["constraint"]
            parsed = info["parsed"]

            if not constraint:
                analysis["no_constraints"].append(name)
            elif parsed["operator"] == "==":
                analysis["pinned_versions"].append(
                    {"package": name, "version": parsed["version"]}
                )
            else:
                analysis["range_constraints"].append(
                    {
                        "package": name,
                        "constraint": constraint,
                        "operator": parsed["operator"],
                    }
                )

        return analysis

    def check_security_vulnerabilities(self) -> Dict:
        """Check for known security vulnerabilities"""
        # This would integrate with safety, pip-audit, or similar tools
        result = {"tool": "none", "vulnerabilities": [], "status": "not_checked"}

        # Try pip-audit if available
        try:
            proc = subprocess.run(
                ["pip-audit", "--format", "json"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if proc.returncode == 0:
                data = json.loads(proc.stdout)
                result["tool"] = "pip-audit"
                result["status"] = "success"
                result["vulnerabilities"] = data.get("vulnerabilities", [])
            else:
                result["status"] = "error"
                result["error"] = proc.stderr
        except FileNotFoundError:
            result["status"] = "tool_not_available"
            result["message"] = (
                "pip-audit not installed. Install with: pip install pip-audit"
            )

        return result

    def generate_report(self, check_security: bool = False) -> Dict:
        """Generate full analysis report"""
        print("🔍 Analyzing dependencies...", file=sys.stderr)

        constraints = self.analyze_constraints()
        lock_status = self.check_lock_file()

        report = {"constraints": constraints, "lock_file": lock_status}

        if check_security:
            print("🔒 Checking security vulnerabilities...", file=sys.stderr)
            report["security"] = self.check_security_vulnerabilities()

        return report

    def print_report(self, report: Dict):
        """Print human-readable report"""
        print("\n" + "=" * 80)
        print("Dependency Analysis Report")
        print("=" * 80)

        constraints = report["constraints"]
        print(f"\n📦 Dependencies:")
        print(f"  Total: {constraints['total_dependencies']}")
        print(f"  Pinned versions: {len(constraints['pinned_versions'])}")
        print(f"  Range constraints: {len(constraints['range_constraints'])}")
        print(f"  No constraints: {len(constraints['no_constraints'])}")

        if constraints["pinned_versions"]:
            print("\n  Pinned Versions:")
            for pkg in constraints["pinned_versions"][:10]:
                print(f"    {pkg['package']} == {pkg['version']}")

        if constraints["range_constraints"]:
            print("\n  Range Constraints:")
            for pkg in constraints["range_constraints"][:10]:
                print(f"    {pkg['package']} {pkg['constraint']}")

        lock_status = report["lock_file"]
        print(f"\n🔒 Lock File Status:")
        print(f"  Exists: {lock_status['lock_file_exists']}")
        print(f"  Status: {lock_status['status']}")
        if "error" in lock_status:
            print(f"  Error: {lock_status['error']}")

        if "security" in report:
            security = report["security"]
            print(f"\n🛡️  Security Status:")
            print(f"  Tool: {security['tool']}")
            print(f"  Status: {security['status']}")
            if security["vulnerabilities"]:
                print(f"  Vulnerabilities Found: {len(security['vulnerabilities'])}")
                for vuln in security["vulnerabilities"][:5]:
                    print(
                        f"    - {vuln.get('name', 'unknown')}: {vuln.get('id', 'unknown')}"
                    )
            elif security["status"] == "success":
                print("  ✅ No known vulnerabilities")
            if "message" in security:
                print(f"  Note: {security['message']}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze dependency constraints and conflicts"
    )
    parser.add_argument(
        "--check-security",
        action="store_true",
        help="Check for security vulnerabilities",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output JSON instead of human-readable"
    )
    parser.add_argument("--project-root", type=Path, help="Project root directory")

    args = parser.parse_args()

    analyzer = DependencyAnalyzer(args.project_root)

    try:
        report = analyzer.generate_report(check_security=args.check_security)

        if args.json:
            print(json.dumps(report, indent=2))
        else:
            analyzer.print_report(report)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
