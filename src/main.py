import sys
from PySide6.QtWidgets import (QApplication)
from factory.ui_factory import BuildUi

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if len(sys.argv) < 2:
        print("Uso: flatpak-manager-gui <url/arquivo>")
        sys.exit(1)

    window = BuildUi.AutoInferPkg(sys.argv[1])
    window.show()
    sys.exit(app.exec())
