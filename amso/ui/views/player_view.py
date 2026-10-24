"""Vue plein écran du Lecteur Audio pour AMSO."""

from __future__ import annotations

import os

from PySide6.QtCore import QFileSystemWatcher, Qt, QTimer, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget

from amso.core.database import TrackRecord
from amso.core.i18n import tr
from amso.services.player_service import PlayerService
from amso.ui.models import format_duration
from amso.ui.views.cover_helper import (
    get_default_cover_pixmap,
    invalidate_cover_cache,
    load_cover_async,
)
from amso.ui.views.player_ui_builder import PlayerUiMixin
from amso.ui.widgets.transport_mixin import TransportViewMixin


class PlayerView(PlayerUiMixin, TransportViewMixin, QWidget):
    """Page dédiée au Lecteur Audio grand format avec jaquette et contrôles complets."""

    effect_changed = Signal(str)
    add_folder_requested = Signal()

    def __init__(self, player_service: PlayerService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.player = player_service
        self._has_sources: bool = True

        self._setup_ui()
        self._connect_signals()

        # Surveillance dynamique du dossier pour recharger la pochette si folder.png change
        self._folder_watcher = QFileSystemWatcher(self)
        self._folder_watcher.directoryChanged.connect(self._on_current_folder_changed)
        self._folder_watch_timer = QTimer(self)
        self._folder_watch_timer.setSingleShot(True)
        self._folder_watch_timer.setInterval(300)
        self._folder_watch_timer.timeout.connect(self._on_folder_change_debounced)

        # État initial
        self.update_track_info(self.player.current_track)
        self.update_playback_state("playing" if self.player.is_playing else "stopped")

    def _connect_signals(self) -> None:
        # Signaux du PlayerService et contrôles de transport (partagés)
        self._connect_transport_signals()

        # Synchronisation de l'état initial
        self.update_shuffle_ui(self.player.is_shuffle)
        self.update_repeat_ui(self.player.repeat_mode)
        self.update_volume(self.player.volume, self.player.is_muted)
        if self.player.current_track:
            self.update_track_info(self.player.current_track)

    def _on_cover_loaded(self, path: str, pixmap: QPixmap) -> None:
        """Appelé dès que la pochette asynchrone a fini de charger."""
        if getattr(self, "_displayed_track_path", None) == path:
            self._current_pixmap = pixmap
            self._update_scaled_cover()

    def _on_current_folder_changed(self, path: str) -> None:
        """Appelé dès qu'un fichier (ex: folder.png) est ajouté ou modifié dans le dossier courant."""
        if hasattr(self, "_folder_watch_timer"):
            self._folder_watch_timer.start()

    def _on_folder_change_debounced(self) -> None:
        """Recharge la pochette du morceau en cours après modification du dossier."""
        if self.player.current_track:
            invalidate_cover_cache(self.player.current_track)
            load_cover_async(
                self.player.current_track,
                size=320,
                radius=12,
                callback=self._on_cover_loaded,
                force_check=True,
            )

    def _update_scaled_cover(self) -> None:
        """Applique l'image actuelle à la taille exacte du lbl_cover avec anticrénelage fluide."""
        pixmap = getattr(self, "_current_pixmap", None)
        size = self.lbl_cover.width()
        if not pixmap or pixmap.isNull():
            pixmap = get_default_cover_pixmap(size, radius=12)
            self._current_pixmap = pixmap
            self.lbl_cover.setPixmap(pixmap)
            return

        if pixmap.width() != size or pixmap.height() != size:
            scaled = pixmap.scaled(
                size,
                size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.lbl_cover.setPixmap(scaled)
        else:
            self.lbl_cover.setPixmap(pixmap)

    def _adjust_layout(self) -> None:
        """Ajuste dynamiquement la hauteur de la pochette et décale les blocs verticaux
        pour garantir un affichage intégral (titre et auteur multi-lignes, commandes,
        curseur de volume) sans coupure ni défilement superflu."""
        if not hasattr(self, "scroll_area") or not hasattr(self, "card"):
            return
        if not getattr(self, "_has_sources", True):
            return

        viewport_h = self.scroll_area.viewport().height()
        if viewport_h <= 100:
            top_h = self.top_bar.height() if hasattr(self, "top_bar") and self.top_bar.height() > 0 else 44
            viewport_h = max(300, self.height() - top_h)

        c_margins = self.center_layout.contentsMargins()
        net_available = viewport_h - c_margins.top() - c_margins.bottom()

        # Hauteur requise pour les composants de la carte hors pochette
        card_hint = self.card.sizeHint().height()
        current_cover_h = self.lbl_cover.height()
        non_cover_h = max(130, card_hint - current_cover_h)

        # Taille idéale de la pochette carrée
        target_size = net_available - non_cover_h - 4
        # Borner entre une taille minimale lisible (150px) et maximale (320px)
        target_size = max(150, min(320, target_size))

        if target_size != self.lbl_cover.width():
            self.lbl_cover.setFixedSize(target_size, target_size)
            self._update_scaled_cover()

    def update_track_info(self, track: TrackRecord | None) -> None:
        """Met à jour l'affichage avec la piste en cours de lecture de façon instantanée et non-bloquante."""
        track_path = (track.source_path or track.source_ref or track.folder_path or "") if track else ""
        self._displayed_track_path = track_path

        # Mise à jour de la surveillance du dossier contenant la piste
        if hasattr(self, "_folder_watcher"):
            existing = self._folder_watcher.directories()
            if existing:
                self._folder_watcher.removePaths(existing)

            folder_to_watch: str | None = None
            if track:
                if track.folder_path and os.path.isdir(track.folder_path):
                    folder_to_watch = track.folder_path
                elif track.source_path:
                    parent_dir = os.path.dirname(track.source_path)
                    if os.path.isdir(parent_dir):
                        folder_to_watch = parent_dir
            if folder_to_watch:
                self._folder_watcher.addPath(folder_to_watch)

        if hasattr(self, "effect_canvas") and self.effect_canvas:
            self.effect_canvas.set_track(track)

        # Chargement immédiat (en cache) ou asynchrone (défaut puis cover) sans bloquer
        pixmap = load_cover_async(track, size=320, radius=12, callback=self._on_cover_loaded, force_check=True)
        self._current_pixmap = pixmap

        if not track:
            self.lbl_title.setText(tr("player.no_track"))
            self.lbl_title.setToolTip("")
            self.lbl_artist_album.setText("")
            self.lbl_artist_album.setToolTip("")
            self.lbl_file_name.setText("")
            self.lbl_file_name.setToolTip("")
            self.lbl_file_name.setVisible(False)
            self.lbl_badge.setVisible(False)
            self.lbl_time_cur.setText("00:00")
            self.lbl_time_total.setText("00:00")
            self.slider_seek.setValue(0)
            self._adjust_layout()
            self._update_scaled_cover()
            return

        title_text = track.title or track.file_name or tr("track.untitled")
        self.lbl_title.setText(title_text)
        self.lbl_title.setToolTip(title_text)

        artist_part = track.artist or tr("track.unknown_artist")
        album_part = f" — {track.album}" if track.album else ""
        sub_text = f"{artist_part}{album_part}"
        self.lbl_artist_album.setText(sub_text)
        self.lbl_artist_album.setToolTip(sub_text)

        # Nom du fichier (entre auteur/album et le badge de format)
        file_name_text = track.file_name or (
            os.path.basename(track.source_path.replace("\\", "/")) if track.source_path else ""
        )
        if file_name_text:
            self.lbl_file_name.setText(file_name_text)
            self.lbl_file_name.setToolTip(file_name_text)
            self.lbl_file_name.setVisible(True)
        else:
            self.lbl_file_name.setText("")
            self.lbl_file_name.setToolTip("")
            self.lbl_file_name.setVisible(False)

        # Badge de format
        details = []
        if track.format:
            details.append(track.format.upper())
        if track.bitrate:
            details.append(f"{track.bitrate} kbps")
        if track.sample_rate:
            details.append(f"{track.sample_rate / 1000:.1f} kHz")

        if details:
            self.lbl_badge.setText(" • ".join(details))
            self.lbl_badge.setVisible(True)
        else:
            self.lbl_badge.setVisible(False)

        total_sec = track.duration_seconds or 0
        self.lbl_time_total.setText(format_duration(total_sec))

        # Recalcul de l'ajustement vertical pour s'adapter aux textes (titre/auteur sur plusieurs lignes)
        self._adjust_layout()
        self._update_scaled_cover()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._adjust_layout()
        if hasattr(self, "effect_canvas"):
            self.effect_canvas.showEvent(event)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._adjust_layout()

    def hideEvent(self, event) -> None:
        super().hideEvent(event)
        if hasattr(self, "effect_canvas"):
            self.effect_canvas.hideEvent(event)

    def update_playback_state(self, state: str) -> None:
        """Met à jour l'animation puis l'icône Play/Pause."""
        if hasattr(self, "effect_canvas"):
            self.effect_canvas.set_playback_state(state)
        super().update_playback_state(state)

    def update_position(self, current_ms: int, total_ms: int, ratio: float) -> None:
        """Met à jour la position courante, la barre de progression et l'animation."""
        super().update_position(current_ms, total_ms, ratio)
        if hasattr(self, "effect_canvas") and self.effect_canvas:
            self.effect_canvas.update_audio_time(current_ms, ratio)

    def update_volume(self, volume: int, is_muted: bool) -> None:
        """Met à jour le volume, le libellé et l'animation."""
        super().update_volume(volume, is_muted)
        if hasattr(self, "effect_canvas") and self.effect_canvas:
            self.effect_canvas.update_audio_volume(volume, is_muted)
        if is_muted or volume == 0:
            self.lbl_volume.setText(tr("player.btn_mute"))
        else:
            self.lbl_volume.setText(f"{volume}%")

    def _on_add_folder_clicked(self) -> None:
        """Déclenché par le bouton de premier accueil dans la carte du lecteur."""
        self.add_folder_requested.emit()

    def set_has_sources(self, has_sources: bool) -> None:
        """Bascule entre la vue lecteur standard et l'état d'accueil incitatif."""
        self._has_sources = has_sources
        show_empty = not has_sources
        if hasattr(self, "empty_container"):
            self.empty_container.setVisible(show_empty)
        if hasattr(self, "lbl_cover"):
            self.lbl_cover.setVisible(not show_empty)
        if hasattr(self, "info_container"):
            self.info_container.setVisible(not show_empty)
        if hasattr(self, "seek_container"):
            self.seek_container.setVisible(not show_empty)
        if hasattr(self, "ctrl_container"):
            self.ctrl_container.setVisible(not show_empty)
        self._adjust_layout()

    def retranslate_ui(self) -> None:
        """Met à jour l'ensemble des textes et infobulles du lecteur selon la langue active."""
        self.lbl_page_title.setText(tr("player.title"))
        if hasattr(self, "lbl_effect_badge"):
            self.lbl_effect_badge.setText(tr("player.visual_effect"))
        if hasattr(self, "combo_effect"):
            self._populate_effects_combo()

        if hasattr(self, "lbl_empty_title"):
            self.lbl_empty_title.setText(tr("player.empty_title"))
        if hasattr(self, "lbl_empty_desc"):
            self.lbl_empty_desc.setText(tr("player.empty_desc"))
        if hasattr(self, "btn_add_first_folder"):
            self.btn_add_first_folder.setText(tr("player.btn_add_first_folder"))

        if not self.player.current_track:
            self.lbl_title.setText(tr("player.no_track"))
        else:
            self.update_track_info(self.player.current_track)

        self.btn_shuffle.setToolTip(tr("player.btn_shuffle"))
        self.btn_prev.setToolTip(tr("player.btn_previous"))
        if self.player.is_playing:
            self.btn_play_pause.setToolTip(tr("player.btn_pause"))
        else:
            self.btn_play_pause.setToolTip(tr("player.btn_play"))
        self.btn_stop.setToolTip(tr("player.btn_stop"))
        self.btn_next.setToolTip(tr("player.btn_next"))
        self.btn_repeat.setToolTip(tr("player.btn_repeat"))
        if self.player.is_muted or self.player.volume == 0:
            self.lbl_volume.setText(tr("player.btn_mute"))
