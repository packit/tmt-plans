#!/usr/bin/python3
# /// script
# dependencies = [ ]
# ///

import argparse
import os
import re
import subprocess
from pathlib import Path


def main(args: argparse.Namespace) -> None:
    """
    Prepare for rpmlint from a copr-build
    """
    args.env_file: Path

    # TODO: Get the data from copr.
    # For now we assume a testing-farm environment.
    with args.env_file.open("a") as f:
        f.write("RPM_FILES=/var/share/test-artifacts/*.rpm\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--copr-project", default=os.environ.get("PACKIT_COPR_PROJECT"))
    # TODO: Get the data from copr.
    # TODO: Get the rpmlint that upstream passes somehow
    parser.add_argument(
        "--workdir",
        type=Path,
        default=os.environ.get("TMT_PLAN_DATA", "."),
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=os.environ.get("TMT_PLAN_ENVIRONMENT_FILE", ".env"),
    )

    args = parser.parse_args()
    main(args)
