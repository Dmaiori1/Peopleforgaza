"""Exercise the real verification command against disposable project fixtures."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

VERIFY = Path(__file__).resolve().parents[1] / "scripts" / "verify.py"

class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "scripts").mkdir()
        (self.root / "tests").mkdir()
        shutil.copyfile(VERIFY, self.root / "scripts" / "verify.py")
        (self.root / "scripts" / "check_site.py").write_text(
            'print("STATIC_FIXTURE_RAN")\n', encoding="utf-8")
        (self.root / "tests" / "test_fixture.py").write_text(
            'import unittest\nclass Fixture(unittest.TestCase):\n'
            '    def test_example(self):\n        self.assertTrue(True)\n', encoding="utf-8")
        (self.root / "tests" / "payment-calculator.test.mjs").write_text(
            'import test from "node:test";\n'
            'test("NODE_FIXTURE_RAN", () => {});\n', encoding="utf-8")

    def run_verification(self, **kwargs):
        # Launch from outside the fixture to exercise repository-root resolution.
        return subprocess.run(
            [sys.executable, str(self.root / "scripts" / "verify.py")],
            cwd=self.root.parent, capture_output=True, text=True,
            timeout=20, check=False, **kwargs)

    @unittest.skipUnless(shutil.which("node"), "Node is required for integration checks")
    def test_success_runs_every_stage_without_creating_build_output(self):
        result = self.run_verification()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("STATIC_FIXTURE_RAN", result.stdout)
        self.assertIn("Ran 1 test", result.stderr)
        self.assertIn("NODE_FIXTURE_RAN", result.stdout)
        self.assertIn("All offline checks passed", result.stdout)
        self.assertFalse((self.root / "dist").exists())

    @unittest.skipUnless(shutil.which("node"), "Node is required for integration checks")
    def test_static_failure_stops_before_test_stages(self):
        (self.root / "scripts" / "check_site.py").write_text('raise SystemExit(7)\n')
        result = self.run_verification()
        self.assertEqual(result.returncode, 7)
        self.assertNotIn("Ran 1 test", result.stderr)
        self.assertNotIn("NODE_FIXTURE_RAN", result.stdout)
        self.assertNotIn("All offline checks passed", result.stdout)

    @unittest.skipUnless(shutil.which("node"), "Node is required for integration checks")
    def test_python_failure_stops_before_node_stage(self):
        path = self.root / "tests" / "test_fixture.py"
        path.write_text(path.read_text().replace("assertTrue(True)", "assertTrue(False)"))
        result = self.run_verification()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAILED", result.stderr)
        self.assertNotIn("NODE_FIXTURE_RAN", result.stdout)
        self.assertNotIn("All offline checks passed", result.stdout)

    @unittest.skipUnless(shutil.which("node"), "Node is required for integration checks")
    def test_node_failure_is_not_reported_as_success(self):
        path = self.root / "tests" / "payment-calculator.test.mjs"
        path.write_text('import test from "node:test";\n'
                        'test("NODE_FIXTURE_RAN", () => { throw new Error("fixture failure"); });\n')
        result = self.run_verification()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fixture failure", result.stdout + result.stderr)
        self.assertNotIn("All offline checks passed", result.stdout)

    def test_missing_node_fails_before_running_checks(self):
        import os
        environment = dict(os.environ, PATH="")
        result = self.run_verification(env=environment)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires Node.js", result.stderr)
        self.assertNotIn("STATIC_FIXTURE_RAN", result.stdout)
        self.assertNotIn("All offline checks passed", result.stdout)

if __name__ == "__main__":
    unittest.main()
