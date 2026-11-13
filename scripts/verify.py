#!/usr/bin/env python3
"""Run all offline checks without building output or enabling services."""
from pathlib import Path
import shutil
import subprocess
import sys

def main():
    root = Path(__file__).resolve().parents[1]
    node = shutil.which("node")
    if node is None:
        print("Verification requires Node.js 18 or newer for payment-preparation tests.", file=sys.stderr)
        return 1
    commands = (
        [sys.executable, str(root / "scripts/check_site.py")],
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        [node, "--test", "tests/payment-calculator.test.mjs"],
    )
    for command in commands:
        result = subprocess.run(command, cwd=root, check=False)
        if result.returncode:
            return result.returncode
    print("All offline checks passed. No deployment, intake or payments enabled.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
