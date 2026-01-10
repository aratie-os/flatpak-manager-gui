from PySide6.QtWidgets import (QMainWindow)
from ui.flatpak_manager import FlatpakManager
from ui.appimage_manager import AppImageManager
from ui.notfound_manager import NotFoundManager


class BuildUi:
    @classmethod
    def AutoInferPkg(cls, url: str) -> QMainWindow:
        url_lower = url.lower()
        if url_lower.endswith('flatpakref'):
            return FlatpakManager(url)
        elif url.endswith('appimage'):
            return AppImageManager(url)

        return NotFoundManager()
