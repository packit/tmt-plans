#!/usr/bin/python3
# /// script
# dependencies = [ ]
# ///

import argparse
import logging
import os
import subprocess
from pathlib import Path

logging.basicConfig(level="INFO")
logger = logging.getLogger(Path(__file__).name)


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
    logger.info(f"Running rpmlint with: {rpmlint_args}")
    subprocess.run(
        ["rpmlint", *rpmlint_args],
        check=True,
    )


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
    try:
        main(args)
    except (subprocess.CalledProcessError, SystemExit):
        logger.error("Rpmlint failed!")
        raise SystemExit(1)
    except Exception as exc:
        logger.error("Unexpected rpmlint failure", exc_info=exc)
        raise SystemExit(2)
