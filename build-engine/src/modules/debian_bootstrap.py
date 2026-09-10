from __future__ import annotations

import os
import shutil
import subprocess
from src.models.build_context import BuildContext
from src.models.pipeline_stage import ILogger


class DebianBootstrapper:
    """Real Debian 13 Trixie bootstrap using debootstrap."""

    def __init__(self, workspace_root: str, logger: ILogger) -> None:
        self._workspace = os.path.abspath(workspace_root)
        self._logger = logger

    def bootstrap(self, context: BuildContext, target_dir: str) -> bool:
        cfg = context.config.get("debian", {})
        bootstrap_cfg = cfg.get("bootstrap", {})

        suite = cfg.get("codename", "trixie")
        arch = cfg.get("architecture", "amd64")
        mirror = bootstrap_cfg.get(
            "mirror_url", "http://deb.debian.org/debian"
        )
        components = ",".join(
            bootstrap_cfg.get(
                "components",
                ["main", "contrib", "non-free", "non-free-firmware"],
            )
        )

        debootstrap = shutil.which("debootstrap") or "/usr/sbin/debootstrap"

        if not os.path.exists(debootstrap):
            raise RuntimeError("debootstrap executable not found")

        os.makedirs(target_dir, exist_ok=True)

        # Do not silently accept an already-created empty directory.
        if os.path.exists(os.path.join(target_dir, "etc", "debian_version")):
            self._logger.info("Existing Debian root filesystem detected; reusing it.")
            return True

        cmd = [
            debootstrap,
            f"--components={components}",
            f"--arch={arch}",
            suite,
            target_dir,
            mirror,
        ]

        self._logger.info("Executing real Debian bootstrap:")
        self._logger.info(" ".join(cmd))

        result = subprocess.run(
            cmd,
            cwd=self._workspace,
            text=True,
            capture_output=False,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"debootstrap failed with exit code {result.returncode}"
            )

        if not os.path.exists(os.path.join(target_dir, "etc", "debian_version")):
            raise RuntimeError(
                "debootstrap reported success but Debian root filesystem is missing"
            )

        context.metadata["base_os"] = "Debian 13 (Trixie)"
        context.metadata["bootstrap_target"] = target_dir

        self._logger.success("Real Debian 13 base root filesystem created.")
        return True
