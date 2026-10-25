"""Sauvegarde et restauration de la session (mixin de MainWindow)."""

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import TYPE_CHECKING, Any

from PySide6.QtWidgets import (
    QMainWindow,
)

from amso.core.config import get_config_manager
from amso.core.database import (
    SourceType,
    TrackRecord,
    get_saved_playlist_path,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    _MixinBase = QMainWindow
else:
    _MixinBase = object


class SessionStateMixin(_MixinBase):
    """Sauvegarde et restauration de la session (mixin de MainWindow)."""

    if TYPE_CHECKING:
        # Les attributs/méthodes de MainWindow sont résolus dynamiquement (typage uniquement)
        def __getattr__(self, name: str) -> Any: ...

    def _save_active_page(self) -> None:
        """Supprimé : la page active n'est plus persistée, l'appli démarre systématiquement sur le Lecteur."""
        pass

    def _restore_active_page(self) -> None:
        """Au démarrage de l'appli, on bascule systématiquement sur la page Lecteur."""
        cfg = get_config_manager()
        cfg.remove_active_page()
        page_id = "player"
        self._current_active_page = page_id

        mapping = {
            "tracks": (
                getattr(self, "btn_all_tracks", None),
                getattr(self, "drawer_library", None),
                self._on_all_tracks_clicked,
            ),
            "folders": (
                getattr(self, "btn_by_folder", None),
                getattr(self, "drawer_library", None),
                self._on_by_folder_clicked,
            ),
            "duplicates": (
                getattr(self, "btn_duplicates", None),
                getattr(self, "drawer_tools", None),
                self._on_duplicates_clicked,
            ),
            "stats": (
                getattr(self, "btn_stats_page", None),
                getattr(self, "drawer_stats", None),
                self._on_stats_page_clicked,
            ),
            "player": (
                getattr(self, "btn_player", None),
                getattr(self, "drawer_player", None),
                self._on_player_nav_clicked,
            ),
            "blind_test": (
                getattr(self, "btn_blind_test", None),
                getattr(self, "drawer_games", None),
                self._on_blind_test_nav_clicked,
            ),
            "playlist": (
                getattr(self, "btn_playlist", None),
                getattr(self, "drawer_player", None),
                self._on_playlist_nav_clicked,
            ),
            "settings_general": (
                getattr(self, "btn_settings_general", None),
                getattr(self, "drawer_settings", None),
                self._on_settings_general_clicked,
            ),
            "settings_sources": (
                getattr(self, "btn_settings_sources", None),
                getattr(self, "drawer_settings", None),
                self._on_settings_sources_clicked,
            ),
            "settings_player": (
                getattr(self, "btn_settings_player", None),
                getattr(self, "drawer_settings", None),
                self._on_settings_player_clicked,
            ),
            "logs": (
                getattr(self, "btn_settings_logs", None),
                getattr(self, "drawer_settings", None),
                self._on_settings_logs_clicked,
            ),
            "settings_about": (
                getattr(self, "btn_settings_about", None),
                getattr(self, "drawer_settings", None),
                self._on_settings_about_clicked,
            ),
        }

        if page_id in mapping:
            btn, drawer, handler = mapping[page_id]
            if drawer and page_id != "tracks":
                drawer.set_expanded(True)
            if btn:
                btn.setChecked(True)
            if handler is not None:
                handler()

    def _save_all_tables_state(self) -> None:
        """Sauvegarde l'état des tableaux de l'application (taille, visibilité, ordre des colonnes, tri)."""
        if hasattr(self, "table_view") and self.table_view:
            self._save_table_header_state(self.table_view, "all_tracks")
        if hasattr(self, "folder_table_view") and self.folder_table_view:
            self._save_table_header_state(self.folder_table_view, "folders")
        if hasattr(self, "page_playlist") and self.page_playlist:
            self.page_playlist.save_table_state()

    def _save_player_state(self) -> None:
        """Sauvegarde les paramètres du lecteur (shuffle, repeat, volume, mute, effet visuel, position) dans la configuration."""
        cfg = get_config_manager()
        if hasattr(self, "player_service") and self.player_service:
            cfg.set_player_shuffle(self.player_service.is_shuffle)
            cfg.set_player_repeat_mode(self.player_service.repeat_mode)
            cfg.set_player_volume(self.player_service.volume)
            cfg.set_player_muted(self.player_service.is_muted)
            cfg.set_player_position_ms(self.player_service.current_time_ms)
        if hasattr(self, "page_player") and self.page_player:
            eff = getattr(self.page_player, "effect_type", None)
            if not eff and hasattr(self.page_player, "effect_canvas") and self.page_player.effect_canvas:
                eff = self.page_player.effect_canvas.effect_type
            if eff:
                cfg.set_visual_effect(eff)

    def _on_player_track_changed_for_save(self, _track: TrackRecord | None) -> None:
        """Déclenché lors d'un changement de morceau pour sauvegarder l'état après stabilisation."""
        if hasattr(self, "_playlist_save_timer"):
            self._playlist_save_timer.start()

    def _on_playlist_updated_for_save(self) -> None:
        """Déclenché lors d'une modification de la file d'attente (ajout, suppression, réordonnancement)."""
        if hasattr(self, "_playlist_save_timer"):
            self._playlist_save_timer.start()

    def _save_current_playlist(self, immediate: bool = False) -> None:
        """Sauvegarde la file d'attente (playlist), l'index de lecture et la position en cours dans un fichier JSON.

        Optimisé pour les très grandes bibliothèques (> 10 000 titres) :
        - Sauvegarde compacte par identifiants SQLite (track_ids) réduisant le fichier de 99%.
        - Écriture asynchrone non-bloquante pour garantir 0 saccade sur l'interface graphique.
        """
        if not hasattr(self, "player_service") or not self.player_service:
            return
        playlist = self.player_service.playlist
        curr_idx = self.player_service.current_index
        curr_pos_ms = self.player_service.current_time_ms
        playlist_path = get_saved_playlist_path()

        if not playlist:
            data: dict[str, Any] = {
                "version": 2,
                "current_index": 0,
                "position_ms": 0,
                "track_ids": [],
            }
        elif all(t.id is not None for t in playlist) and not any(t.is_cue_segment for t in playlist):
            data = {
                "version": 2,
                "current_index": curr_idx,
                "position_ms": curr_pos_ms,
                "track_ids": [t.id for t in playlist],
            }
        else:
            data = {
                "version": 1,
                "current_index": curr_idx,
                "position_ms": curr_pos_ms,
                "tracks": [t.to_dict() for t in playlist],
            }

        def _do_write() -> None:
            try:
                playlist_path.parent.mkdir(parents=True, exist_ok=True)
                temp_path = playlist_path.with_suffix(".tmp")
                with open(temp_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
                temp_path.replace(playlist_path)
            except Exception as exc:
                logger.warning("Impossible de sauvegarder la playlist courante : %s", exc)

        if immediate:
            _do_write()
        else:
            threading.Thread(target=_do_write, daemon=True, name="PlaylistSaveThread").start()

    def _restore_saved_playlist(self) -> None:
        """Restaure la playlist, l'index et la position temporelle sauvegardés lors de la session précédente."""
        playlist_path = get_saved_playlist_path()
        if not playlist_path.exists():
            return

        try:
            with open(playlist_path, encoding="utf-8") as f:
                data = json.load(f)

            saved_index = data.get("current_index", 0)
            saved_pos_ms = data.get("position_ms", 0)
            if saved_pos_ms <= 0:
                saved_pos_ms = get_config_manager().get_player_position_ms()

            restored_tracks: list[TrackRecord] = []
            db_tracks: dict[int, TrackRecord] = {}

            # Format version 2 : liste compacte d'identifiants
            if "track_ids" in data:
                track_ids = data.get("track_ids", [])
                if track_ids and self.db:
                    try:
                        restored_tracks = self.db.get_tracks_by_ids(track_ids)
                        db_tracks = {t.id: t for t in restored_tracks if t.id is not None}
                    except Exception as e:
                        logger.warning("Erreur lors de la récupération des pistes par ID : %s", e)
            else:
                # Format version 1 : liste de dictionnaires complets
                raw_tracks = data.get("tracks", [])
                if not raw_tracks:
                    return

                track_ids = [t.get("id") for t in raw_tracks if t.get("id") is not None]
                if track_ids and self.db:
                    try:
                        for trk in self.db.get_tracks_by_ids(track_ids):
                            if trk.id is not None:
                                db_tracks[trk.id] = trk
                    except Exception:
                        pass

                for t_dict in raw_tracks:
                    tid = t_dict.get("id")
                    if tid is not None and tid in db_tracks and t_dict.get("cue_start_ms") is None:
                        restored_tracks.append(db_tracks[tid])
                    else:
                        restored_tracks.append(TrackRecord.from_dict(t_dict))

            # Filtrage des pistes orphelines ou fantômes (ex. mocks de tests ou fichiers locaux inexistants)
            # Optimisation majeure : si la piste provient de la base SQLite active (db_tracks),
            # elle est déjà validée en mémoire (O(1)) et on évite des milliers d'I/O disque bloquantes (Path.exists).
            valid_tracks: list[TrackRecord] = []
            for trk in restored_tracks:
                if trk.id is not None and trk.id in db_tracks:
                    valid_tracks.append(trk)
                elif trk.source_type != SourceType.LOCAL:
                    valid_tracks.append(trk)
                else:
                    path_str = trk.source_path or trk.source_ref
                    if path_str and Path(path_str).exists():
                        valid_tracks.append(trk)
                    elif self.db and path_str and self.db.get_track_by_ref(path_str):
                        valid_tracks.append(trk)

            if not valid_tracks:
                logger.info("Playlist sauvegardée ignorée : aucun fichier valide trouvé.")
                return

            saved_index = max(0, min(saved_index, len(valid_tracks) - 1))
            current_track = valid_tracks[saved_index]
            if current_track.duration_seconds and current_track.duration_seconds > 0:
                dur_ms = int(current_track.duration_seconds * 1000)
                if saved_pos_ms >= dur_ms:
                    saved_pos_ms = 0
                else:
                    saved_pos_ms = max(0, saved_pos_ms)

            self.player_service.load_playlist(
                valid_tracks,
                current_index=saved_index,
                initial_position_ms=saved_pos_ms,
            )
            if hasattr(self, "page_playlist") and self.page_playlist:
                self.page_playlist._update_stats_label()
        except Exception as exc:
            logger.warning("Erreur lors de la restauration de la playlist : %s", exc)

    # -------------------------------------------------------------------------
    # Construction de l'interface graphique
    # -------------------------------------------------------------------------
