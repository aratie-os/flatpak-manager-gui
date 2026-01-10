import os
from service.pkg_service import PkgService
from PySide6.QtCore import QProcess
from utils.grp_utils import GroupUtils
from utils.str_utils import StrUtils
import subprocess
from pathlib import Path


class FlatpakService(PkgService):
    def __init__(self, process: QProcess):
        self._is_su = os.getuid() == 0
        self.process = process
        self.is_user_in_flatpak_group = GroupUtils(
        ).is_user_in_group(os.getenv("USER"), "flatpak")

    def install(self, url: str):
        file_path = Path(url).resolve()

        if not file_path.exists():
            raise Exception(f"Arquivo {file_path} não encontrado")

        cmd = ["flatpak", "install", str(
            file_path), "-y", "--no-static-deltas"]

        if self._is_su or self.is_user_in_flatpak_group:
            self.process.start(cmd[0], cmd[1:])
            return

        self.process.start("pkexec", cmd)

    def uninstall(self, base_name: str):
        app_id = self._extract_app_id(base_name)
        cmd = ["flatpak", "uninstall", app_id, "-y"]

        if self._is_su or self.is_user_in_flatpak_group:
            self.process.start(cmd[0], cmd[1:])
            return

        self.process.start("pkexec", cmd)

    def _extract_app_id(self, url: str) -> str:
        return url.replace(".flatpakref", "").replace(".flatpak", "")

    def extract_name(self, base_name: str):
        name = self._extract_app_id(base_name).split(".")[-1]
        return StrUtils.split_camel_case(name)

    def is_installed(self, base_name: str):
        app_id = self._extract_app_id(base_name)

        try:
            result = subprocess.run(
                ["flatpak", "list", "--columns=application"],
                capture_output=True, text=True
            )
            return app_id in result.stdout
        except:
            return False
