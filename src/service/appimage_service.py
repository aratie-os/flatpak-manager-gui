import os
import subprocess
import re
from pathlib import Path
from service.pkg_service import PkgService
from PySide6.QtCore import QProcess


class AppImageService(PkgService):
    def __init__(self, process: QProcess):
        self._is_su = os.getuid() == 0
        self.process = process
        self.is_user_in_group = False
        self.wrapper_path = "/usr/local/bin/appimage_manager_backend"

    def install(self, url: str):
        file_path = Path(url).resolve()
        cmd = [self.wrapper_path, "-i", str(file_path)]

        if not file_path.exists():
            raise Exception(f"Arquivo {file_path} não encontrado")

        if self._is_su:
            self.process.start(cmd[0], cmd[1:])
            return

        self.process.start("pkexec", cmd)

    def uninstall(self, base_name: str):
        cmd = [self.wrapper_path, "-r", base_name]

        if self._is_su:
            self.process.start(cmd[0], cmd[1:])
            return
        
        self.process.start("pkexec", cmd)

    def extract_name(self, base_name: str):
        name = Path(base_name).stem.replace(
            ".AppImage", "").replace("-x86_64", "").split("-")[0]
        
        replacements = {'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'é': 'e',
                        'ê': 'e', 'í': 'i', 'ó': 'o', 'õ': 'o', 'ô': 'o', 'ú': 'u', 'ç': 'c'}
        
        for char, rep in replacements.items():
            name = name.replace(char, rep)
            
        name = name.strip().replace(" ", "-").lower()
        return re.sub(r'[^a-z0-9.-]', '', name)

    def is_installed(self, base_name: str):
        base_name = self.extract_name(base_name)
        normalized = base_name + "appimage"

        return self._check_dpkg_status(normalized)

    def _check_dpkg_status(self, pkg_name: str) -> bool:
        try:
            result = subprocess.run(
                ["dpkg-query", "-W", "-f='${Status}'", pkg_name],
                capture_output=True, text=True
            )
            return "install ok installed" in result.stdout
        except:
            return False

