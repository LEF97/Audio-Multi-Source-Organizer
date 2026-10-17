"""Boîte de dialogue de confirmation pour la suppression d'un morceau.

Permet de choisir entre retirer le morceau de la bibliothèque (avec exclusion des futurs scans)
ou mettre également le fichier physique à la corbeille système Windows.
"""

from __future__ import annotations

import logging
import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from amso.core.database import TrackRecord
from amso.core.i18n import tr
from amso.ui.theme import DARK_THEME_QSS

logger = logging.getLogger(__name__)


def send_file_to_trash(path: str) -> bool:
    """Déplace un fichier vers la corbeille système Windows (avec possibilité de restauration par l'utilisateur).

    En cas de système non-Windows ou d'impossibilité d'accès à l'API Shell, supprime le fichier de manière sécurisée.
    """
    if not path or not os.path.exists(path):
        return False

    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            class SHFILEOPSTRUCTW(ctypes.Structure):
                _fields_ = [
                    ("hwnd", wintypes.HWND),
                    ("wFunc", wintypes.UINT),
                    ("pFrom", wintypes.LPCWSTR),
                    ("pTo", wintypes.LPCWSTR),
                    ("fFlags", wintypes.WORD),
                    ("fAnyOperationsAborted", wintypes.BOOL),
                    ("hNameMappings", wintypes.LPVOID),
                    ("lpszProgressTitle", wintypes.LPCWSTR),
                ]

            FO_DELETE = 0x0003
            FOF_ALLOWUNDO = 0x0040
            FOF_NOCONFIRMATION = 0x0010
            FOF_SILENT = 0x0004

            # L'API Win32 SHFileOperationW attend une chaîne doublement terminée par zéro (\0\0)
            abs_path = os.path.abspath(path) + "\0\0"
            fileop = SHFILEOPSTRUCTW()
            fileop.hwnd = None
            fileop.wFunc = FO_DELETE
            fileop.pFrom = abs_path
            fileop.pTo = None
            fileop.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT

            res = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(fileop))
            if res == 0 and not fileop.fAnyOperationsAborted:
                logger.info("Fichier déplacé vers la corbeille Windows : %s", path)
                return True
        except Exception as e:
            logger.warning("Erreur SHFileOperation vers la corbeille : %s", e)

    # Repli
    try:
        os.remove(path)
        logger.info("Fichier supprimé du disque : %s", path)
        return True
    except Exception as e:
        logger.error("Impossible de supprimer le fichier %s : %s", path, e)
        return False


class DeleteTrackDialog(QDialog):
    """Dialogue modal proposant les deux modes de suppression d'un morceau."""

    def __init__(self, track: TrackRecord, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.track = track
        self._action: str | None = None  # "ignore", "trash", ou None

        self.setWindowTitle(tr("dialog.delete_confirm_title"))
        self.setMinimumWidth(540)
        self.setModal(True)
        self.setStyleSheet(DARK_THEME_QSS)

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # En-tête avec icône
        header = QHBoxLayout()
        header.setSpacing(16)
        header.setAlignment(Qt.AlignmentFlag.AlignTop)

        icon_lbl = QLabel("🗑️")
        icon_lbl.setStyleSheet("""
            font-size: 32px;
            padding: 10px;
            background-color: #1A1D24;
            border: 1px solid #282C37;
            border-radius: 12px;
        """)
        header.addWidget(icon_lbl)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        title_lbl = QLabel(tr("dialog.delete_confirm_title"))
        title_lbl.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: 700;")
        text_layout.addWidget(title_lbl)

        track_title = self.track.title or self.track.file_name or tr("track.untitled")
        artist = self.track.artist or tr("track.unknown_artist")
        track_info = QLabel(f"<b>{track_title}</b> — <span style='color: #94A3B8;'>{artist}</span>")
        track_info.setTextFormat(Qt.TextFormat.RichText)
        track_info.setStyleSheet("color: #38BDF8; font-size: 13px;")
        text_layout.addWidget(track_info)

        path_str = self.track.source_path or self.track.source_ref
        if path_str:
            path_lbl = QLabel(f"📁 {path_str}")
            path_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
            path_lbl.setWordWrap(True)
            text_layout.addWidget(path_lbl)

        header.addLayout(text_layout, 1)
        layout.addLayout(header)

        # Question d'action
        prompt_lbl = QLabel(tr("dialog.delete_track_prompt"))
        prompt_lbl.setStyleSheet("color: #E2E8F0; font-size: 13px; font-weight: 600; margin-top: 6px;")
        layout.addWidget(prompt_lbl)

        # Cadre d'options
        options_frame = QFrame()
        options_frame.setStyleSheet("""
            QFrame {
                background-color: #161920;
                border: 1px solid #282C37;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        options_layout = QVBoxLayout(options_frame)
        options_layout.setSpacing(12)

        # Option 1 : Retirer de la bibliothèque (et ignorer)
        btn_ignore = QPushButton(tr("dialog.delete_option_ignore"))
        btn_ignore.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ignore.setStyleSheet("""
            QPushButton {
                background-color: #1E2430;
                color: #F8FAFC;
                border: 1px solid #38BDF8;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
                font-weight: 600;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #0284C7;
                color: #FFFFFF;
            }
        """)
        btn_ignore.clicked.connect(self._on_choose_ignore)
        options_layout.addWidget(btn_ignore)

        desc_ignore = QLabel(tr("dialog.delete_option_ignore_desc"))
        desc_ignore.setWordWrap(True)
        desc_ignore.setStyleSheet("color: #94A3B8; font-size: 11px; margin-left: 6px; margin-bottom: 4px;")
        options_layout.addWidget(desc_ignore)

        # Option 2 : Mettre à la corbeille Windows
        btn_trash = QPushButton(tr("dialog.delete_option_trash"))
        btn_trash.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_trash.setStyleSheet("""
            QPushButton {
                background-color: #1E2430;
                color: #F87171;
                border: 1px solid #EF4444;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
                font-weight: 600;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #DC2626;
                color: #FFFFFF;
            }
        """)
        btn_trash.clicked.connect(self._on_choose_trash)
        options_layout.addWidget(btn_trash)

        desc_trash = QLabel(tr("dialog.delete_option_trash_desc"))
        desc_trash.setWordWrap(True)
        desc_trash.setStyleSheet("color: #94A3B8; font-size: 11px; margin-left: 6px;")
        options_layout.addWidget(desc_trash)

        layout.addWidget(options_frame)

        # Bouton Annuler en bas
        bottom_box = QHBoxLayout()
        bottom_box.addStretch()

        btn_cancel = QPushButton(tr("dialog.delete_btn_cancel"))
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #20242D;
                color: #94A3B8;
                border: 1px solid #333846;
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2A303C;
                color: #F8FAFC;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        bottom_box.addWidget(btn_cancel)

        layout.addLayout(bottom_box)

    def _on_choose_ignore(self) -> None:
        self._action = "ignore"
        self.accept()

    def _on_choose_trash(self) -> None:
        self._action = "trash"
        self.accept()

    @property
    def action(self) -> str | None:
        """Retourne l'action sélectionnée ('ignore', 'trash', ou None si annulé)."""
        return self._action
