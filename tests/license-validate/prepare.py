#!/usr/bin/python3
# /// script
# dependencies = []
# ///
from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from utils import TestEnv

logger = logging.getLogger(Path(__file__).name)

# TODO: Move this to TestEnv
if __name__ == "__main__":
    try:
        env = TestEnv.from_env_variables()
        # Try to get the spec file
        env.spec_file  # noqa: B018
    except SystemExit:
        raise
    except subprocess.CalledProcessError:
        logger.error("Preparation failed!")
        raise SystemExit(1) from None
    except Exception as exc:
        logger.exception("Unexpected failure", exc_info=exc)
        raise SystemExit(2) from None
