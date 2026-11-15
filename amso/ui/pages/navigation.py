"""Navigation entre les pages et changement de page courante (mixin de MainWindow)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QAbstractItemView,
    QMainWindow,
)

from amso.core.i18n import tr

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    _MixinBase = QMainWindow
else:
    _MixinBase = object


class NavigationMixin(_MixinBase):
    """Navigation entre les pages et changement de page courante (mixin de MainWindow)."""

    if TYPE_CHECKING:
        # Les attributs/méthodes de MainWindow sont résolus dynamiquement (typage uniquement)
        def __getattr__(self, name: str) -> Any: ...

    def _switch_to_page(self, page_name: str, target: Any) -> None:
        """Bascule vers la page cible en sécurisant l'arrêt des modes exclusifs (ex: Blind Test)."""
        if getattr(self, "_current_active_page", None) == "blind_test" and page_name != "blind_test":
            if hasattr(self, "player_service") and self.player_service:
                self.player_service.pause()
                if hasattr(self.player_service, "_reset_standby_player"):
                    self.player_service._reset_standby_player()
        self._current_active_page = page_name
        if isinstance(target, int):
            self.stacked_widget.setCurrentIndex(target)
        else:
            self.stacked_widget.setCurrentWidget(target)

    def _on_player_nav_clicked(self) -> None:
        """Active la page du grand Lecteur audio."""
        if not self.player_service.is_vlc_available:
            self._ensure_vlc_available()
        self._switch_to_page("player", self.page_player)

    def _on_blind_test_nav_clicked(self) -> None:
        """Active la page du mode Blind Test."""
        if not self.player_service.is_vlc_available:
            self._ensure_vlc_available()
        self._switch_to_page("blind_test", self.page_blind_test)

    def _on_playlist_nav_clicked(self) -> None:
        """Active la page de la Liste de lecture (Playlist)."""
        if not self.player_service.is_vlc_available:
            self._ensure_vlc_available()
        self._switch_to_page("playlist", self.page_playlist)

    def _on_all_tracks_clicked(self) -> None:
        self._switch_to_page("tracks", 0)
        if hasattr(self, "tracks_top_bar"):
            self.tracks_top_bar.setVisible(True)
        if hasattr(self, "tracks_stack"):
            self.tracks_stack.setCurrentWidget(self.table_view)
        self.table_model.set_filter(source_id=None, source_type=None, search_query=self.search_edit.text())
        self._tracks_dirty = False
        self._update_track_count()

    def _on_by_folder_clicked(self) -> None:
        """Active la page d'exploration par dossiers."""
        self._switch_to_page("folders", self.page_folders)
        if self.folder_tree.topLevelItemCount() == 0 or getattr(self, "_folders_dirty", False):
            self._refresh_folders_tree()
            self.folder_table_model.reload_data()
            self._folders_dirty = False
        if getattr(self, "_pending_restore_scroll", False):
            self._pending_restore_scroll = False
            cur_item = self.folder_tree.currentItem()
            if cur_item is not None:
                self.folder_tree.scrollToItem(cur_item, QAbstractItemView.ScrollHint.PositionAtCenter)
                QTimer.singleShot(
                    0,
                    lambda: (
                        self.folder_tree.currentItem() is not None
                        and self.folder_tree.scrollToItem(
                            self.folder_tree.currentItem(),
                            QAbstractItemView.ScrollHint.PositionAtCenter,
                        )
                    ),
                )
            if hasattr(self, "scroll_folder_table_to_current_track"):
                self.scroll_folder_table_to_current_track()
                QTimer.singleShot(60, self.scroll_folder_table_to_current_track)

    def _on_duplicates_clicked(self) -> None:
        """Affiche les morceaux en doublon détectés dans la liste de lecture active."""
        self._switch_to_page("duplicates", 0)
        playlist = list(self.player_service.playlist) if hasattr(self, "player_service") and self.player_service else []
        if not playlist:
            self.table_model.set_tracks([])
            if hasattr(self, "tracks_top_bar"):
                self.tracks_top_bar.setVisible(False)
            self._update_track_count()
            if hasattr(self, "tracks_stack") and hasattr(self, "tracks_empty_widget"):
                self.tracks_stack.setCurrentWidget(self.tracks_empty_widget)
            self.status_label.setText(tr("duplicates.empty_playlist_message"))
            return

        if hasattr(self, "tracks_top_bar"):
            self.tracks_top_bar.setVisible(True)
        if hasattr(self, "tracks_stack"):
            self.tracks_stack.setCurrentWidget(self.table_view)

        dup_hash, dup_meta, all_dup_tracks = self.db.find_duplicates_in_tracks(playlist)
        self.table_model.set_tracks(all_dup_tracks)
        self._update_track_count()
        self.status_label.setText(
            tr(
                "status.duplicates_summary",
                hash_count=len(dup_hash),
                meta_count=len(dup_meta),
            )
        )

    def _on_settings_general_clicked(self) -> None:
        """Bascule sur la page des Paramètres Généraux."""
        self._switch_to_page("settings_general", self.page_settings)

    def _on_library_sources_clicked(self) -> None:
        """Bascule sur la page Gestion de la bibliothèque > Sources."""
        self._switch_to_page("library_sources", self.page_library_sources)
        if getattr(self, "_sources_dirty", False) or not hasattr(self, "tree_library_sources"):
            self._refresh_library_sources_tree()
            self._sources_dirty = False
        elif self.tree_library_sources.topLevelItemCount() == 0:
            self._refresh_library_sources_tree()

    def _on_settings_player_clicked(self) -> None:
        """Bascule sur la page Paramètres > Lecteur."""
        self._switch_to_page("settings_player", self.page_settings_player)

    def _on_current_page_changed(self, index: int) -> None:
        """Appelé lors du basculement d'onglet pour adapter l'inhibition de veille de l'écran et la page active."""
        prev_page = getattr(self, "_current_active_page", None)
        self._update_sleep_inhibition()
        if hasattr(self, "stacked_widget"):
            curr_widget = self.stacked_widget.currentWidget()
            if prev_page == "blind_test" and curr_widget != getattr(self, "page_blind_test", None):
                if hasattr(self, "player_service") and self.player_service and self.player_service.is_playing:
                    self.player_service.pause()
                    if hasattr(self.player_service, "_reset_standby_player"):
                        self.player_service._reset_standby_player()
            if curr_widget == getattr(self, "page_player", None):
                self._current_active_page = "player"
            elif curr_widget == getattr(self, "page_blind_test", None):
                self._current_active_page = "blind_test"
            elif curr_widget == getattr(self, "page_playlist", None):
                self._current_active_page = "playlist"
            elif curr_widget == getattr(self, "page_folders", None):
                self._current_active_page = "folders"
            elif curr_widget == getattr(self, "page_settings", None):
                self._current_active_page = "settings_general"
            elif curr_widget == getattr(self, "page_library_sources", None):
                self._current_active_page = "library_sources"
            elif curr_widget == getattr(self, "page_settings_player", None):
                self._current_active_page = "settings_player"
            elif curr_widget == getattr(self, "page_logs", None):
                self._current_active_page = "logs"
            elif curr_widget == getattr(self, "page_settings_about", None):
                self._current_active_page = "settings_about"
            elif curr_widget == getattr(self, "page_tracks", None):
                if getattr(self, "_current_active_page", None) != "duplicates":
                    self._current_active_page = "tracks"

    def _on_settings_logs_clicked(self) -> None:
        """Bascule sur la page Paramètres > Logs."""
        self._switch_to_page("logs", self.page_logs)
        self.page_logs.refresh_if_dirty()

    def show_logs_page(self) -> None:
        """Sélectionne le bouton de navigation Logs et ouvre la page Paramètres > Logs."""
        if hasattr(self, "drawer_settings"):
            self.drawer_settings.set_expanded(True)
        if hasattr(self, "btn_settings_logs"):
            self.btn_settings_logs.setChecked(True)
        self._on_settings_logs_clicked()

    def _on_settings_about_clicked(self) -> None:
        """Bascule sur la page Paramètres > À propos."""
        self._switch_to_page("settings_about", self.page_settings_about)
        if hasattr(self, "drawer_settings"):
            self.drawer_settings.set_expanded(True)
        if hasattr(self, "btn_settings_about"):
            self.btn_settings_about.setChecked(True)

    def show_about_page(self) -> None:
        """Sélectionne le bouton de navigation À propos et ouvre la page Paramètres > À propos."""
        self._on_settings_about_clicked()
