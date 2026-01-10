import os
import re
from service.appimage_service import AppImageService
from ui.pkg_manager import PkgManager, PKGAction

class AppImageManager(PkgManager):
    def __init__(self, target_url: str, action: PKGAction | None = None):
        super().__init__(title="AppImage Manager", action=action)

        self.service = AppImageService(self.process)
        self.target_url = target_url
        self.target_base_name = os.path.basename(self.target_url)
        self.target_name = self.service.extract_name(self.target_base_name)

        self.intialize_application()

    def intialize_application(self): 
        self.current_progress.setRange(0, 0) 
        if self.service.is_installed(self.target_base_name) or self.pkg_action == PKGAction.REMOVE:
            self.start_removal(self.target_name, self.target_base_name)
        else:
            self.start_installation(self.target_name, self.target_url)

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        match = re.search(r'(\d+)%', data)
        if match:
            self.current_progress.setValue(int(match.group(1)))