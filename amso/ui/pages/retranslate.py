"""Traduction dynamique de l'interface (mixin de MainWindow)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
)

from amso import __version__
from amso.core.config import get_config_path
from amso.core.i18n import tr
from amso.ui.pages.vlc_status import build_vlc_status
from amso.ui.widgets.help_guide_popup import HelpButton

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    _MixinBase = QMainWindow
else:
    _MixinBase = object

# (attribut, clé i18n, préfixe) : les widgets absents sont ignorés, certaines pages ou menus étant optionnels.
_TEXTS: tuple[tuple[str, str, str], ...] = (
    # Barre latérale
    ("btn_player", "sidebar.nav_player", ""),
    ("btn_blind_test", "sidebar.nav_blind_test", ""),
    ("btn_playlist", "sidebar.nav_playlist", ""),
    ("btn_by_folder", "sidebar.nav_by_folder", ""),
    ("btn_duplicates", "sidebar.nav_duplicates", ""),
    ("btn_settings_general", "sidebar.nav_settings_general", ""),
    ("btn_settings_sound", "sidebar.nav_settings_sound", ""),
    ("btn_library_sources", "sidebar.nav_library_sources", ""),
    ("btn_settings_player", "sidebar.nav_settings_player", ""),
    ("btn_settings_effects", "sidebar.nav_settings_effects", ""),
    ("btn_settings_logs", "sidebar.nav_settings_logs", ""),
    ("btn_settings_about", "sidebar.nav_settings_about", ""),
    # Page Morceaux
    ("btn_cancel_scan", "common.cancel", ""),
    ("lbl_tracks_empty_message", "duplicates.empty_playlist_message", ""),
    # Page Par dossiers et corbeille
    ("lbl_folders_page_title", "folders.page_title", ""),
    ("lbl_tree_title", "folders.tree_title", ""),
    ("cb_recursive", "folders.include_subfolders", ""),
    ("lbl_placeholder_title", "folders.empty_selection_title", ""),
    ("lbl_placeholder_desc", "folders.empty_selection_desc", ""),
    ("lbl_trash_title", "trash.banner_title", ""),
    ("lbl_trash_desc", "trash.banner_desc", ""),
    ("btn_restore_selected_trash", "trash.btn_restore_selected", ""),
    ("btn_clear_all_trash", "trash.btn_clear_all", ""),
    # Paramètres généraux et Sources
    ("lbl_settings_title", "settings.page_title", ""),
    ("lbl_library_sources_page_title", "settings.page_sources_title", ""),
    ("lbl_lib_sources_card_title", "settings.section_sources_title", ""),
    ("lbl_lib_sources_card_desc", "settings.section_sources_desc", ""),
    ("btn_lib_tab_sources", "library_sources.tab_by_source", ""),
    ("btn_lib_tab_library", "library_sources.tab_library", ""),
    ("btn_add_source_library", "sidebar.btn_add_source", ""),
    ("lbl_card_lang_title", "settings.section_language", ""),
    ("lbl_card_lang_desc", "settings.language_desc", ""),
    ("lbl_card_storage_title", "settings.section_storage", ""),
    ("btn_open_data_folder", "settings.btn_open_folder", ""),
    # Paramètres > À propos
    ("lbl_settings_about_page_title", "settings.about_page_title", ""),
    ("lbl_about_app_name", "app.name", ""),
    ("lbl_about_desc", "dialog.about_description", ""),
    ("btn_check_updates_about", "settings.btn_check_updates", ""),
    ("btn_update_download", "settings.btn_download_update", ""),
    ("lbl_about_credits_title", "dialog.about_credits_title", "👍  "),
    ("lbl_about_credits_tech", "dialog.about_credits_tech", ""),
    ("lbl_about_license", "dialog.about_license", ""),
    ("lbl_about_support_title", "dialog.about_support_title", "💖  "),
    ("btn_about_kofi", "dialog.about_btn_kofi", ""),
    ("btn_about_donate", "dialog.about_btn_kofi", ""),
    ("btn_about_sponsors", "dialog.about_btn_sponsors", ""),
    ("lbl_about_official_title", "dialog.about_official_pages_title", "🌐  "),
    ("btn_about_github", "dialog.about_btn_github", ""),
    ("btn_about_itch", "dialog.about_btn_itch", ""),
    ("action_about", "menu.about", ""),
    ("action_check_updates", "menu.check_updates", ""),
    # Paramètres > Son
    ("lbl_settings_sound_page_title", "settings.page_sound_title", ""),
    ("lbl_card_sound_proc_title", "settings.sound_processing_title", ""),
    ("lbl_card_sound_proc_desc", "settings.sound_processing_desc", ""),
    ("chk_settings_replaygain", "audio_tools.replaygain_enable", ""),
    ("lbl_settings_speed", "audio_tools.playback_speed", ""),
    ("btn_settings_speed_reset", "audio_tools.speed_reset", ""),
    # Paramètres > Lecteur : veille, transitions, moteur
    ("lbl_settings_player_page_title", "settings.page_player_title", ""),
    ("lbl_card_player_title", "settings.player_playback_title", ""),
    ("lbl_card_player_desc", "settings.player_playback_desc", ""),
    ("radio_sleep_allow", "settings.sleep_mode_allow", ""),
    ("lbl_sleep_allow_hint", "settings.sleep_mode_allow_hint", ""),
    ("radio_sleep_screens", "settings.sleep_mode_player_playlist", ""),
    ("lbl_sleep_screens_hint", "settings.sleep_mode_player_playlist_hint", ""),
    ("radio_sleep_always", "settings.sleep_mode_always", ""),
    ("lbl_sleep_always_hint", "settings.sleep_mode_always_hint", ""),
    ("lbl_card_transitions_title", "settings.player_transitions_title", ""),
    ("lbl_card_transitions_desc", "settings.player_transitions_desc", ""),
    ("radio_trans_standard", "settings.transition_standard", ""),
    ("lbl_trans_standard_hint", "settings.transition_standard_hint", ""),
    ("radio_trans_gapless", "settings.transition_gapless", ""),
    ("lbl_trans_gapless_hint", "settings.transition_gapless_hint", ""),
    ("radio_trans_crossfade", "settings.transition_crossfade", ""),
    ("lbl_trans_crossfade_hint", "settings.transition_crossfade_hint", ""),
    ("lbl_crossfade_duration", "settings.crossfade_duration", ""),
    ("lbl_card_engine_title", "settings.player_engine_choice_title", ""),
    ("lbl_card_engine_desc", "settings.player_engine_choice_desc", ""),
    ("radio_engine_buffer", "settings.player_engine_buffer_label", ""),
    ("lbl_engine_buffer_hint", "settings.player_engine_buffer_hint", ""),
    ("radio_engine_vlc", "settings.player_engine_vlc_label", ""),
    ("lbl_engine_vlc_hint", "settings.player_engine_vlc_hint", ""),
    ("lbl_vlc_latency", "settings.player_engine_vlc_latency_label", ""),
    ("lbl_vlc_latency_hint", "settings.player_engine_vlc_latency_hint", ""),
    # Paramètres > Lecteur : Blind Test
    ("lbl_card_bt_title", "blind_test.settings_title", "🎭  "),
    ("lbl_card_bt_desc", "settings.blind_test_desc", ""),
    ("lbl_bt_countdown", "blind_test.countdown_label", ""),
    ("lbl_bt_reveal", "blind_test.reveal_label", ""),
    ("lbl_bt_fade", "blind_test.fade_label", ""),
)

_TITLES: tuple[tuple[str, str], ...] = (
    ("drawer_player", "sidebar.drawer_player"),
    ("drawer_games", "sidebar.drawer_games"),
    ("drawer_tools", "sidebar.drawer_tools"),
    ("drawer_settings", "sidebar.drawer_settings"),
    ("drawer_library_mgmt", "sidebar.drawer_library_mgmt"),
)

_TOOLTIPS: tuple[tuple[str, str], ...] = (
    ("btn_refresh_tree", "folders.btn_refresh"),
    ("btn_expand_tree", "folders.btn_expand_all"),
    ("btn_collapse_tree", "folders.btn_collapse_all"),
    ("btn_expand_lib_sources", "folders.btn_expand_all"),
    ("btn_collapse_lib_sources", "folders.btn_collapse_all"),
)

_PLACEHOLDERS: tuple[tuple[str, str], ...] = (
    ("search_edit", "topbar.search_placeholder"),
    ("folder_search_edit", "folders.search_placeholder"),
)

# Vues autonomes qui gèrent elles-mêmes leurs libellés
_SUB_VIEWS: tuple[str, ...] = (
    "update_banner",
    "page_player",
    "page_blind_test",
    "page_playlist",
    "folders_player_header",
    "page_logs",
    "activity_popover",
)


class RetranslateMixin(_MixinBase):
    """Traduction dynamique de l'interface (mixin de MainWindow)."""

    if TYPE_CHECKING:
        # Les attributs/méthodes de MainWindow sont résolus dynamiquement (typage uniquement)
        def __getattr__(self, name: str) -> Any: ...

    def retranslate_ui(self) -> None:
        """Applique les traductions de la langue active à l'ensemble de l'interface."""
        self.setWindowTitle(f"{tr('app.window_title')} v{__version__}")
        self._apply_static_translations()
        self._retranslate_status_and_counts()
        self._retranslate_folders_state()
        self._retranslate_settings_dynamic()

        for name in _SUB_VIEWS:
            view = getattr(self, name, None)
            if view:
                view.retranslate_ui()
        for help_btn in self.findChildren(HelpButton):
            help_btn.retranslate_ui()
        self._sync_taskbar_and_tray()

    def _apply_static_translations(self) -> None:
        for attr, key, prefix in _TEXTS:
            widget = getattr(self, attr, None)
            if widget is not None:
                widget.setText(prefix + tr(key))
        for attr, key in _TITLES:
            drawer = getattr(self, attr, None)
            if drawer is not None:
                drawer.set_title(tr(key))
        for attr, key in _TOOLTIPS:
            widget = getattr(self, attr, None)
            if widget is not None:
                widget.setToolTip(tr(key))
        for attr, key in _PLACEHOLDERS:
            widget = getattr(self, attr, None)
            if widget is not None:
                widget.setPlaceholderText(tr(key))

        menu_help = getattr(self, "menu_help", None)
        if menu_help is not None:
            menu_help.setTitle(tr("menu.help"))
        btn_quick_about = getattr(self, "btn_quick_about", None)
        if btn_quick_about is not None:
            btn_quick_about.setToolTip(tr("dialog.about_title") + " (F1)")

    def _retranslate_status_and_counts(self) -> None:
        scanning = bool(self.scan_worker and self.scan_worker.isRunning())
        # Pendant un scan, le bouton et la barre d'état affichent la progression : ne pas l'écraser
        btn_activity_feed = getattr(self, "btn_activity_feed", None)
        if btn_activity_feed is not None and not scanning:
            btn_activity_feed.setText("⚡ " + tr("status.activity_feed"))
        if not scanning and not getattr(self, "_status_is_alert", False):
            self.status_label.setText(tr("status.ready"))
            self.status_label.setToolTip("")
            self.status_label.setCursor(Qt.CursorShape.ArrowCursor)

        self._update_track_count()
        self.table_model.notify_language_changed()

    def _retranslate_folders_state(self) -> None:
        self.folder_tree.setHeaderLabels([tr("table.col_folder_name"), tr("folders.tree_col_count")])
        self.folder_table_model.notify_language_changed()
        if self.right_stack.currentIndex() == 2:
            self._update_folder_count_badge(count=self.trash_table.rowCount(), total_duration_sec=0.0)
        else:
            self._update_folder_count_badge()

        cur_item = self.folder_tree.currentItem()
        if cur_item:
            cdata = cur_item.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(cdata, dict) and cdata.get("folder_path"):
                fp = cdata.get("folder_path")
                self.lbl_folder_breadcrumb.setToolTip(f"{fp}\n({tr('folders.breadcrumb_tooltip')})")

    def _retranslate_settings_dynamic(self) -> None:
        """Libellés qui dépendent d'une valeur courante (curseurs, chemins, état VLC) ou d'un rafraîchissement."""
        if hasattr(self, "lbl_lib_sources_card_title"):
            self._refresh_library_sources_tree()
        self._refresh_update_ui()

        cfg_p = str(get_config_path())
        db_p = str(self.db.db_path)
        self.lbl_config_path_val.setText(f"• <b>{tr('settings.config_file')}</b> <code>{cfg_p}</code>")
        self.lbl_db_path_val.setText(f"• <b>{tr('settings.db_file')}</b> <code>{db_p}</code>")

        slider_crossfade = getattr(self, "slider_crossfade", None)
        if slider_crossfade is not None and hasattr(self, "lbl_crossfade_value"):
            self.lbl_crossfade_value.setText(
                tr("settings.crossfade_duration_val", seconds=str(slider_crossfade.value()))
            )
        slider_vlc_latency = getattr(self, "slider_vlc_latency", None)
        if slider_vlc_latency is not None and hasattr(self, "lbl_vlc_latency_val"):
            self.lbl_vlc_latency_val.setText(
                tr("settings.player_engine_vlc_latency_val", ms=str(slider_vlc_latency.value()))
            )

        self._retranslate_cover_transition_card()
        self._retranslate_settings_effects_page()

        if hasattr(self, "lbl_vlc_status_val"):
            status_html, status_tip = build_vlc_status(self.player_service)
            self.lbl_vlc_status_val.setText(status_html)
            self.lbl_vlc_status_val.setToolTip(status_tip)

        if hasattr(self, "spin_bt_countdown"):
            for spin in (self.spin_bt_countdown, self.spin_bt_reveal, self.spin_bt_fade):
                spin.setSuffix(f" {tr('unit.seconds_short')}")
            self._update_blind_test_summary_label()
