#!/usr/bin/python3

import sys
import argparse
import os
import subprocess
import shutil
from pathlib import Path


def main(args: argparse.Namespace) -> None:
    """
    Run fedora-review
    """
    if not args.spec_file:
        raise RuntimeError("No spec file provided")

    if not args.rpm_files:
        raise RuntimeError("No RPM files provided")

    # At this point, the RPM packages are already downloaded in `args.workdir`,
    # we just need to copy the .spec next to them
    shutil.copy(args.spec_file, args.workdir)

    env = os.environ.copy()
    env["REVIEW_NO_MOCKGROUP_CHECK"] = "true"

    name = Path(args.spec_file).stem
    cmd = ["fedora-review", "--prebuilt", "-n", name]
    print(f"Running: {" ".join(cmd)}")
    subprocess.run(cmd, cwd=args.workdir, env=env, check=True)

    result = os.path.join(args.workdir, "review-" + name, "review.json")
    if not os.path.exists(result):
        raise RuntimeError(f"Result JSON doesn't exist: {result}")

    print("Result: {0}".format(result))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Simple wrapper for fedora-review. "
            "Can also pass variables via environment variables."
        )
    )
    parser.add_argument(
        "--workdir",
        type=Path,
        default=os.environ.get("TMT_PLAN_DATA", "."),
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

    args = parser.parse_args()
    try:
        main(args)
    except RuntimeError as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
