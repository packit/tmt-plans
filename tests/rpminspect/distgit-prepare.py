#!/usr/bin/python3
# /// script
# dependencies = [
#   "ruamel.yaml",
# ]
# ///

import argparse
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Literal

import koji
from ruamel.yaml import YAML

import utils

logging.basicConfig(level="INFO")
logger = logging.getLogger(Path(__file__).name)

CI_CONFIG_SECTION = "rpminspect"


def set_config_files(config: dict[str, Any], workdir: Path) -> None:
    config_file: Path = workdir / "rpminspect.yaml"
    yaml = YAML()
    with config_file.open("wb") as f:
        yaml.dump(config, f)


def get_config_fallback(dist_git_path: Path, workdir: Path) -> None:
    config_files = list(dist_git_path.glob("rpminspect.*"))
    if len(config_files) > 1:
        logger.warning(f"More than 1 rpminspect config file found: {config_files}")
    if config_files:
        logger.info(f"Using config file: {config_files[0]}")
        shutil.copy(config_files[0], workdir)


def get_release_tag(dist_git_branch: str) -> str:
    # Special handling for eln since the `%{?dist}` is not predictable
    if dist_git_branch == "eln":
        koji_session = utils.get_koji_session()
        try:
            configs = koji_session.getBuildConfig("eln-build")
            eln_macro = configs["extra"]["rpm.macro.eln"]
        except Exception:
            logger.error("Failed to get eln distro tag")
            exit(1)
        return f"eln{eln_macro}"

    release = utils.get_bodhi_release(dist_git_branch)

    match release.id_prefix:
        case "FEDORA":
            return f"fc{release.version}"
        case "FEDORA-EPEL", "FEDORA-EPEL-NEXT":
            return f"el{release.version.replace('.', '_')}"
        case _:
            raise AssertionError


def main(
    artifact_type: Literal["koji-task", "bodhi-update"], args: argparse.Namespace
) -> None:
    dist_git_path = utils.get_dist_git(args.koji_task_id, args.workdir)

    rpms_workdir: Path = args.workdir / "rpms"
    rpms_workdir.mkdir(exist_ok=True)

    if config := utils.get_config(dist_git_path, CI_CONFIG_SECTION):
        set_config_files(config, rpms_workdir)
    else:
        get_config_fallback(dist_git_path, rpms_workdir)

    match artifact_type:
        case "koji-task":
            package = next(dist_git_path.glob("*.spec")).stem
            last_build = utils.get_last_build(args.dist_git_branch, package)
            if last_build:
                logger.info(f"Found previous build: {last_build}")
            release_tag = get_release_tag(args.dist_git_branch)
            logger.info(f"Determined release tag: {release_tag}")
            with args.env_file.open("a") as f:
                f.write(f"RPMINSPECT_RELEASE={release_tag}\n")
                if last_build:
                    f.write(f"RPMINSPECT_LAST_BUILD={last_build}\n")
            utils.get_koji_build(args.koji_task_id, rpms_workdir)
        case "bodhi-update":
            # TODO: Need to download the rpms in separate subfolders
            # TODO: Need to separate the results for each sub-run
            raise NotImplementedError
        case _:
            raise NotImplementedError


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
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
    parser.add_argument(
        "--dist-git-branch",
        default=os.environ.get("DIST_GIT_BRANCH", ""),
    )

    actions = parser.add_subparsers(required=True, dest="action")

    koji_parser = actions.add_parser("koji-task")
    koji_parser.add_argument("koji_task_id")

    bodhi_parser = actions.add_parser("bodhi-update")
    bodhi_parser.add_argument("bodhi_update_id")

    args = parser.parse_args()

    try:
        match args.action:
            case "koji-task":
                main("koji-task", args)
            case "bodhi-update":
                main("bodhi-update", args)
            case _:
                raise NotImplementedError
    except SystemExit:
        raise
    except subprocess.CalledProcessError:
        logger.error("Prepare failed")
        raise SystemExit(1)
    except Exception as exc:
        logger.error("Unexpected prepare failure", exc_info=exc)
        raise SystemExit(2)
