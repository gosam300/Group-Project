#!/usr/bin/env python3
"""
Run all tests for the Record Management System
"""

import sys
import subprocess


def run_tests():
    """Run all test modules"""
    test_modules = [
        "test_models.py",
        "test_storage.py",
        "test_models_storage_integration.py"
    ]

    results = []

    for module in test_modules:
        print(f"\n{'=' * 60}")
        print(f"Running tests in {module}")
        print('=' * 60)

        result = subprocess.run(
            [sys.executable, "-m", "pytest", module, "-v"],
            capture_output=True,
            text=True
        )

        print(result.stdout)
        if result.stderr:
            print(f"Errors in {module}:")
            print(result.stderr)

        results.append((module, result.returncode))

    # Summary
    print(f"\n{'=' * 60}")
    print("TEST SUMMARY")
    print('=' * 60)

    all_passed = True
    for module, returncode in results:
        status = "PASSED" if returncode == 0 else "FAILED"
        print(f"{module}: {status}")
        if returncode != 0:
            all_passed = False

    print(f"\nOverall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    run_tests()

