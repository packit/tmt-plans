import logging
import re
import sys
import subprocess
import tomllib
from pathlib import Path
from typing import Any

logger = logging.getLogger("tmt_plans.utils")

CI_CONFIG_FILES = [
    "fedora-ci.yaml",
    "fedora-ci.yml",
    "fedora-ci.toml",
]


def get_config(dist_git_path: Path, section: str) -> dict[str, Any] | None:
    from ruamel.yaml import YAML

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
        elif ci_file.suffix in [".yaml", ".yml"]:
            full_config = YAML().load(f)
        else:
            raise AssertionError("Trying to load a file not listed in CI_CONFIG_FILES")

    if not (tools := full_config.get("tools")):
        logger.info("No `tools` section found")
        return None
    if not (config := tools.get(section)):
        logger.info(f"No `tools.{section}` section found")
        return None
    return config


def get_dist_git(koji_task_id: str, workdir: Path) -> Path:
    result = subprocess.run(
        [
            "koji",
            "taskinfo",
            "-v",
            koji_task_id,
        ],
        capture_output=True,
        text=True,
        check=True,
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
    dist_git_path = workdir / "dist-git"
    subprocess.run(
        ["git", "clone", repo_url, dist_git_path],
        check=True,
    )
    subprocess.run(
        ["git", "checkout", "-d", repo_ref],
        cwd=dist_git_path,
        check=True,
    )
    return dist_git_path


def get_koji_build(
    koji_task_id: str,
    workdir: Path,
    env_file: Path | None = None,
    arch: str | None = None,
) -> None:
    # TODO: Migrate these to tmt artifacts when possible
    arch_flags = set()
    if arch:
        arch_flags.add(f"--arch={arch}")
        arch_flags.add("--arch=noarch")
        arch_flags.add("--arch=srpm")
    subprocess.run(
        [
            "koji",
            "download-task",
            koji_task_id,
            *arch_flags,
        ],
        cwd=workdir,
        check=True,
    )
    if env_file:
        with env_file.open("a") as f:
            f.write(f"RPM_FILES={workdir}/*.rpm\n")


def get_bodhi_update(
    update_id: str,
    workdir: Path,
    env_file: Path | None = None,
    arch: str | None = None,
) -> None:

    # TODO: Migrate these to tmt artifacts when possible
    arch_flag = f"--arch={arch}" if arch else "--arch=all"
    subprocess.run(
        [
            "bodhi",
            "updates",
            "download",
            # we don't need signed packages for rmdepcheck so this
            # avoids problems if koji can't find the signed ones
            "--no-gpg",
            f"--updateid={update_id}",
            arch_flag,
        ],
        cwd=workdir,
        check=True,
    )
    if env_file:
        with env_file.open("a") as f:
            f.write(f"RPM_FILES={workdir}/*.rpm\n")
