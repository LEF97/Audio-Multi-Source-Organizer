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

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    _MixinBase = QMainWindow
else:
    _MixinBase = object


class RetranslateMixin(_MixinBase):
    """Traduction dynamique de l'interface (mixin de MainWindow)."""

    if TYPE_CHECKING:
        # Les attributs/méthodes de MainWindow sont résolus dynamiquement (typage uniquement)
        def __getattr__(self, name: str) -> Any: ...

    def retranslate_ui(self) -> None:
        """Applique les traductions de la langue active à l'ensemble de l'interface."""
        self.setWindowTitle(f"{tr('app.window_title')} v{__version__}")

        # Tiroirs
        if hasattr(self, "drawer_player"):
            self.drawer_player.set_title(tr("sidebar.drawer_player"))
        if hasattr(self, "drawer_games"):
            self.drawer_games.set_title(tr("sidebar.drawer_games"))
        self.drawer_library.set_title(tr("sidebar.drawer_library"))
        self.drawer_tools.set_title(tr("sidebar.drawer_tools"))
        self.drawer_stats.set_title(tr("sidebar.drawer_stats"))
        self.drawer_sources.set_title(tr("sidebar.drawer_sources"))
        self.drawer_settings.set_title(tr("sidebar.drawer_settings"))

        # Boutons de tiroir
        if hasattr(self, "btn_player"):
            self.btn_player.setText(tr("sidebar.nav_player"))
        if hasattr(self, "btn_blind_test"):
            self.btn_blind_test.setText(tr("sidebar.nav_blind_test"))
        if hasattr(self, "btn_playlist"):
            self.btn_playlist.setText(tr("sidebar.nav_playlist"))
        self.btn_all_tracks.setText(tr("sidebar.nav_all_tracks"))
        self.btn_by_folder.setText(tr("sidebar.nav_by_folder"))
        self.btn_duplicates.setText(tr("sidebar.nav_duplicates"))
        self.btn_stats_page.setText(tr("sidebar.nav_stats_page"))
        self.btn_settings_general.setText(tr("sidebar.nav_settings_general"))
        if hasattr(self, "btn_settings_sources"):
            self.btn_settings_sources.setText(tr("sidebar.nav_settings_sources"))
        if hasattr(self, "btn_settings_player"):
            self.btn_settings_player.setText(tr("sidebar.nav_settings_player"))
        if hasattr(self, "btn_settings_logs"):
            self.btn_settings_logs.setText(tr("sidebar.nav_settings_logs"))
        if hasattr(self, "btn_settings_about"):
            self.btn_settings_about.setText(tr("sidebar.nav_settings_about"))
        if hasattr(self, "btn_activity_feed") and not (self.scan_worker and self.scan_worker.isRunning()):
            self.btn_activity_feed.setText("⚡ " + tr("status.activity_feed"))
        self.btn_add_source.setText(tr("sidebar.btn_add_source"))

        # Page Morceaux
        self.search_edit.setPlaceholderText(tr("topbar.search_placeholder"))
        self.btn_cancel_scan.setText(tr("status.cancel"))

        if not (self.scan_worker and self.scan_worker.isRunning()):
            if not getattr(self, "_status_is_alert", False):
                self.status_label.setText(tr("status.ready"))
                self.status_label.setToolTip("")
                self.status_label.setCursor(Qt.CursorShape.ArrowCursor)

        self._update_track_count()
        self.table_model.notify_language_changed()

        # Page Statistiques
        self.lbl_stats_page_title.setText(tr("stats.page_title"))
        self.btn_refresh_stats.setText(tr("stats.btn_refresh"))
        self.lbl_kpi_tracks_title.setText(tr("stats.card_tracks"))
        self.lbl_kpi_size_title.setText(tr("stats.card_size"))
        self.lbl_kpi_duration_title.setText(tr("stats.card_duration"))
        self.lbl_kpi_sources_title.setText(tr("stats.card_sources"))
        self.lbl_section_formats.setText(tr("stats.section_formats"))
        self.lbl_section_sources.setText(tr("stats.section_sources"))
        self._refresh_stats_view()

        # Page Par dossiers
        self.lbl_folders_page_title.setText(tr("folders.page_title"))
        self.lbl_tree_title.setText(tr("folders.tree_title"))
        self.btn_refresh_tree.setToolTip(tr("folders.btn_refresh"))
        self.btn_expand_tree.setToolTip(tr("folders.btn_expand_all"))
        self.btn_collapse_tree.setToolTip(tr("folders.btn_collapse_all"))
        self.cb_recursive.setText(tr("folders.include_subfolders"))
        self.folder_search_edit.setPlaceholderText(tr("folders.search_placeholder"))
        self.lbl_placeholder_title.setText(tr("folders.empty_selection_title"))
        self.lbl_placeholder_desc.setText(tr("folders.empty_selection_desc"))
        self.folder_tree.setHeaderLabels([tr("folders.tree_col_folder"), tr("folders.tree_col_count")])
        self.folder_table_model.notify_language_changed()
        cnt = self.folder_table_model.rowCount()
        count_key = "folders.track_count_singular" if cnt == 1 else "folders.track_count"
        self.lbl_folder_count_badge.setText(tr(count_key, count=f"{cnt:,}"))

        cur_item = self.folder_tree.currentItem()
        if cur_item:
            cdata = cur_item.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(cdata, dict) and cdata.get("folder_path"):
                fp = cdata.get("folder_path")
                self.lbl_folder_breadcrumb.setToolTip(f"{fp}\n({tr('folders.breadcrumb_tooltip')})")

        # Corbeille dans la vue Dossiers
        if hasattr(self, "lbl_trash_title"):
            self.lbl_trash_title.setText(tr("trash.banner_title"))
        if hasattr(self, "lbl_trash_desc"):
            self.lbl_trash_desc.setText(tr("trash.banner_desc"))
        if hasattr(self, "btn_restore_selected_trash"):
            self.btn_restore_selected_trash.setText(tr("trash.btn_restore_selected"))
        if hasattr(self, "btn_clear_all_trash"):
            self.btn_clear_all_trash.setText(tr("trash.btn_clear_all"))

        # Page Paramètres
        self.lbl_settings_title.setText(tr("settings.page_title"))
        if hasattr(self, "lbl_settings_sources_page_title"):
            self.lbl_settings_sources_page_title.setText(tr("settings.page_sources_title"))
        if hasattr(self, "lbl_card_sources_title"):
            self.lbl_card_sources_title.setText(tr("settings.section_sources_title"))
            self.lbl_card_sources_desc.setText(tr("settings.section_sources_desc"))
            self.btn_add_source_settings.setText(tr("sidebar.btn_add_source"))
            self._refresh_settings_sources_table()
        self.lbl_card_lang_title.setText(tr("settings.section_language"))
        self.lbl_card_lang_desc.setText(tr("settings.language_desc"))
        self.lbl_card_storage_title.setText(tr("settings.section_storage"))
        self.btn_open_data_folder.setText(tr("settings.btn_open_folder"))

        # Page Paramètres > À propos
        if hasattr(self, "lbl_settings_about_page_title"):
            self.lbl_settings_about_page_title.setText(tr("settings.about_page_title"))
        if hasattr(self, "lbl_about_app_name"):
            self.lbl_about_app_name.setText(tr("dialog.about_app_name"))
        if hasattr(self, "lbl_about_desc"):
            self.lbl_about_desc.setText(tr("dialog.about_description"))
        if hasattr(self, "btn_check_updates_about"):
            self.btn_check_updates_about.setText(tr("settings.btn_check_updates"))
        if hasattr(self, "btn_update_download"):
            self.btn_update_download.setText(tr("settings.btn_download_update"))
        self._refresh_update_ui()
        if hasattr(self, "lbl_about_credits_title"):
            self.lbl_about_credits_title.setText("👍  " + tr("dialog.about_credits_title"))
        if hasattr(self, "lbl_about_credits_tech"):
            self.lbl_about_credits_tech.setText(tr("dialog.about_credits_tech"))
        if hasattr(self, "lbl_about_license"):
            self.lbl_about_license.setText(tr("dialog.about_license"))
        if hasattr(self, "lbl_about_support_title"):
            self.lbl_about_support_title.setText("💖  " + tr("dialog.about_support_title"))
        if hasattr(self, "btn_about_kofi"):
            self.btn_about_kofi.setText(tr("dialog.about_btn_kofi"))
        if hasattr(self, "btn_about_donate"):
            self.btn_about_donate.setText(tr("dialog.about_btn_kofi"))
        if hasattr(self, "btn_about_sponsors"):
            self.btn_about_sponsors.setText(tr("dialog.about_btn_sponsors"))
        if hasattr(self, "lbl_about_official_title"):
            self.lbl_about_official_title.setText("🌐  " + tr("dialog.about_official_pages_title"))
        if hasattr(self, "btn_about_github"):
            self.btn_about_github.setText(tr("dialog.about_btn_github"))
        if hasattr(self, "btn_about_itch"):
            self.btn_about_itch.setText(tr("dialog.about_btn_itch"))

        if hasattr(self, "btn_quick_about"):
            self.btn_quick_about.setToolTip(tr("dialog.about_title") + " (F1)")
        if hasattr(self, "menu_help") and self.menu_help is not None:
            self.menu_help.setTitle(tr("menu.help"))
        if hasattr(self, "action_about") and self.action_about is not None:
            self.action_about.setText(tr("menu.about"))
        if hasattr(self, "action_check_updates") and self.action_check_updates is not None:
            self.action_check_updates.setText(tr("menu.check_updates"))
        if hasattr(self, "update_banner"):
            self.update_banner.retranslate_ui()

        cfg_p = str(get_config_path())
        db_p = str(self.db.db_path)
        self.lbl_config_path_val.setText(f"• <b>{tr('settings.config_file')}</b> <code>{cfg_p}</code>")
        self.lbl_db_path_val.setText(f"• <b>{tr('settings.db_file')}</b> <code>{db_p}</code>")

        if hasattr(self, "lbl_settings_player_page_title"):
            self.lbl_settings_player_page_title.setText(tr("settings.page_player_title"))
            self.lbl_card_player_title.setText(tr("settings.player_playback_title"))
            self.lbl_card_player_desc.setText(tr("settings.player_playback_desc"))
            if hasattr(self, "radio_sleep_allow"):
                self.radio_sleep_allow.setText(tr("settings.sleep_mode_allow"))
                self.lbl_sleep_allow_hint.setText(tr("settings.sleep_mode_allow_hint"))
                self.radio_sleep_screens.setText(tr("settings.sleep_mode_player_playlist"))
                self.lbl_sleep_screens_hint.setText(tr("settings.sleep_mode_player_playlist_hint"))
                self.radio_sleep_always.setText(tr("settings.sleep_mode_always"))
                self.lbl_sleep_always_hint.setText(tr("settings.sleep_mode_always_hint"))

            if hasattr(self, "lbl_card_transitions_title"):
                self.lbl_card_transitions_title.setText(tr("settings.player_transitions_title"))
                self.lbl_card_transitions_desc.setText(tr("settings.player_transitions_desc"))
                self.radio_trans_standard.setText(tr("settings.transition_standard"))
                self.lbl_trans_standard_hint.setText(tr("settings.transition_standard_hint"))
                self.radio_trans_gapless.setText(tr("settings.transition_gapless"))
                self.lbl_trans_gapless_hint.setText(tr("settings.transition_gapless_hint"))
                self.radio_trans_crossfade.setText(tr("settings.transition_crossfade"))
                self.lbl_trans_crossfade_hint.setText(tr("settings.transition_crossfade_hint"))
                self.lbl_crossfade_duration.setText(tr("settings.crossfade_duration"))
                self.lbl_crossfade_value.setText(
                    tr("settings.crossfade_duration_val", seconds=str(self.slider_crossfade.value()))
                )

            if hasattr(self, "lbl_card_effects_title"):
                self.lbl_card_effects_title.setText(tr("settings.player_effects_title"))
                self.lbl_card_effects_desc.setText(tr("settings.player_effects_desc"))
                self.radio_eff_particles.setText(f"✨ {tr('effects.particles')}")
                self.lbl_eff_particles_hint.setText(tr("effects.particles_hint"))
                self.radio_eff_waves.setText(f"🌊 {tr('effects.waves')}")
                self.lbl_eff_waves_hint.setText(tr("effects.waves_hint"))
                self.radio_eff_stars.setText(f"☄️ {tr('effects.stars')}")
                self.lbl_eff_stars_hint.setText(tr("effects.stars_hint"))
                self.radio_eff_warp.setText(f"🚀 {tr('effects.warp')}")
                self.lbl_eff_warp_hint.setText(tr("effects.warp_hint"))
                self.radio_eff_warp_dynamic.setText(f"🛸 {tr('effects.warp_dynamic')}")
                self.lbl_eff_warp_dynamic_hint.setText(tr("effects.warp_dynamic_hint"))
                self.radio_eff_aurora.setText(f"🌌 {tr('effects.aurora')}")
                self.lbl_eff_aurora_hint.setText(tr("effects.aurora_hint"))
                self.radio_eff_bars.setText(f"📊 {tr('effects.bars')}")
                self.lbl_eff_bars_hint.setText(tr("effects.bars_hint"))
                self.radio_eff_bars_full.setText(f"📶 {tr('effects.bars_full')}")
                self.lbl_eff_bars_full_hint.setText(tr("effects.bars_full_hint"))
                self.radio_eff_none.setText(f"🚫 {tr('effects.none')}")
                self.lbl_eff_none_hint.setText(tr("effects.none_hint"))

            self.lbl_card_vlc_title.setText(tr("settings.player_engine_title"))
            self.lbl_card_vlc_desc.setText(tr("settings.player_engine_desc"))
            is_avail = self.player_service.is_vlc_available
            status_txt = tr("settings.player_engine_active") if is_avail else tr("settings.player_engine_inactive")
            status_color = "#34D399" if is_avail else "#EF4444"
            self.lbl_vlc_status_val.setText(
                f"• <b>{tr('settings.player_engine_status')}</b> <span style='color: {status_color}; font-weight: 600;'>{status_txt}</span>"
            )

            if hasattr(self, "lbl_card_bt_title"):
                self.lbl_card_bt_title.setText("🎭  " + tr("blind_test.settings_title"))
                self.lbl_card_bt_desc.setText(tr("settings.blind_test_desc"))
                self.lbl_bt_countdown.setText(tr("blind_test.countdown_label"))
                self.lbl_bt_reveal.setText(tr("blind_test.reveal_label"))
                self.lbl_bt_fade.setText(tr("blind_test.fade_label"))
                self._update_blind_test_summary_label()

        # Vues Lecteur, Blind Test et Playlist
        if hasattr(self, "page_player") and self.page_player:
            self.page_player.retranslate_ui()
        if hasattr(self, "page_blind_test") and self.page_blind_test:
            self.page_blind_test.retranslate_ui()
        if hasattr(self, "page_playlist") and self.page_playlist:
            self.page_playlist.retranslate_ui()
        if hasattr(self, "page_logs") and self.page_logs:
            self.page_logs.retranslate_ui()
        if hasattr(self, "activity_popover") and self.activity_popover:
            self.activity_popover.retranslate_ui()
