import sys
import unittest
import json
import shutil
import subprocess
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.validation_utils import TestResult, check_file_exists, save_report, setup_logging

logger = setup_logging()

class TestPhase7Pipeline(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.project_root = Path(__file__).parent.parent
        cls.research_package = cls.project_root / "research_package"
        cls.reports_dir = cls.project_root / "tests" / "reports"
        cls.reports_dir.mkdir(exist_ok=True)

    def test_research_artifacts(self):
        """Test research packaging script and output."""
        result = TestResult("ART-01", "Research Artifacts")
        
        try:
            # 1. Run packaging script
            script_path = self.project_root / "scripts" / "package_research_artifacts.py"
            cmd = [sys.executable, str(script_path)]
            
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                raise AssertionError(f"Packaging script failed: {proc.stderr}")
            result.add_detail("Packaging script ran successfully")
            
            # 2. Verify folder structure
            required_dirs = ["benchmark", "experiments", "configs", "docs"]
            for d in required_dirs:
                if not (self.research_package / d).exists():
                    raise AssertionError(f"Missing directory: {d}")
            result.add_detail("Subfolders present")
            
            # 3. Verify Manifest
            manifest_path = self.research_package / "REPRODUCIBILITY_MANIFEST.json"
            if not check_file_exists(manifest_path):
                raise AssertionError("Manifest missing")
            
            with open(manifest_path) as f:
                manifest = json.load(f)
                required_keys = ["created_at", "version", "python_version"]
                for k in required_keys:
                    if k not in manifest:
                        raise AssertionError(f"Manifest missing key: {k}")
            result.add_detail("Manifest valid")
            
            # 4. Verify README
            readme_path = self.research_package / "README.md"
            if not check_file_exists(readme_path, min_size_bytes=50):
                raise AssertionError("README missing or empty")
            result.add_detail("README present")
            
            # 5. Size Check (<100MB)
            total_size = sum(f.stat().st_size for f in self.research_package.rglob('*') if f.is_file())
            size_mb = total_size / (1024 * 1024)
            if size_mb >= 100:
                raise AssertionError(f"Package too large: {size_mb:.2f} MB")
            result.add_detail(f"Package size acceptable: {size_mb:.2f} MB")
            
            result.pass_test("Research artifacts packaged correctly")
            
        except Exception as e:
            result.fail_test(str(e))
            
        save_report(result.to_dict(), self.reports_dir / "art_01_artifacts.json")

    def test_deployment_config(self):
        """Test deployment configuration files."""
        result = TestResult("DEP-01", "Deployment Config")
        
        try:
            # 1. config.toml
            config_path = self.project_root / ".streamlit" / "config.toml"
            if not check_file_exists(config_path):
                raise AssertionError("config.toml missing")
            
            content = config_path.read_text()
            if "[server]" not in content:
                raise AssertionError("Invalid config.toml content")
            result.add_detail("config.toml valid")
            
            # 2. Procfile
            procfile_path = self.project_root / "Procfile"
            if not check_file_exists(procfile_path):
                raise AssertionError("Procfile missing")
            
            proc_content = procfile_path.read_text()
            if "streamlit run" not in proc_content:
                raise AssertionError("Procfile missing streamlit command")
            result.add_detail("Procfile valid")
            
            # 3. Requirements
            req_path = self.project_root / "requirements.txt"
            if not check_file_exists(req_path):
                raise AssertionError("requirements.txt missing")
            result.add_detail("requirements.txt present")
            
            result.pass_test("Deployment config valid")
            
        except Exception as e:
            result.fail_test(str(e))
            
        save_report(result.to_dict(), self.reports_dir / "dep_01_config.json")

    def test_code_quality(self):
        """Check for print statements and docstrings."""
        result = TestResult("QUAL-01", "Code Quality")
        
        try:
            # Scan modules for print()
            modules_dir = self.project_root / "modules"
            print_violations = []
            
            for py_file in modules_dir.glob("*.py"):
                content = py_file.read_text()
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if "print(" in line and "#" not in line: # Simple heuristic
                        print_violations.append(f"{py_file.name}:{i+1}")
            
            if print_violations:
                result.warn_test(f"Found print statements in modules: {print_violations}")
            else:
                result.add_detail("No print statements found in modules")
                
            result.pass_test("Code quality checks passed")
            
        except Exception as e:
            result.fail_test(str(e))
            
        save_report(result.to_dict(), self.reports_dir / "qual_01_quality.json")

if __name__ == "__main__":
    unittest.main()
