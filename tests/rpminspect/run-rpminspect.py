#!/usr/bin/python3
# /// script
# dependencies = [
#   "requests",
#   "ruamel.yaml",
# ]
# ///

import argparse
import logging
import os
import subprocess
from pathlib import Path
from typing import TypedDict, Literal, NotRequired

import requests
from ruamel.yaml import YAML

logging.basicConfig(level="INFO")
logger = logging.getLogger(Path(__file__).name)


class Result(TypedDict):
    """
    Subset of tmt result that we will use.

    See https://tmt.readthedocs.io/en/stable/spec/results.html
    """

    name: str
    result: Literal["pass", "fail", "info", "warn", "error", "skip", "pending"]
    log: list[str]
    duration: NotRequired[str]


yaml = YAML()
results = {}
results["/"] = Result(
    name="/",
    result="pending",
    log=[
        "../output.txt",
    ],
)


def update_results(test_data: Path) -> None:
    with (test_data / "results.yaml").open("w") as f:
        yaml.dump(list(results.values()), f)


def main(args: argparse.Namespace) -> None:
    rpms_workdir: Path = args.workdir / "rpms"
    rpminspect_workdir: Path = args.workdir / "workdir"
    rpminspect_workdir.mkdir(exist_ok=True)
    result_json: Path = args.test_data / "result.json"
    before_build_args = []
    if args.last_build:
        before_build_args = [args.last_build]
    rpminspect_args = [
        f"--config={args.config}",
        f"--workdir={rpminspect_workdir}",
        "--format=json",
        f"--output={result_json}",
        "--verbose",
        f"--release={args.release}",
        f"--profile={args.profile}",
        # before-build
        *before_build_args,
        # after-build
        rpms_workdir,
    ]
    update_results(args.test_data)
    logger.info(f"Running rpminspect with: {rpminspect_args}")
    output = subprocess.run(["rpminspect", *rpminspect_args])
    if result_json.exists():
        response = requests.get(
            "https://raw.githubusercontent.com/rpminspect/rpminspect/main/contrib/viewer.html"
        )
        if not response.status_code == 200:
            logger.warning("Could not get the viewer.html")
        else:
            viewer_html: Path = args.test_data / "viewer.html"
            viewer_html.write_text(response.text)
            results["/"]["log"] = [
                "viewer.html",
                "result.json",
                *results["/"]["log"],
            ]
    match output.returncode:
        case 0:
            results["/"]["result"] = "pass"
        case 1:
            results["/"]["result"] = "fail"
        case _:
            results["/"]["result"] = "error"
    update_results(args.test_data)
    if output.returncode:
        exit(output.returncode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Simple wrapper for rpmlint. Can also pass variables via environment variables."
    )
    parser.add_argument(
        "--workdir",
        type=Path,
        default=os.environ.get("TMT_PLAN_DATA", "."),
    )
    parser.add_argument(
        "--test-data",
        type=Path,
        default=os.environ.get("TMT_TEST_DATA", "."),
    )
    parser.add_argument(
        "--profile",
        metavar="RPMINSPECT_PROFILE/DIST_GIT_BRANCH",
        help="Rpminspect configuration profile to use.",
        default=os.environ.get(
            "RPMINSPECT_PROFILE",
            os.environ.get("DIST_GIT_BRANCH", "rawhide"),
        ),
    )
    parser.add_argument(
        "--config",
        metavar="RPMINSPECT_CONFIG",
        help="Rpminspect config file to override.",
        default=os.environ.get("RPMINSPECT_CONFIG"),
    )
    parser.add_argument(
        "--release",
        metavar="RPMINSPECT_RELEASE",
        help="Default release tag.",
        default=os.environ.get("RPMINSPECT_RELEASE"),
    )
    parser.add_argument(
        "--last-build",
        metavar="RPMINSPECT_LAST_BUILD",
        help="Last build of the package.",
        default=os.environ.get("RPMINSPECT_LAST_BUILD"),
    )

    args = parser.parse_args()
    try:
        main(args)
    except (subprocess.CalledProcessError, SystemExit):
        logger.error("Rpminspect failed!")
        raise SystemExit(1)
    except Exception as exc:
        logger.error("Unexpected rpminspect failure", exc_info=exc)
        raise SystemExit(2)
