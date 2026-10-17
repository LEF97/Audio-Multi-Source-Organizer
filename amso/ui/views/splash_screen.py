"""Écran de chargement (Splash Screen) moderne au démarrage d'AMSO.

Affiche un visuel soigné, sombre et épuré avec barre de progression
et statut des étapes d'initialisation (BDD, audio, interface).
"""

from __future__ import annotations

import os

from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QColor, QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from amso import __version__


class SplashScreen(QWidget):
    """Fenêtre sans bordure affichant l'avancement de l'initialisation."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._current_value: int = 0

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SplashScreen
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.setFixedSize(540, 310)

        from amso.ui.theme import get_app_icon

        self.setWindowIcon(get_app_icon())

        self._setup_ui()
        self._center_on_screen()

    def _setup_ui(self) -> None:
        from amso.ui.theme import get_app_logo_pixmap

        # Layout racine
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(15, 15, 15, 15)

        # Cadre conteneur sombre avec coins arrondis et ombre
        self.card = QFrame(self)
        self.card.setObjectName("splashCard")
        self.card.setStyleSheet("""
            QFrame#splashCard {
                background-color: #121418;
                border: 1px solid #282C37;
                border-radius: 16px;
            }
        """)

        # Ombre portée douce
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 10)
        self.card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(36, 32, 36, 28)
        card_layout.setSpacing(8)

        # En-tête : Logo officiel + Titre + Sous-titre
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        app_pm = get_app_logo_pixmap()
        if not app_pm.isNull():
            lbl_icon = QLabel()
            lbl_icon.setPixmap(
                app_pm.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            )
            lbl_icon.setStyleSheet("background: transparent;")
            header_layout.addWidget(lbl_icon)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        lbl_logo = QLabel("AMSO" if not app_pm.isNull() else "🎵  AMSO")
        lbl_logo.setStyleSheet("""
            color: #F8FAFC;
            font-size: 28px;
            font-weight: 800;
            letter-spacing: 1.5px;
        """)
        title_box.addWidget(lbl_logo)

        lbl_subtitle = QLabel("Audio Multi-Source Organizer")
        lbl_subtitle.setStyleSheet("""
            color: #38BDF8;
            font-size: 13px;
            font-weight: 600;
            margin-top: 2px;
        """)
        title_box.addWidget(lbl_subtitle)

        header_layout.addLayout(title_box)
        header_layout.addStretch()

        card_layout.addLayout(header_layout)

        # Ligne d'accentuation subtile
        accent_line = QFrame()
        accent_line.setFixedHeight(2)
        accent_line.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0284C7, stop:0.7 #38BDF8, stop:1 transparent);
            border-radius: 1px;
            margin-top: 10px;
            margin-bottom: 14px;
        """)
        card_layout.addWidget(accent_line)

        card_layout.addStretch()

        # Statut textuel & Pourcentage
        status_box = QHBoxLayout()
        status_box.setContentsMargins(0, 0, 0, 4)

        self.lbl_status = QLabel("Démarrage de l'application...")
        self.lbl_status.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 500;")
        status_box.addWidget(self.lbl_status)

        status_box.addStretch()

        self.lbl_percent = QLabel("0%")
        self.lbl_percent.setStyleSheet("color: #38BDF8; font-size: 12px; font-weight: 700;")
        status_box.addWidget(self.lbl_percent)

        card_layout.addLayout(status_box)

        # Barre de progression personnalisée
        self.progress_bar = QProgressBar(self.card)
        self.progress_bar.setObjectName("splashProgressBar")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet("""
            QProgressBar#splashProgressBar {
                background-color: #1E2430;
                border: none;
                border-radius: 4px;
                max-width: 5000px;
                min-width: 0px;
                height: 8px;
            }
            QProgressBar#splashProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0284C7, stop:1 #38BDF8);
                border-radius: 4px;
            }
        """)
        card_layout.addWidget(self.progress_bar)

        card_layout.addSpacing(16)

        # Pied de page (version uniquement)
        footer_box = QHBoxLayout()
        footer_box.setContentsMargins(0, 0, 0, 0)

        lbl_version = QLabel(f"v{__version__}")
        lbl_version.setStyleSheet("color: #475569; font-size: 11px; font-weight: 500;")
        footer_box.addWidget(lbl_version)

        footer_box.addStretch()

        card_layout.addLayout(footer_box)

        root_layout.addWidget(self.card)

    def _center_on_screen(self) -> None:
        """Centre la fenêtre splash sur l'écran principal."""
        screen = QGuiApplication.primaryScreen()
        if screen:
            geom = screen.availableGeometry()
            x = geom.x() + (geom.width() - self.width()) // 2
            y = geom.y() + (geom.height() - self.height()) // 2
            self.move(x, y)

    def set_progress(self, value: int, message: str, step_delay_ms: int = 10) -> None:
        """Met à jour le pourcentage de manière fluide pas-à-pas (1% en 1%) et rafraîchit l'affichage en continu."""
        target = max(self._current_value, min(100, value))
        self.lbl_status.setText(message)

        # En environnement sans affichage (CI / tests) ou sans délai, mise à jour immédiate
        if os.environ.get("QT_QPA_PLATFORM") == "offscreen" or step_delay_ms <= 0:
            self._current_value = target
            self.progress_bar.setValue(target)
            self.lbl_percent.setText(f"{target}%")
            QApplication.processEvents()
            return

        if target <= self._current_value:
            return

        # Progression fluide continue pas à pas de 1% en 1%
        for v in range(self._current_value + 1, target + 1):
            if not self.isVisible():
                break
            self.progress_bar.setValue(v)
            self.lbl_percent.setText(f"{v}%")
            QApplication.processEvents()
            if step_delay_ms > 0:
                QThread.msleep(step_delay_ms)

        self._current_value = target

    def finish(self, main_window: QWidget) -> None:
        """Ferme l'écran de chargement et active la fenêtre principale."""
        main_window.activateWindow()
        main_window.raise_()
        self.close()
