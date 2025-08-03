#!/usr/bin/env python3
"""
Automated Code Review Script for PlayaTewsIdentityMasker
Integrates all quality tools for comprehensive code review
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime


class CodeReviewer:
    """Automated code reviewer that integrates all quality tools."""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "summary": {
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }
    
    def run_command(self, command, description, capture_output=True):
        """Run a command and capture results."""
        print(f"🔍 Running {description}...")
        try:
            if capture_output:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    check=True, 
                    capture_output=True, 
                    text=True
                )
                print(f"✅ {description} passed")
                return True, result.stdout, result.stderr
            else:
                result = subprocess.run(command, shell=True, check=True)
                print(f"✅ {description} passed")
                return True, "", ""
        except subprocess.CalledProcessError as e:
            print(f"❌ {description} failed")
            return False, e.stdout, e.stderr
    
    def check_code_style(self):
        """Check code style and formatting."""
        print("\n" + "="*60)
        print("🎨 CODE STYLE AND FORMATTING CHECKS")
        print("="*60)
        
        # Black formatting check
        success, stdout, stderr = self.run_command(
            "black --check apps xlib resources",
            "Code formatting (Black)"
        )
        self.results["checks"]["black"] = {
            "passed": success,
            "output": stdout,
            "error": stderr
        }
        
        # isort import check
        success, stdout, stderr = self.run_command(
            "isort --check-only apps xlib resources",
            "Import sorting (isort)"
        )
        self.results["checks"]["isort"] = {
            "passed": success,
            "output": stdout,
            "error": stderr
        }
        
        # Flake8 style check
        success, stdout, stderr = self.run_command(
            "flake8 apps xlib resources",
            "Code style (Flake8)"
        )
        self.results["checks"]["flake8"] = {
            "passed": success,
            "output": stdout,
            "error": stderr
        }
    
    def check_security(self):
        """Check security vulnerabilities."""
        print("\n" + "="*60)
        print("🔒 SECURITY CHECKS")
        print("="*60)
        
        # Bandit security scan
        success, stdout, stderr = self.run_command(
            "bandit -r apps xlib resources -f json -o bandit-report.json",
            "Security scanning (Bandit)"
        )
        self.results["checks"]["bandit"] = {
            "passed": success,
            "output": stdout,
            "error": stderr
        }
        
        # Safety dependency check
        success, stdout, stderr = self.run_command(
            "safety check",
            "Dependency security (Safety)"
        )
        self.results["checks"]["safety"] = {
            "passed": success,
            "output": stdout,
            "error": stderr
        }
        
        # pip-audit check
        success, stdout, stderr = self.run_command(
            "pip-audit",
            "Package audit (pip-audit)"
        )
        self.results["checks"]["pip_audit"] = {
            "passed": success,
            "output": stdout,
            "error": stderr
        }
    
    def check_type_safety(self):
        """Check type safety with MyPy."""
        print("\n" + "="*60)
        print("🔍 TYPE SAFETY CHECKS")
        print("="*60)
        
        # MyPy type checking
        success, stdout, stderr = self.run_command(
            "mypy apps xlib resources",
            "Type checking (MyPy)"
        )
        self.results["checks"]["mypy"] = {
            "passed": success,
            "output": stdout,
            "error": stderr
        }
    
    def check_test_coverage(self):
        """Check test coverage."""
        print("\n" + "="*60)
        print("🧪 TEST COVERAGE CHECKS")
        print("="*60)
        
        # Run tests with coverage
        success, stdout, stderr = self.run_command(
            "pytest --cov=apps --cov=xlib --cov=resources "
            "--cov-report=term-missing --cov-report=html",
            "Test coverage (pytest-cov)"
        )
        self.results["checks"]["test_coverage"] = {
            "passed": success,
            "output": stdout,
            "error": stderr
        }
        
        # Run performance tests
        success, stdout, stderr = self.run_command(
            "pytest tests/performance/ --benchmark-only -v",
            "Performance tests (pytest-benchmark)"
        )
        self.results["checks"]["performance_tests"] = {
            "passed": success,
            "output": stdout,
            "error": stderr
        }
    
    def check_dependencies(self):
        """Check dependency health."""
        print("\n" + "="*60)
        print("📦 DEPENDENCY CHECKS")
        print("="*60)
        
        # Check outdated packages
        success, stdout, stderr = self.run_command(
            "pip list --outdated",
            "Outdated packages check"
        )
        self.results["checks"]["outdated_packages"] = {
            "passed": success,
            "output": stdout,
            "error": stderr
        }
    
    def check_documentation(self):
        """Check documentation."""
        print("\n" + "="*60)
        print("📚 DOCUMENTATION CHECKS")
        print("="*60)
        
        # Check if docs directory exists and can be built
        docs_dir = Path("docs")
        if docs_dir.exists():
            success, stdout, stderr = self.run_command(
                "cd docs && make html",
                "Documentation build (Sphinx)"
            )
            self.results["checks"]["documentation"] = {
                "passed": success,
                "output": stdout,
                "error": stderr
            }
        else:
            print("⚠️  Documentation directory not found")
            self.results["checks"]["documentation"] = {
                "passed": False,
                "output": "",
                "error": "Documentation directory not found"
            }
    
    def generate_report(self):
        """Generate comprehensive review report."""
        print("\n" + "="*60)
        print("📊 GENERATING CODE REVIEW REPORT")
        print("="*60)
        
        # Count results
        for check_name, check_result in self.results["checks"].items():
            if check_result["passed"]:
                self.results["summary"]["passed"] += 1
            else:
                self.results["summary"]["failed"] += 1
        
        # Save detailed report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"code_review_report_{timestamp}.json"
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        # Generate summary
        total_checks = len(self.results["checks"])
        passed = self.results["summary"]["passed"]
        failed = self.results["summary"]["failed"]
        
        print("\n📋 CODE REVIEW SUMMARY")
        print(f"Total Checks: {total_checks}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(passed/total_checks)*100:.1f}%")
        
        # Show failed checks
        if failed > 0:
            print("\n❌ FAILED CHECKS:")
            for check_name, check_result in self.results["checks"].items():
                if not check_result["passed"]:
                    print(f"  - {check_name}: {check_result['error'][:100]}...")
        
        # Show passed checks
        if passed > 0:
            print("\n✅ PASSED CHECKS:")
            for check_name, check_result in self.results["checks"].items():
                if check_result["passed"]:
                    print(f"  - {check_name}")
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return failed == 0
    
    def run_full_review(self):
        """Run complete code review."""
        print("🔍 STARTING COMPREHENSIVE CODE REVIEW")
        print("="*60)
        print(f"Timestamp: {self.results['timestamp']}")
        print("="*60)
        
        # Run all checks
        self.check_code_style()
        self.check_security()
        self.check_type_safety()
        self.check_test_coverage()
        self.check_dependencies()
        self.check_documentation()
        
        # Generate report
        all_passed = self.generate_report()
        
        if all_passed:
            print("\n🎉 ALL CODE REVIEW CHECKS PASSED!")
            print("✅ Code is ready for production")
            return True
        else:
            print("\n⚠️  SOME CODE REVIEW CHECKS FAILED")
            print("🔧 Please address the issues before proceeding")
            return False


def main():
    """Main function to run code review."""
    reviewer = CodeReviewer()
    success = reviewer.run_full_review()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main() 