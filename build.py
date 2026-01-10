import os
import subprocess
from dotenv import load_dotenv
import sys

load_dotenv()

APP_NAME = os.getenv("APP_NAME")
VERSION = os.getenv("VERSION")
MAINTAINER = os.getenv("MAINTAINER")


def build():
    print("--- Iniciando Build do ELF ---")
    subprocess.run([
        "pyinstaller", "--onefile", "--windowed",
        f"--name={APP_NAME}", "./src/main.py"
    ], check=True)

    print("--- Criando estrutura do pacote DEB ---")
    working_dir = f"/tmp/{APP_NAME}-build"

    if os.path.exists(working_dir):
        subprocess.run(["rm", "-rf", working_dir])

    os.makedirs(f"{working_dir}/DEBIAN", exist_ok=True)
    os.makedirs(f"{working_dir}/usr/bin", exist_ok=True)
    os.makedirs(f"{working_dir}/usr/local/bin", exist_ok=True)
    os.makedirs(f"{working_dir}/usr/share/polkit-1/actions", exist_ok=True)
    os.makedirs(f"{working_dir}/usr/share/applications", exist_ok=True)

    print("--- Copiando arquivos ---")
    subprocess.run(["cp", f"dist/{APP_NAME}",
                   f"{working_dir}/usr/bin/"], check=True)
    subprocess.run(
        ["chmod", "755", f"{working_dir}/usr/bin/{APP_NAME}"], check=True)

    subprocess.run(["cp", "appimage_manager_backend",
                   f"{working_dir}/usr/local/bin/"], check=True)
    subprocess.run(
        ["chmod", "755", f"{working_dir}/usr/local/bin/appimage_manager_backend"], check=True)

    subprocess.run(["cp", "br.com.aratie.appimagemanagerbackend.policy",
                   f"{working_dir}/usr/share/polkit-1/actions/"], check=True)

    subprocess.run(["cp", "pkg-manager-gui.desktop",
                   f"{working_dir}/usr/share/applications/"], check=True)

    print("--- Gerando arquivo de controle ---")
    control_content = f"""Package: {APP_NAME}
Version: {VERSION}
Section: utils
Priority: optional
Architecture: amd64
Maintainer: {MAINTAINER}
Depends: flatpak
Description: {os.getenv("DESCRIPTION")}
"""

    with open(f"{working_dir}/DEBIAN/control", "w") as f:
        f.write(control_content)

    print("--- Gerando script postinst ---")
    postinst_content = """#!/bin/sh
set -e

if [ -x /usr/bin/update-desktop-database ]; then
    update-desktop-database /usr/share/applications
fi

if [ -x /usr/bin/update-mime-database ]; then
    update-mime-database /usr/share/mime
fi
"""

    postinst_path = f"{working_dir}/DEBIAN/postinst"
    with open(postinst_path, "w") as f:
        f.write(postinst_content)

    subprocess.run(["chmod", "755", postinst_path], check=True)

    os.makedirs("./dist", exist_ok=True)
    print("--- Empacotando .deb ---")
    subprocess.run(["dpkg-deb", "--build", working_dir,
                   f"./dist/{APP_NAME}.deb"], check=True)
    print(f"--- Sucesso: {APP_NAME}.deb gerado! ---")


if __name__ == "__main__":
    build()
