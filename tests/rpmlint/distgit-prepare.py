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
import shutil
import subprocess
from pathlib import Path
from typing import Any

import tomli_w

import utils

logging.basicConfig(level="INFO")
logger = logging.getLogger(Path(__file__).name)

CI_CONFIG_SECTION = "rpmlint"

RPMLINT_TOML_FILES = [
    "./fedora-ci.toml",
]


def export_rpmlint_tomls(custom_file: Path) -> None:
    workdir = utils.get_workdir()
    rpmlint_data_dir = workdir / "rpmlint"
    rpmlint_data_dir.mkdir(exist_ok=True)
    for toml_file in RPMLINT_TOML_FILES:
        shutil.copy(toml_file, rpmlint_data_dir)
    if custom_file.exists():
        logger.info("Found custom rpmlint.toml file")
        shutil.copy(custom_file, rpmlint_data_dir)
    utils.save_env("RPMLINT_TOML_FILE", rpmlint_data_dir)


def set_config_files(config: dict[str, Any]) -> None:
    workdir = utils.get_workdir()
    if rc_content := config.get("rc"):
        rc_content: str
        rc_file: Path = workdir / "rpmlintrc"
        rc_file.write_text(rc_content)
        utils.save_env("RPMLINT_RC_FILE", rc_file)
    distgit_toml_file: Path = workdir / "rpmlint.toml"
    if toml_content := config.get("toml"):
        toml_content: dict[str, Any]
        with distgit_toml_file.open("wb") as f:
            tomli_w.dump(toml_content, f)
    export_rpmlint_tomls(distgit_toml_file)


def get_config_fallback(dist_git_path: Path) -> None:
    rc_files = list(dist_git_path.glob("*.rpmlintrc"))
    if len(rc_files) > 1:
        logger.warning("More than 1 rpmlintrc file found")
    if rc_files:
        logger.info("Found rpmlintrc file")
        utils.save_env("RPMLINT_RC_FILE", rc_files[0])
    toml_file = dist_git_path / "rpmlint.toml"
    export_rpmlint_tomls(toml_file)


def main(args: argparse.Namespace) -> None:
    """
    Prepare for rpmlint from a dist-git
    """
    dist_git_path = utils.get_dist_git(args.koji_task_id)

    if config := utils.get_config(dist_git_path, CI_CONFIG_SECTION):
        set_config_files(config)
    else:
        get_config_fallback(dist_git_path)

    utils.get_koji_build(args.koji_task_id)

    # Find the other files
    # TODO: The SRPM should be enough?
    spec_files = list(dist_git_path.glob("*.spec"))
    if len(spec_files) > 1:
        logger.warning("More than 1 spec file found")
    if spec_files:
        utils.save_env("SPEC_FILE", spec_files[0])
    else:
        logger.error("No spec file found?")
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--koji-task-id", default=os.environ.get("KOJI_TASK_ID"))

    args = parser.parse_args()
    try:
        main(args)
    except (subprocess.CalledProcessError, SystemExit):
        logger.error("Prepare failed!")
        raise SystemExit(1)
    except Exception as exc:
        logger.error("Unexpected prepare failure", exc_info=exc)
        raise SystemExit(2)
