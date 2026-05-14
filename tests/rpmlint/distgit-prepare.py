#!/usr/bin/python3
# /// script
# dependencies = [
#   "ruamel.yaml",
#   "tomli-w",
# ]
# ///

import argparse
import logging
import os
import re
import sys
import subprocess
import tomllib
from pathlib import Path
from typing import Any

import tomli_w
from ruamel.yaml import YAML

logging.basicConfig(level="INFO")
logger = logging.getLogger(Path(__file__).name)

CI_CONFIG_SECTION = "rpmlint"
CI_CONFIG_FILES = [
    "ci.yaml",
    "ci.yml",
    "ci.toml",
    "fedora-ci.yaml",
    "fedora-ci.yml",
    "fedora-ci.toml",
]


def get_config_from_ci_yaml(dist_git_path: Path) -> dict[str, Any] | None:
    for ci_file_name in CI_CONFIG_FILES:
        ci_file = dist_git_path / ci_file_name
        if ci_file.exists():
            break
    else:
        return None

    logger.info(f"Found config file {ci_file_name}")
    with ci_file.open("rb") as f:
        if ci_file.suffix == ".toml":
            full_config = tomllib.load(f)
        else:
            full_config = YAML().load(f)

    if not (tools := full_config.get("tools")):
        logger.info("No `tools` section found")
        return None
    if not (config := tools.get(CI_CONFIG_SECTION)):
        logger.info(f"No `tools.{config}` section found")
        return None
    return config


def set_config_files(config: dict[str, Any], args: argparse.Namespace) -> None:
    if rc_content := config.get("rc"):
        rc_content: str
        rc_file: Path = args.workdir / "rpmlintrc"
        rc_file.write_text(rc_content)
        with args.env_file.open("a") as f:
            f.write(f"RPMLINT_RC_FILE={rc_file}\n")
    if toml_content := config.get("toml"):
        toml_content: dict[str, Any]
        toml_file: Path = args.workdir / "rpmlint.toml"
        with toml_file.open("wb") as f:
            tomli_w.dump(toml_content, f)
        with args.env_file.open("a") as f:
            f.write(f"RPMLINT_TOML_FILE={toml_file}\n")


def get_config_fallback(dist_git_path: Path, args: argparse.Namespace) -> None:
    rc_files = list(dist_git_path.glob("*.rpmlintrc"))
    if len(rc_files) > 1:
        logger.warning("More than 1 rpmlintrc file found")
    if rc_files:
        logger.info("Found rpmlintrc file")
        with args.env_file.open("a") as f:
            f.write(f"RPMLINT_RC_FILE={rc_files[0]}\n")
    toml_file = dist_git_path / "rpmlint.toml"
    if toml_file.exists():
        logger.info("Found rpmlint.toml file")
        with args.env_file.open("a") as f:
            f.write(f"RPMLINT_TOML_FILE={toml_file}\n")


def main(args: argparse.Namespace) -> None:
    """
    Prepare for rpmlint from a dist-git
    """
    args.env_file: Path

    # Get the basic build information from koji
    result = subprocess.run(
        [
            "koji",
            "taskinfo",
            "-v",
            args.koji_task_id,
        ],
        capture_output=True,
        text=True,
    )
    task_info = result.stdout
    task_error = result.stderr
    logger.info(f"Task info output:\n{task_info}\nTask error:\n{task_error}")
    source_match_obj = re.search(r"Source:\s*(.*)", task_info)
    if source_match_obj is None:
        logger.error(
            "Could not find 'Source:' in koji taskinfo output. Maybe a 500 error? Please retry."
        )
        sys.exit(1)
    source = source_match_obj.group(1)
    source_match = re.search(r"git\+(?P<url>.*)#(?P<ref>.*)", source)
    repo_url = source_match.group("url")
    repo_ref = source_match.group("ref")

    # Clone the dist-git used in the build
    dist_git_path: Path = args.workdir / "dist-git"
    subprocess.run(["git", "clone", repo_url, dist_git_path])
    subprocess.run(["git", "checkout", "-d", repo_ref], cwd=dist_git_path)

    if config := get_config_from_ci_yaml(dist_git_path):
        set_config_files(config, args)
    else:
        get_config_fallback(dist_git_path, args)

    # Find the files to lint
    # TODO: Migrate these to tmt artifacts when possible
    spec_files = list(dist_git_path.glob("*.spec"))
    if len(spec_files) > 1:
        logger.warning("More than 1 spec file found")
    if spec_files:
        with args.env_file.open("a") as f:
            f.write(f"SPEC_FILE={spec_files[0]}\n")
    else:
        logger.error("No spec file found?")
    subprocess.run(
        ["koji", "download-task", args.koji_task_id],
        cwd=args.workdir,
    )
    with args.env_file.open("a") as f:
        f.write(f"RPM_FILES={args.workdir}/*.rpm\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--koji-task-id", default=os.environ.get("KOJI_TASK_ID"))
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
