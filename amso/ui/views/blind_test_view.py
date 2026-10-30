"""Vue dédiée au mode Blind Test interactif pour AMSO."""

from __future__ import annotations

import time

from PySide6.QtCore import QTimer, Signal
from PySide6.QtGui import QHideEvent, QResizeEvent
from PySide6.QtWidgets import QWidget

from amso.core.config import get_config_manager
from amso.core.database import TrackRecord
from amso.core.i18n import tr
from amso.services.player_service import PlayerService, RepeatMode
from amso.ui.views.blind_test.compat import BlindTestCompatMixin
from amso.ui.views.blind_test.fades import BlindTestFadesMixin
from amso.ui.views.blind_test.round_controller import BlindTestRoundMixin
from amso.ui.views.blind_test.ui_builder import BlindTestUiMixin
from amso.ui.views.blind_test.zoom_fade_label import ZoomFadeLabel
from amso.ui.views.cover_helper import get_default_cover_pixmap

__all__ = ["BlindTestView", "ZoomFadeLabel"]


class BlindTestView(BlindTestUiMixin, BlindTestRoundMixin, BlindTestFadesMixin, BlindTestCompatMixin, QWidget):
    """Page dédiée au jeu de Blind Test musical grand format."""

    effect_changed = Signal(str)

    def __init__(self, player_service: PlayerService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.player = player_service

        # États du Blind Test : "countdown", "revealed", "idle"
        self._state: str = "idle"
        cfg = get_config_manager()
        self._configured_countdown: int = cfg.get_blind_test_countdown()
        self._configured_reveal: int = cfg.get_blind_test_reveal()
        self._configured_fade: int = cfg.get_blind_test_fade()
        self._countdown_remain: int = self._configured_countdown
        self._reveal_remain: int = self._configured_reveal
        self._total_round_duration: int = self._countdown_remain + self._reveal_remain
        self._current_round_elapsed: int = 0
        self._is_active_page: bool = False
        self.current_effect: str = cfg.get_visual_effect()
        self._nominal_volume: int = getattr(self.player, "volume", 100)
        self._is_fading: bool = False
        self._fade_start_time: float = 0.0
        self._fade_duration: float = float(self._configured_fade)

        # Fondu entrant (Fade-in 0% -> 100% sur 2.0 secondes)
        self._is_fading_in: bool = False
        self._fade_in_duration: float = 2.0
        self._fade_in_start_time: float = 0.0
        self._fade_in_paused_elapsed: float = 0.0

        # Sauvegarde d'état du lecteur
        self._saved_player_index: int | None = None
        self._saved_player_position_ms: int = 0
        self._session_playing: bool = False
        # `play()` émet `track_changed` ; la manche est déjà prête, la relancer re-positionnerait la piste
        # (`seek_ratio` → `load_index`) avant que le décodeur ait livré son premier bloc et la remettrait en pause.
        self._is_starting_playback: bool = False

        self._setup_ui()
        self._connect_signals()

        # Timer d'horloge de seconde en seconde pour le Blind Test
        self._game_timer = QTimer(self)
        self._game_timer.setInterval(1000)
        self._game_timer.timeout.connect(self._on_game_tick)

        # Timer pour fondu sonore progressif sortant (fin de manche)
        self._fade_timer = QTimer(self)
        self._fade_timer.setInterval(50)
        self._fade_timer.timeout.connect(self._on_fade_tick)

        # Timer pour fondu sonore progressif entrant (0% -> 100% en 2 secondes au début)
        self._fade_in_timer = QTimer(self)
        self._fade_in_timer.setInterval(50)
        self._fade_in_timer.timeout.connect(self._on_fade_in_tick)

    def _on_player_position_changed(self, current_ms: int, total_ms: int, ratio: float) -> None:
        if hasattr(self, "effect_canvas") and self.effect_canvas:
            self.effect_canvas.update_audio_time(current_ms, ratio)

    def _on_playlist_updated(self) -> None:
        if self._is_active_page:
            self._update_session_progress()

    def showEvent(self, event) -> None:
        """Déclenché lorsque l'utilisateur affiche la page Blind Test.
        Sauvegarde l'état du lecteur sans démarrer la musique automatiquement."""
        super().showEvent(event)
        self._is_active_page = True
        self._session_playing = False

        if self._state == "revealed" and hasattr(self, "cover_opacity") and self.cover_opacity:
            self.cover_opacity.setEnabled(False)
        if hasattr(self, "lbl_cover") and self.lbl_cover:
            self.lbl_cover.update()
        if hasattr(self, "cover_box") and self.cover_box:
            self.cover_box.update()

        if hasattr(self, "effect_canvas") and self.effect_canvas:
            self.effect_canvas.showEvent(event)
            eff_state = "playing" if self.player.is_playing else "stopped"
            self.effect_canvas.set_playback_state(eff_state)
            self.effect_canvas.update_audio_volume(self.player.volume, self.player.is_muted)
            if self.player.current_track:
                self.effect_canvas.set_track(self.player.current_track)

        # Sauvegarder l'état exact du lecteur (piste sélectionnée, position, lecture en cours)
        # pour le restaurer fidèlement lorsqu'on quitte le Blind Test
        self._saved_player_index = self.player.current_index
        self._saved_player_position_ms = getattr(self.player, "current_time_ms", 0)
        self._saved_player_was_playing = self.player.is_playing

        # La musique ne doit PAS démarrer de suite lors de l'arrivée sur la page
        if self.player.is_playing:
            self.player.pause()

        # Synchroniser l'effet visuel actif avec le ConfigManager
        cfg = get_config_manager()
        eff = cfg.get_visual_effect()
        self.set_effect_type(eff)

        # Préparer la manche sur le morceau courant à 0 seconde, en attente de play
        if self.player.current_track:
            self._start_round_for_track(self.player.current_track, auto_play=False)
        elif self.player.playlist:
            if hasattr(self.player, "load_index"):
                self.player.load_index(0)
            else:
                self.player.play_index(0)
                self.player.pause()
            self._start_round_for_track(self.player.current_track, auto_play=False)
        else:
            self._reset_to_empty_state()

        self._update_session_progress()

    def hideEvent(self, event: QHideEvent) -> None:
        """Déclenché lorsque l'utilisateur quitte la page Blind Test.
        La musique doit impérativement s'arrêter dès qu'on sort du Blind Test."""
        self._is_active_page = False
        self._session_playing = False
        if hasattr(self, "effect_canvas") and self.effect_canvas:
            self.effect_canvas.set_playback_state("stopped")
            self.effect_canvas.hideEvent(event)

        # Stopper les timers et rétablir le volume nominal
        self._game_timer.stop()
        self._stop_fade_out()
        self._stop_fade_in()
        self._stop_fade_and_restore_volume()

        # Arrêter la lecture immédiatement et réinitialiser tout préchargement
        self.player.pause()
        if hasattr(self.player, "_reset_standby_player"):
            self.player._reset_standby_player()

        # Restauration de l'état du lecteur enregistré avant le Blind Test (en pause silencieuse garantie)
        self._restore_saved_player_state()

        # Garantie absolue : s'assurer que le lecteur est bien en pause
        if self.player.is_playing:
            self.player.pause()
        if hasattr(self.player, "_reset_standby_player"):
            self.player._reset_standby_player()

        try:
            super().hideEvent(event)
        except Exception:
            pass

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Gère le redimensionnement de la vue (bascule plein écran / fenêtré)
        en forçant la synchronisation géométrique de la pochette pour éviter tout décalage d'affichage."""
        super().resizeEvent(event)
        if hasattr(self, "cover_opacity") and self.cover_opacity:
            if self._state == "revealed":
                self.cover_opacity.setEnabled(False)
            else:
                self.cover_opacity.updateBoundingRect()
                self.cover_opacity.update()
        if hasattr(self, "lbl_cover") and self.lbl_cover:
            self.lbl_cover.update()
        if hasattr(self, "cover_box") and self.cover_box:
            self.cover_box.update()

    def _restore_saved_player_state(self) -> None:
        """Restaure la piste et la position de lecture qui étaient actives avant d'entrer en Blind Test.
        La musique est impérativement mise en pause dès qu'on sort du Blind Test."""
        if hasattr(self.player, "_reset_standby_player"):
            self.player._reset_standby_player()

        if not hasattr(self, "_saved_player_index") or self._saved_player_index is None:
            self.player.pause()
            return

        saved_idx = self._saved_player_index
        saved_ms = getattr(self, "_saved_player_position_ms", 0)
        self._saved_player_index = None

        if not self.player.playlist or saved_idx < 0 or saved_idx >= len(self.player.playlist):
            self.player.pause()
            return

        # Si le Blind Test a changé de piste ou si la position a changé :
        # Utiliser load_index pour repositionner le lecteur SANS JAMAIS lancer de lecture audio
        if hasattr(self.player, "load_index"):
            self.player.load_index(saved_idx, seek_ms=saved_ms)
        else:
            self.player.pause()
        if hasattr(self.player, "_reset_standby_player"):
            self.player._reset_standby_player()

    def set_durations(self, countdown_seconds: int, reveal_seconds: int, fade_seconds: int | None = None) -> None:
        """Met à jour les durées configurées du Blind Test."""
        self._configured_countdown = countdown_seconds
        self._configured_reveal = reveal_seconds
        if fade_seconds is not None:
            self._configured_fade = fade_seconds
        self._countdown_remain = countdown_seconds
        self._reveal_remain = reveal_seconds
        self._total_round_duration = countdown_seconds + reveal_seconds
        self._fade_duration = float(self._configured_fade)

    def _on_reveal_clicked(self) -> None:
        """Révèle immédiatement la piste si les joueurs ont trouvé avant la fin des 20s.
        Garantit qu'il reste la durée complète de découverte (10s par défaut)."""
        if self._state == "countdown":
            self._trigger_reveal()

    def _on_prev_track_clicked(self) -> None:
        """Revient à 0 d'abord si la manche a déjà démarré (> 2s ou révélée),
        ou passe réellement au morceau précédent si au tout début.
        Si on est au premier morceau (index 0) et qu'on ne boucle pas, redémarre la manche 0."""
        was_playing = self.player.is_playing or self._session_playing
        self._session_playing = was_playing

        repeat_all = getattr(self.player, "repeat_mode", None) == RepeatMode.ALL
        cur_idx = getattr(self.player, "current_index", 0)
        is_first_track = isinstance(cur_idx, int) and cur_idx <= 0 and not repeat_all

        if self._current_round_elapsed > 2 or self._state == "revealed" or is_first_track:
            self._restart_current_round(auto_play=was_playing)
        else:
            self._stop_fade_out()
            self._stop_fade_in()
            self._apply_temporary_volume(0)
            self._game_timer.stop()
            self.player.previous()

    def _on_next_track_clicked(self) -> None:
        """Passe immédiatement au titre suivant dans le Blind Test (démarre à 0s).
        Boucle sur le premier morceau si on est au dernier titre."""
        self._session_playing = True
        self._game_timer.stop()
        self._stop_fade_out()
        self._stop_fade_in()
        self._apply_temporary_volume(0)

        playlist = getattr(self.player, "playlist", None)
        total = len(playlist) if isinstance(playlist, (list, tuple)) else 0
        cur = getattr(self.player, "current_index", 0)
        repeat_all = getattr(self.player, "repeat_mode", None) == RepeatMode.ALL
        if isinstance(cur, int) and total > 0 and cur + 1 >= total and not repeat_all:
            self.player.play_index(0)
        else:
            self.player.next()

    def _on_play_pause_clicked(self) -> None:
        """Met en pause ou reprend la lecture et le décompte."""
        if self.player.is_playing:
            self._session_playing = False
            self.player.pause()
            self._game_timer.stop()
            if self._is_fading and hasattr(self, "_fade_timer"):
                self._fade_timer.stop()
                self._fade_paused_elapsed = max(0.0, time.time() - self._fade_start_time)
            if self._is_fading_in and hasattr(self, "_fade_in_timer"):
                self._fade_in_timer.stop()
                self._fade_in_paused_elapsed = max(0.0, time.time() - self._fade_in_start_time)
            self.btn_play_pause.setText("▶")
            self.lbl_status_badge.setText(tr("blind_test.status_paused"))
            self.lbl_status_badge.setStyleSheet("""
                color: #94A3B8;
                font-size: 12px;
                font-weight: 600;
                padding: 3px 12px;
                border-radius: 10px;
                background-color: rgba(148, 163, 184, 0.12);
                border: 1px solid rgba(148, 163, 184, 0.3);
            """)
        else:
            self._session_playing = True
            # Démarrer ou reprendre la lecture
            is_start_of_round = self._current_round_elapsed == 0 and self._state == "countdown"
            if is_start_of_round:
                self.player.seek_ratio(0.0)
                self._apply_temporary_volume(0)

            self._is_starting_playback = True
            try:
                self.player.play()
            finally:
                self._is_starting_playback = False

            if self._is_active_page:
                self._game_timer.start(1000)
                if is_start_of_round:
                    self._start_fade_in(2.0)
                elif self._is_fading_in and hasattr(self, "_fade_in_timer"):
                    self._fade_in_start_time = time.time() - getattr(self, "_fade_in_paused_elapsed", 0.0)
                    self._fade_in_timer.start(50)
                elif self._is_fading and hasattr(self, "_fade_timer"):
                    self._fade_start_time = time.time() - getattr(self, "_fade_paused_elapsed", 0.0)
                    self._fade_timer.start(50)

            self.btn_play_pause.setText("⏸")
            if self._state == "countdown":
                self.lbl_status_badge.setText(tr("blind_test.status_searching"))
                self.lbl_status_badge.setStyleSheet("""
                    color: #38BDF8;
                    font-size: 12px;
                    font-weight: 600;
                    padding: 3px 12px;
                    border-radius: 10px;
                    background-color: rgba(56, 189, 248, 0.12);
                    border: 1px solid rgba(56, 189, 248, 0.3);
                """)
            elif self._state == "revealed":
                self.lbl_status_badge.setText(tr("blind_test.status_revealed", remain=self._reveal_remain))
                self.lbl_status_badge.setStyleSheet("""
                    color: #4ADE80;
                    font-size: 12px;
                    font-weight: 600;
                    padding: 3px 12px;
                    border-radius: 10px;
                    background-color: rgba(74, 222, 128, 0.12);
                    border: 1px solid rgba(74, 222, 128, 0.3);
                """)

    def _on_track_changed(self, track: TrackRecord | None) -> None:
        """Appelé lors d'un changement de piste dans le PlayerService."""
        if hasattr(self, "effect_canvas") and self.effect_canvas:
            self.effect_canvas.set_track(track)
        if self._is_active_page and not self._is_starting_playback:
            auto_play = self._session_playing or self.player.is_playing
            # Moteur buffer uniquement : le chemin VLC est validé tel quel et garde son repositionnement.
            player_started = (
                auto_play
                and get_config_manager().get_audio_engine() == "buffer"
                and not getattr(self.player, "_is_paused_requested", True)
            )
            self._start_round_for_track(track, auto_play=auto_play, player_started=player_started)

    def _on_playback_state_changed(self, state: str) -> None:
        if hasattr(self, "effect_canvas") and self.effect_canvas:
            self.effect_canvas.set_playback_state(state)
        if not self._is_active_page:
            return
        is_playing = state == "playing"
        self.btn_play_pause.setText("⏸" if is_playing else "▶")
        if is_playing:
            self._session_playing = True
            if self._state == "countdown":
                self.lbl_status_badge.setText(tr("blind_test.status_searching"))
                self.lbl_status_badge.setStyleSheet("""
                    color: #38BDF8;
                    font-size: 12px;
                    font-weight: 600;
                    padding: 3px 12px;
                    border-radius: 10px;
                    background-color: rgba(56, 189, 248, 0.12);
                    border: 1px solid rgba(56, 189, 248, 0.3);
                """)
                if not self._is_fading_in and not self._is_fading:
                    self._start_fade_in(2.0)
            elif self._state == "revealed":
                self.lbl_status_badge.setText(tr("blind_test.status_revealed", remain=self._reveal_remain))
                self.lbl_status_badge.setStyleSheet("""
                    color: #4ADE80;
                    font-size: 12px;
                    font-weight: 600;
                    padding: 3px 12px;
                    border-radius: 10px;
                    background-color: rgba(74, 222, 128, 0.12);
                    border: 1px solid rgba(74, 222, 128, 0.3);
                """)
            if self._state != "idle":
                self._game_timer.start(1000)
        else:
            self._game_timer.stop()
            if state in ("paused", "stopped"):
                self.lbl_status_badge.setText(tr("blind_test.status_paused"))
                self.lbl_status_badge.setStyleSheet("""
                    color: #94A3B8;
                    font-size: 12px;
                    font-weight: 600;
                    padding: 3px 12px;
                    border-radius: 10px;
                    background-color: rgba(148, 163, 184, 0.12);
                    border: 1px solid rgba(148, 163, 184, 0.3);
                """)

    def _reset_to_empty_state(self) -> None:
        self._state = "idle"
        self._game_timer.stop()
        self._stop_fade_out()
        self._stop_fade_in()
        self.lbl_countdown.setVisible(False)
        self.lbl_cover.setPixmap(get_default_cover_pixmap())
        self.cover_opacity.setEnabled(True)
        self.cover_opacity.setOpacity(0.3)
        self.lbl_title.setText(tr("blind_test.no_track"))
        self.lbl_artist_album.setText("")
        if hasattr(self, "lbl_file_name"):
            self.lbl_file_name.setText("")
            self.lbl_file_name.setVisible(False)
        self.lbl_status_badge.setText(tr("blind_test.no_track"))
        self.btn_reveal.setEnabled(False)
        self.round_progress.setValue(0)
        self._update_session_progress()

    # -------------------------------------------------------------------------
    # Gestion du volume et effets visuels
    # -------------------------------------------------------------------------

    def _toggle_mute(self) -> None:
        self.player.toggle_mute()

    def _on_volume_changed(self, val: int) -> None:
        self._nominal_volume = val
        self.player.set_volume(val)
        self.lbl_volume.setText(f"{val}%")

    def _on_player_volume_changed(self, vol: int, muted: bool) -> None:
        if not self._is_fading and not getattr(self, "_is_fading_in", False):
            self._nominal_volume = vol
            if hasattr(self, "effect_canvas") and self.effect_canvas:
                self.effect_canvas.update_audio_volume(vol, muted)
        self.slider_volume.blockSignals(True)
        self.slider_volume.setValue(vol)
        self.slider_volume.blockSignals(False)
        self.lbl_volume.setText(tr("player.btn_mute") if (muted or vol == 0) else f"{vol}%")
        self.btn_mute.setText("🔇" if (muted or vol == 0) else "🔊")

    def retranslate_ui(self) -> None:
        """Met à jour les textes traduits lors d'un changement de langue."""
        self.lbl_page_title.setText("🎭  " + tr("blind_test.title"))
        self.lbl_effect_badge.setText(tr("player.visual_effect"))
        self._populate_effects_combo()
        if hasattr(self, "btn_prev"):
            self.btn_prev.setText(tr("blind_test.btn_prev"))
        self.btn_reveal.setText(tr("blind_test.btn_reveal"))
        self.btn_next.setText(tr("blind_test.btn_next"))
        if self._state == "countdown":
            self.lbl_title.setText("❓  " + tr("blind_test.mystery_title"))
            self.lbl_artist_album.setText("👥  " + tr("blind_test.mystery_artist"))
            if hasattr(self, "lbl_file_name"):
                self.lbl_file_name.setText("📁  " + tr("blind_test.mystery_file"))
            self.lbl_status_badge.setText(tr("blind_test.status_searching"))
        elif self._state == "revealed":
            self.lbl_status_badge.setText(tr("blind_test.status_revealed", remain=self._reveal_remain))
        elif self._state == "idle":
            self._reset_to_empty_state()

        self._update_session_progress()
