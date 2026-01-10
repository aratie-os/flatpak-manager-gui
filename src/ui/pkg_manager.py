from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget,
                               QLabel, QProgressBar, QPushButton, QMessageBox)
from PySide6.QtCore import QProcess, Qt
from enum import Enum
import sys
from service.pkg_service import PkgService


class PKGAction(Enum):
    INSTALL = 0
    REMOVE = 1
    INSTALL_MULTI_PKG = 2
    AUTO = 3


class PkgManager(QMainWindow):
    def __init__(self, title: str, service: PkgService | None = None, action: PKGAction = None, other_progress_bar: QProgressBar | None = None):
        if action == None:
            action = PKGAction.AUTO

        super().__init__()
        self.setWindowTitle(title)
        self.setFixedSize(500, 250)
        self.pkg_action = action
        self.service = service

        # UI Setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.label = QLabel(f"<b>Verificando status...</b>")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        self.current_progress = QProgressBar()
        self.current_progress.setFormat("Ação atual: %p%")
        self.layout.addWidget(self.current_progress)

        if isinstance(other_progress_bar, QProgressBar):
            self.layout.addWidget(other_progress_bar)

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.close)
        self.layout.addWidget(self.btn_cancel)

        # Processo e Serviço
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.finished.connect(self.on_finished)

    def intialize_application(self):
        raise NotImplementedError(
            "Você precisa implementar este método nas subclasses!")

    def handle_stdout(self):
        raise NotImplementedError(
            "Você precisa implementar este método nas subclasses!")

    def on_finished(self, exit_code):
        if exit_code == 0:
            QMessageBox.information(
                self, "Sucesso", "Operação concluída com êxito!")
        else:
            QMessageBox.warning(
                self, "Aviso", "A operação foi encerrada ou apresentou erros.")
        self.close()

    def start_installation(self, target_name: str, target_ref: str):
        if self.pkg_action == PKGAction.AUTO and not self.msg_box_install(target_name):
            sys.exit(0)

        self.label.setText(f"<b>Instalando:</b> {target_name} 😎")
        try:
            self.service.install(target_ref)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha na instalação: {e}")
            sys.exit(1)

    def start_removal(self, target_name: str, target_ref: str):
        if self.pkg_action == PKGAction.AUTO and not self.msg_box_remove(self.target_name):
            sys.exit(0)

        self.label.setText(f"<b>Removendo:</b> {target_name} 😥")
        try:
            self.service.uninstall(target_ref)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha na remoção: {e}")
            sys.exit(1)

    def msg_box_remove(self, package_name: str):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Aplicativo já instalado")
        msg_box.setText(
            f"O pacote '{package_name}' já está instalado no sistema.")
        msg_box.setInformativeText("Deseja removê-lo?")
        btn_sim = msg_box.addButton(
            "Desinstalar", QMessageBox.YesRole)
        msg_box.addButton("Cancelar", QMessageBox.NoRole)
        msg_box.exec()

        return msg_box.clickedButton() == btn_sim

    def msg_box_install(self, package_name: str):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(f"Confirmação de instalação")
        msg_box.setText(
            f"O pacote '{package_name}' não está instalado no sistema.")
        msg_box.setInformativeText("Deseja instala-lo?")
        btn_sim = msg_box.addButton(
            "Instalar", QMessageBox.YesRole)
        msg_box.addButton("Cancelar", QMessageBox.NoRole)
        msg_box.exec()

        return msg_box.clickedButton() == btn_sim
