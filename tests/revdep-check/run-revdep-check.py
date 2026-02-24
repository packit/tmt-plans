#!/usr/bin/python3
# /// script
# dependencies = [ ]
# ///

import argparse
import os
import subprocess
import sys


def install_revdep_check():
    """Install fedora-revdep-check from GitHub."""
    print("Installing fedora-revdep-check from GitHub...")
    result = subprocess.run(
        [
            "pip",
            "install",
            "git+https://github.com/fedora-python/fedora-revdep-check.git",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error installing fedora-revdep-check:\n{result.stderr}")
        sys.exit(1)
    print("Installation successful")


def run_revdep_check(package_name: str, package_version: str) -> tuple[int, str]:
    """
    Run fedora-revdep-check and return the result.

    Returns:
        tuple of (return_code, output)
    """
    print(f"Running fedora-revdep-check for {package_name} {package_version}")
    result = subprocess.run(
        ["fedora-revdep-check", package_name, package_version],
        capture_output=True,
        text=True,
    )

    output = result.stdout
    if result.stderr:
        output += f"\nStderr:\n{result.stderr}"

    return result.returncode, output


def main(args: argparse.Namespace) -> None:
    """
    Run reverse dependency check
    """
    if not args.package_name:
        print("Error: PACKAGE_NAME not provided")
        sys.exit(1)

    if not args.package_version:
        print("Error: PACKAGE_VERSION not provided")
        sys.exit(1)

    # Install the tool
    install_revdep_check()

    # Run the check
    return_code, output = run_revdep_check(args.package_name, args.package_version)

    print("\n" + "="*80)
    print("REVERSE DEPENDENCY CHECK OUTPUT:")
    print("="*80)
    print(output)
    print("="*80 + "\n")

    if output.strip() or return_code != 0:
        print("Reverse dependency check found issues (see output above)")
        sys.exit(return_code)

    print("No reverse dependency issues found!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run fedora-revdep-check on a package. "
        "Can also pass variables via environment variables."
    )
    parser.add_argument(
        "--package-name",
        help="Name of the package to check.",
        default=os.environ.get("PACKAGE_NAME"),
    )
    parser.add_argument(
        "--package-version",
        help="New version of the package.",
        default=os.environ.get("PACKAGE_VERSION"),
    )

    args = parser.parse_args()
    main(args)
