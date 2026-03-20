#!/usr/bin/python3
# /// script
# dependencies = [ ]
# ///

import argparse
import os
import subprocess
import sys


def main(args: argparse.Namespace) -> None:
    """
    Run rpmlint
    """
    rpmlint_args = []
    if args.spec_file:
        rpmlint_args.append(args.spec_file)
    print(f"Running: license-validate -v --spec {rpmlint_args}")
    result = subprocess.run(["license-validate", "-v", "--spec", *rpmlint_args])
    if result.returncode != 0:
        print(f"Error: license-validate failed with exit code {result.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Simple wrapper for license-validate. Can also pass variables via environment variables."
    )
    parser.add_argument(
        "--spec-file",
        help="Spec file to check.",
        default=os.environ.get("SPEC_FILE"),
    )

    args = parser.parse_args()
    main(args)
