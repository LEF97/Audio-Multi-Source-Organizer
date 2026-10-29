"""Service de téléchargement et d'installation automatique des binaires LibVLC pour AMSO.

Permet de rendre AMSO 100% autonome sur Windows en téléchargeant l'archive
officielle de VLC et en extrayant uniquement les composants audio nécessaires
(libvlc.dll, libvlccore.dll et plugins/) dans le répertoire AppData local.
"""

from __future__ import annotations

import logging
import os
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal

from amso.core.database import get_default_data_dir
from amso.core.i18n import tr
from amso.services.vlc_info import setup_macos_user_vlc

logger = logging.getLogger(__name__)

# URL officielle de l'archive ZIP 64-bit de VideoLAN
VLC_ZIP_URLS = [
    "https://download.videolan.org/pub/videolan/vlc/3.0.21/win64/vlc-3.0.21-win64.zip",
    "https://get.videolan.org/vlc/3.0.21/win64/vlc-3.0.21-win64.zip",
]


def get_local_vlc_dir() -> Path:
    """Retourne l'emplacement du dossier local VLC dans les données de l'application."""
    vlc_dir = get_default_data_dir() / "vlc"
    vlc_dir.mkdir(parents=True, exist_ok=True)
    return vlc_dir


def is_local_vlc_installed() -> bool:
    """Vérifie si les binaires libvlc et libvlccore sont présents dans le dossier local."""
    vlc_dir = get_local_vlc_dir()
    return (vlc_dir / "libvlc.dll").is_file() and (vlc_dir / "libvlccore.dll").is_file()


def setup_vlc_environment() -> Path | None:
    """Configure les variables d'environnement Windows pour que python-vlc trouve les DLL locales.

    Vérifie en priorité :
    1. Dossier ./vlc à côté de l'exécutable
    2. Dossier %APPDATA%/AMSO/vlc
    """
    setup_macos_user_vlc()
    candidates = [
        Path(sys.executable).parent / "vlc",
        Path(__file__).parents[2] / "vlc",
        get_local_vlc_dir(),
    ]

    for candidate in candidates:
        if (candidate / "libvlc.dll").is_file() and (candidate / "libvlccore.dll").is_file():
            # Ajout au PATH et enregistrement auprès du chargeur de DLL Windows (Python 3.8+)
            c_str = str(candidate.resolve())
            if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
                try:
                    os.add_dll_directory(c_str)
                except Exception as exc:
                    logger.debug("add_dll_directory exception : %s", exc)

            os.environ["PATH"] = f"{c_str};{os.environ.get('PATH', '')}"
            os.environ["PYTHON_VLC_LIB_PATH"] = str((candidate / "libvlc.dll").resolve())
            os.environ["PYTHON_VLC_MODULE_PATH"] = str((candidate / "plugins").resolve())
            return candidate

    return None


class VlcDownloadWorker(QThread):
    """Thread de téléchargement et d'extraction des composants VLC avec rapport de progression."""

    # Signaux
    progress = Signal(int, str)  # pourcentage (0-100), message descriptif
    finished = Signal(bool, str)  # succès (True/False), message final ou erreur

    def __init__(self, dest_dir: Path | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.dest_dir = dest_dir or get_local_vlc_dir()
        self._is_cancelled = False

    def cancel(self) -> None:
        """Annule le téléchargement en cours."""
        self._is_cancelled = True

    def run(self) -> None:
        temp_zip_file: Path | None = None
        try:
            self.progress.emit(0, "Connexion aux serveurs VideoLAN...")

            # 1. Téléchargement du ZIP dans un fichier temporaire
            temp_fd, temp_path_str = tempfile.mkstemp(suffix="_vlc.zip", prefix="amso_")
            os.close(temp_fd)
            temp_zip_file = Path(temp_path_str)

            download_success = False
            last_error = ""

            for url in VLC_ZIP_URLS:
                if self._is_cancelled:
                    self.finished.emit(False, tr("vlc_download.cancelled_by_user"))
                    return

                try:
                    self.progress.emit(5, tr("vlc_download.from_host", host=url.split("/")[2]))
                    req = urllib.request.Request(url, headers={"User-Agent": "AMSO/1.0 (Windows)"})
                    with urllib.request.urlopen(req, timeout=25) as response:
                        total_bytes = int(response.headers.get("Content-Length", 75 * 1024 * 1024))
                        downloaded_bytes = 0
                        chunk_size = 64 * 1024  # 64 Ko par paquet

                        with open(temp_zip_file, "wb") as f_out:
                            while True:
                                if self._is_cancelled:
                                    self.finished.emit(False, tr("vlc_download.cancelled"))
                                    return
                                chunk = response.read(chunk_size)
                                if not chunk:
                                    break
                                f_out.write(chunk)
                                downloaded_bytes += len(chunk)

                                percent = int(5 + (downloaded_bytes / total_bytes) * 75)
                                mb_done = downloaded_bytes / (1024 * 1024)
                                mb_total = total_bytes / (1024 * 1024)
                                msg = tr(
                                    "vlc_download.progress",
                                    done=f"{mb_done:.1f}",
                                    total=f"{mb_total:.1f}",
                                    percent=percent,
                                )
                                self.progress.emit(min(80, percent), msg)

                    download_success = True
                    break
                except Exception as err:
                    last_error = str(err)
                    logger.warning("Échec du miroir %s : %s", url, err)
                    continue

            if not download_success:
                self.finished.emit(False, tr("vlc_download.failed", error=last_error))
                return

            # 2. Décompression ciblée (uniquement libvlc, libvlccore et plugins/)
            self.progress.emit(82, tr("vlc_download.extracting"))
            self.dest_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(temp_zip_file, "r") as zf:
                members = zf.infolist()
                total_files = len(members)

                for idx, member in enumerate(members):
                    if self._is_cancelled:
                        self.finished.emit(False, tr("vlc_download.install_cancelled"))
                        return

                    filename = member.filename.replace("\\", "/")
                    parts = filename.split("/")

                    # Extraction de libvlc.dll
                    if "libvlc.dll" in parts:
                        target = self.dest_dir / "libvlc.dll"
                        target.write_bytes(zf.read(member))
                    # Extraction de libvlccore.dll
                    elif "libvlccore.dll" in parts:
                        target = self.dest_dir / "libvlccore.dll"
                        target.write_bytes(zf.read(member))
                    # Extraction des plugins
                    elif "plugins" in parts:
                        p_idx = parts.index("plugins")
                        rel_parts = parts[p_idx:]
                        if not member.is_dir():
                            target = self.dest_dir.joinpath(*rel_parts)
                            target.parent.mkdir(parents=True, exist_ok=True)
                            target.write_bytes(zf.read(member))

                    if idx % 100 == 0:
                        progress_pct = int(82 + (idx / max(1, total_files)) * 17)
                        self.progress.emit(min(99, progress_pct), tr("vlc_download.installing"))

            # 3. Finalisation et vérification
            if (self.dest_dir / "libvlc.dll").is_file() and (self.dest_dir / "libvlccore.dll").is_file():
                setup_vlc_environment()
                self.progress.emit(100, tr("vlc_download.engine_ready"))
                self.finished.emit(True, tr("vlc_download.done"))
            else:
                self.finished.emit(False, tr("vlc_download.dll_missing"))

        except Exception as exc:
            logger.error("Erreur durant l'installation automatique de VLC : %s", exc)
            self.finished.emit(False, str(exc))
        finally:
            # Nettoyage du fichier ZIP temporaire
            if temp_zip_file and temp_zip_file.exists():
                try:
                    temp_zip_file.unlink()
                except OSError:
                    pass
