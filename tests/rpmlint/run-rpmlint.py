#!/usr/bin/python3
# /// script
# dependencies = [ ]
# ///

import argparse
import os
import subprocess


def main(args: argparse.Namespace) -> None:
    """
    Run rpmlint
    """
    rpmlint_args = []
    if args.rc_file:
        rpmlint_args.extend(["-r", args.rc_file])
    if args.toml_file:
        rpmlint_args.extend(["-c", args.toml_file])
    if args.spec_file:
        rpmlint_args.append(args.spec_file)
    if args.rpm_files:
        rpmlint_args.append(args.rpm_files)
    print(f"Running rpmlint with: {rpmlint_args}")
    subprocess.run(["rpmlint", *rpmlint_args])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Simple wrapper for rpmlint. Can also pass variables via environment variables."
    )
    parser.add_argument(
        "--spec-file",
        help="Spec file to check.",
        default=os.environ.get("SPEC_FILE"),
    )
    parser.add_argument(
        "--rpm-files",
        help="RPM files to check. Can be wildcard.",
        default=os.environ.get("RPM_FILES"),
    )
    parser.add_argument(
        "--rc-file",
        metavar="RPMLINT_RC_FILE",
        help=".rpmlintrc file.",
        default=os.environ.get("RPMLINT_RC_FILE"),
    )
    parser.add_argument(
        "--toml-file",
        metavar="RPMLINT_TOML_FILE",
        help="Rpmlint toml file to override.",
        default=os.environ.get("RPMLINT_TOML_FILE"),
    )
    # TODO: Process the test results?

    args = parser.parse_args()
    main(args)
