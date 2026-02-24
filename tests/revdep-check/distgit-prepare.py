#!/usr/bin/python3
# /// script
# dependencies = [ ]
# ///

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


def parse_nvr(nvr: str) -> tuple[str, str, str]:
    """
    Parse NVR (Name-Version-Release) string.

    Since package names can contain hyphens, we parse from the right.
    Format: name-version-release
    """
    # Split from the right: last part is release, second-to-last is version
    parts = nvr.rsplit("-", 2)
    if len(parts) != 3:
        raise ValueError(f"Invalid NVR format: {nvr}")

    name, version, release = parts
    return name, version, release


def get_package_info_from_koji(task_id: str) -> tuple[str, str] | None:
    """
    Try to get package info from koji taskinfo.

    Returns:
        tuple of (package_name, package_version) or None if not available
    """
    print(f"Getting task info for koji task {task_id}")
    result = subprocess.run(
        ["koji", "taskinfo", task_id],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Warning: Error getting koji task info: {result.stderr}")
        return None

    task_info = result.stdout
    print(f"Task info:\n{task_info}")

    # Look for the Build line which contains NVR and build ID
    # Format: "Build: package-name-version-release [build_id]"
    build_match = re.search(r"^Build:\s*(\S+)\s*\(\d+\)", task_info, re.MULTILINE)

    if not build_match:
        print("Warning: Could not find build information in koji taskinfo output")
        return None

    nvr = build_match.group(1)

    print(f"Found build: {nvr}")

    # Parse NVR to get package name and version
    try:
        package_name, package_version, release = parse_nvr(nvr)
        print(f"Parsed: name={package_name}, version={package_version}, release={release}")
        return package_name, package_version
    except ValueError as e:
        print(f"Warning: Error parsing NVR: {e}")
        return None


def get_package_info_from_srpm(task_id: str, workdir: Path) -> tuple[str, str]:
    """
    Get package info by downloading koji artifacts and querying the SRPM.

    Returns:
        tuple of (package_name, package_version)
    """
    print("Falling back to SRPM download method")

    # Download artifacts from the koji task
    print(f"Downloading artifacts from koji task {task_id}")
    result = subprocess.run(
        ["koji", "download-build", task_id],
        cwd=workdir,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Error downloading koji task: {result.stderr}")
        sys.exit(1)

    # Find the SRPM
    srpm_files = list(workdir.glob("*.src.rpm"))

    if not srpm_files:
        print("Error: No SRPM file found in downloaded artifacts")
        sys.exit(1)

    if len(srpm_files) > 1:
        print("Warning: Multiple SRPM files found, using first one")

    srpm_file = srpm_files[0]
    print(f"Using SRPM: {srpm_file}")

    # Query the SRPM for NVR (returns name-version-release format)
    result = subprocess.run(
        ["rpm", "-qp", str(srpm_file)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Error querying SRPM: {result.stderr}")
        sys.exit(1)

    # Parse NVR to get package name and version
    try:
        package_name, package_version, release = parse_nvr(result.stdout.strip())
        print(f"Found package from SRPM: {package_name} version: {package_version}")
        return package_name, package_version
    except ValueError as e:
        print(f"Error parsing NVR from SRPM: {e}")
        sys.exit(1)


def main(args: argparse.Namespace) -> None:
    """
    Prepare for revdep-check from a dist-git.

    Tries to get package info from koji taskinfo first (fast),
    falls back to downloading SRPM and querying it with rpm (reliable).
    """
    args.env_file: Path

    # First try the fast method using koji taskinfo
    package_info = get_package_info_from_koji(args.koji_task_id)

    # If that doesn't work, fall back to downloading and querying SRPM
    if package_info is None:
        package_name, package_version = get_package_info_from_srpm(
            args.koji_task_id, args.workdir
        )
    else:
        package_name, package_version = package_info

    # Write to environment file
    with args.env_file.open("a") as f:
        f.write(f"PACKAGE_NAME={package_name}\n")
        f.write(f"PACKAGE_VERSION={package_version}\n")

    print(f"Successfully prepared: {package_name} {package_version}")


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
