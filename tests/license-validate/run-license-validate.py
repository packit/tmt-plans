#!/usr/bin/python3
# /// script
# dependencies = [ ]
# ///
from __future__ import annotations

import argparse
import logging
import os
import subprocess
from pathlib import Path

logger = logging.getLogger(Path(__file__).name)


# TODO: Move this to TestEnv
def main(args: argparse.Namespace) -> None:
    component_name = os.path.basename(args.spec_file).removesuffix(".spec")  # noqa: PTH119

    logger.info(
        "Running: license-validate -v --spec %s --package %s",
        args.spec_file,
        component_name,
    )
    subprocess.run(
        [
            "license-validate",
            "-v",
            "--spec",
            args.spec_file,
            "--package",
            component_name,
        ],
        check=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Simple wrapper for license-validate.",
    )
    parser.add_argument(
        "--spec-file",
        help="Spec file to check.",
        default=os.environ.get("SPEC_FILE"),
    )

    args = parser.parse_args()
    try:
        main(args)
    except (subprocess.CalledProcessError, SystemExit):
        logger.error("license-validate failed!")
        raise SystemExit(1) from None
    except Exception as exc:
        logger.exception("Unexpected failure", exc_info=exc)
        raise SystemExit(2) from None
