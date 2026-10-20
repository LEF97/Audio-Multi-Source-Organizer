"""Vue dédiée au mode Blind Test interactif pour AMSO."""

from __future__ import annotations

import os
import time

from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import QHideEvent, QPixmap, QResizeEvent
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QLabel,
    QPushButton,
    QWidget,
)

from amso.core.config import get_config_manager
from amso.core.database import TrackRecord
from amso.core.i18n import tr
from amso.services.player_service import PlayerService, RepeatMode
from amso.ui.views.blind_test.fades import BlindTestFadesMixin
from amso.ui.views.blind_test.ui_builder import BlindTestUiMixin
from amso.ui.views.blind_test.zoom_fade_label import ZoomFadeLabel  # noqa: F401 (ré-export)
from amso.ui.views.cover_helper import get_default_cover_pixmap, load_cover_async


class BlindTestView(BlindTestUiMixin, BlindTestFadesMixin, QWidget):
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

        # Arrêter la lecture immédiatement
        self.player.pause()

        # Restauration de l'état du lecteur enregistré avant le Blind Test (en pause silencieuse garantie)
        self._restore_saved_player_state()

        # Garantie absolue : s'assurer que le lecteur est bien en pause
        if self.player.is_playing:
            self.player.pause()

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

    def set_durations(
        self, countdown_seconds: int, reveal_seconds: int, fade_seconds: int | None = None
    ) -> None:
        """Met à jour les durées configurées du Blind Test."""
        self._configured_countdown = countdown_seconds
        self._configured_reveal = reveal_seconds
        if fade_seconds is not None:
            self._configured_fade = fade_seconds
        self._countdown_remain = countdown_seconds
        self._reveal_remain = reveal_seconds
        self._total_round_duration = countdown_seconds + reveal_seconds
        self._fade_duration = float(self._configured_fade)

    def _update_session_progress(self) -> None:
        """Calcule et affiche la progression de la session : 'Extrait x / y — reste z minutes'."""
        if not hasattr(self, "lbl_session_progress"):
            return

        playlist = getattr(self.player, "playlist", None)
        total_tracks = len(playlist) if isinstance(playlist, (list, tuple)) else 0
        if total_tracks == 0:
            self.lbl_session_progress.setText(tr("blind_test.session_empty"))
            return

        cur_idx = getattr(self.player, "current_index", 0)
        if not isinstance(cur_idx, int) or cur_idx < 0:
            cur_idx = 0
        current_track_num = cur_idx + 1

        # Temps restant dans la manche actuelle
        current_round_remain = max(0, self._total_round_duration - self._current_round_elapsed)
        future_tracks = max(0, total_tracks - current_track_num)
        total_remain_sec = current_round_remain + (future_tracks * self._total_round_duration)

        if total_remain_sec >= 90:
            mins = max(1, round(total_remain_sec / 60))
            remain_str = tr("blind_test.minutes_plural", count=mins)
        elif total_remain_sec >= 45:
            remain_str = tr("blind_test.minutes_singular")
        elif total_remain_sec > 0:
            remain_str = tr("blind_test.less_than_minute")
        else:
            remain_str = tr("blind_test.less_than_minute")

        text = tr("blind_test.session_progress", current=current_track_num, total=total_tracks, remain=remain_str)
        self.lbl_session_progress.setText(text)

    def _preload_next_track(self) -> None:
        """Précharge en tâche de fond le prochain fichier de la playlist sur le lecteur standby et sa pochette en RAM."""
        if not hasattr(self.player, "get_next_index"):
            return
        next_idx = self.player.get_next_index()
        if isinstance(next_idx, int) and next_idx != self.player.current_index:
            if hasattr(self.player, "preload_track"):
                self.player.preload_track(next_idx)
            # Précharger également la pochette du morceau suivant dans le cache mémoire pour affichage instantané
            playlist = getattr(self.player, "playlist", None)
            if isinstance(playlist, (list, tuple)) and 0 <= next_idx < len(playlist):
                next_track = playlist[next_idx]
                load_cover_async(next_track, size=280, radius=16)

    def _start_round_for_track(self, track: TrackRecord | None, auto_play: bool = False) -> None:
        """Initialise une manche de Blind Test sur la piste fournie, démarrant à 0 seconde."""
        if not track:
            self._reset_to_empty_state()
            return

        self._stop_fade_out()
        self._stop_fade_in()
        self._nominal_volume = getattr(self.player, "volume", 100)
        self._countdown_remain = self._configured_countdown
        self._reveal_remain = self._configured_reveal
        self._fade_duration = float(self._configured_fade)
        self._total_round_duration = self._countdown_remain + self._reveal_remain
        self._current_round_elapsed = 0

        self._state = "countdown"
        self.lbl_countdown.setVisible(True)
        self.lbl_countdown.show_number(self._countdown_remain)

        # Pochette masquée
        self.cover_opacity.setEnabled(True)
        self.cover_opacity.setOpacity(0.0)
        self.cover_box.setStyleSheet("""
            QFrame {
                background-color: #12151B;
                border: 2px dashed rgba(56, 189, 248, 0.4);
                border-radius: 16px;
            }
        """)

        # Textes mystère
        self.lbl_title.setText("❓  " + tr("blind_test.mystery_title"))
        self.lbl_artist_album.setText("👥  " + tr("blind_test.mystery_artist"))
        self.lbl_file_name.setText("📁  " + tr("blind_test.mystery_file"))
        self.lbl_file_name.setToolTip("")
        self.lbl_file_name.setVisible(True)

        self.btn_reveal.setEnabled(True)
        if hasattr(self, "btn_prev"):
            self.btn_prev.setEnabled(True)
        self.btn_next.setEnabled(True)
        self.round_progress.setValue(0)

        # Précharger l'image de couverture
        pix = load_cover_async(track, size=280, radius=16, callback=self._on_cover_loaded)
        if pix and not pix.isNull():
            self.lbl_cover.setPixmap(pix)

        # Positionner la lecture impérativement à 0 seconde
        self.player.seek_ratio(0.0)

        # Précharger immédiatement le fichier suivant en mémoire tampon
        self._preload_next_track()
        self._update_session_progress()

        if hasattr(self, "effect_canvas") and self.effect_canvas:
            self.effect_canvas.set_track(track)
            eff_state = "playing" if auto_play else "stopped"
            self.effect_canvas.set_playback_state(eff_state)

        if auto_play:
            self._session_playing = True
            # Démarrer à 0% et monter en fondu progressif de 2 secondes vers 100%
            self._apply_temporary_volume(0)
            if not self.player.is_playing:
                self.player.play()
            self.player.seek_ratio(0.0)
            self._start_fade_in(2.0)
            self.btn_play_pause.setText("⏸")
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
            if self._is_active_page:
                self._game_timer.start(1000)
        else:
            self._session_playing = False
            self._game_timer.stop()
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

    def _restart_current_round(self) -> None:
        """Remet à zéro la manche courante du Blind Test avec fondu entrant de 2s."""
        self._stop_fade_out()
        self._stop_fade_in()
        self._current_round_elapsed = 0
        self._countdown_remain = self._configured_countdown
        self._reveal_remain = self._configured_reveal
        self._state = "countdown"
        self.round_progress.setValue(0)
        self.lbl_countdown.setVisible(True)
        self.lbl_countdown.show_number(self._countdown_remain)
        self.cover_opacity.setEnabled(True)
        self.cover_opacity.setOpacity(0.0)
        self.cover_box.setStyleSheet("""
            QFrame {
                background-color: #12151B;
                border: 2px dashed rgba(56, 189, 248, 0.4);
                border-radius: 16px;
            }
        """)
        self.lbl_title.setText("❓  " + tr("blind_test.mystery_title"))
        self.lbl_artist_album.setText("👥  " + tr("blind_test.mystery_artist"))
        self.lbl_file_name.setText("📁  " + tr("blind_test.mystery_file"))
        self.lbl_file_name.setToolTip("")
        self.lbl_file_name.setVisible(True)
        self.btn_reveal.setEnabled(True)
        self.player.seek_ratio(0.0)
        self._preload_next_track()
        self._update_session_progress()

        self._session_playing = True
        if hasattr(self, "effect_canvas") and self.effect_canvas:
            self.effect_canvas.set_playback_state("playing")
        self._apply_temporary_volume(0)
        if not self.player.is_playing:
            self.player.play()
        self.player.seek_ratio(0.0)
        self._start_fade_in(2.0)
        self.btn_play_pause.setText("⏸")
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
        if self._is_active_page:
            self._game_timer.start(1000)

    def _on_cover_loaded(self, target_path: str, pix: QPixmap | None) -> None:
        if not pix or pix.isNull():
            pix = get_default_cover_pixmap(280, 16)
        scaled = pix.scaled(
            280,
            280,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.lbl_cover.setPixmap(scaled)

    def _on_game_tick(self) -> None:
        """Tic régulier de 1 seconde pour animer le décompte et orchestrer la révélation."""
        if not self._is_active_page or not self.player.is_playing:
            return

        self._current_round_elapsed += 1
        pct = min(100, int((self._current_round_elapsed / max(1, self._total_round_duration)) * 100))
        self.round_progress.setValue(pct)
        self._update_session_progress()

        if self._state == "countdown":
            if self.lbl_status_badge.text() == tr("blind_test.status_paused"):
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
            self._countdown_remain -= 1
            if self._countdown_remain > 0:
                self.lbl_countdown.setText(str(self._countdown_remain))
                self.lbl_countdown.trigger_tick_animation()
            else:
                self._trigger_reveal()

        elif self._state == "revealed":
            self._reveal_remain -= 1
            if self._reveal_remain > 0:
                self.lbl_status_badge.setText(tr("blind_test.status_revealed", remain=self._reveal_remain))
                # Vérifier et appliquer le fondu sonore si on est dans la période finale
                eff_fade = min(self._configured_fade, self._configured_reveal)
                if eff_fade > 0 and self._reveal_remain <= eff_fade:
                    if not self._is_fading:
                        self._start_fade(eff_fade)
                    fraction = max(0.0, float(self._reveal_remain) / max(1, eff_fade))
                    target_vol = max(0, int(round(self._nominal_volume * fraction)))
                    self._apply_temporary_volume(target_vol)
            else:
                # Fin de la phase de découverte : extinction propre et passage automatique au suivant !
                self._game_timer.stop()
                self._stop_fade_out()
                # S'assurer que le morceau en cours s'éteint complètement à 0% sans rebond sonore
                self._apply_temporary_volume(0)
                self._session_playing = True
                playlist = getattr(self.player, "playlist", None)
                total = len(playlist) if isinstance(playlist, (list, tuple)) else 0
                cur = getattr(self.player, "current_index", 0)
                if isinstance(cur, int) and total > 0 and cur + 1 >= total:
                    self.player.play_index(0)
                else:
                    self.player.next()

    def _trigger_reveal(self) -> None:
        """Déclenche l'animation de révélation (Fade-In de la pochette et textes)."""
        self._state = "revealed"
        self.lbl_countdown.setVisible(False)
        self.btn_reveal.setEnabled(False)

        # Repositionner au début de la phase de découverte (10s restantes par défaut)
        self._countdown_remain = 0
        self._reveal_remain = self._configured_reveal
        self._current_round_elapsed = self._configured_countdown
        pct = min(100, int((self._current_round_elapsed / max(1, self._total_round_duration)) * 100))
        self.round_progress.setValue(pct)

        # Animation fondu de la pochette
        self.cover_opacity.setEnabled(True)
        self.anim_cover = QPropertyAnimation(self.cover_opacity, b"opacity", self)
        self.anim_cover.setDuration(450)
        self.anim_cover.setStartValue(0.0)
        self.anim_cover.setEndValue(1.0)
        self.anim_cover.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim_cover.finished.connect(self._on_cover_fade_in_finished)
        self.anim_cover.start()

        self.cover_box.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: 2px solid rgba(56, 189, 248, 0.4);
                border-radius: 16px;
            }
        """)

        # Révélation des vrais titres, artistes et nom de fichier
        track = self.player.current_track
        if track:
            title_str = track.title or track.file_name or tr("track.untitled")
            art_str = track.artist or tr("track.unknown_artist")
            if track.album:
                art_str += f" — {track.album}"
            self.lbl_title.setText(title_str)
            self.lbl_artist_album.setText(art_str)
            file_name_text = track.file_name or (
                os.path.basename(track.source_path.replace("\\", "/")) if track.source_path else ""
            )
            if file_name_text:
                self.lbl_file_name.setText(file_name_text)
                self.lbl_file_name.setToolTip(file_name_text)
                self.lbl_file_name.setVisible(True)
            else:
                self.lbl_file_name.setVisible(False)

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

        # Précharger immédiatement la piste suivante en tâche de fond sur standby
        self._preload_next_track()

        # Si le fondu configuré est supérieur ou égal au temps de découverte restant, lancer le fondu
        eff_fade = min(self._configured_fade, self._configured_reveal)
        if eff_fade >= self._reveal_remain and eff_fade > 0 and not self._is_fading:
            self._start_fade(eff_fade)

    def _on_cover_fade_in_finished(self) -> None:
        """Désactive l'effet d'opacité une fois le fondu terminé pour éviter tout glitch de décalage ou de cache lors du redimensionnement."""
        if hasattr(self, "cover_opacity") and self.cover_opacity:
            self.cover_opacity.setOpacity(1.0)
            self.cover_opacity.setEnabled(False)
        if hasattr(self, "lbl_cover") and self.lbl_cover:
            self.lbl_cover.update()

    def _on_reveal_clicked(self) -> None:
        """Révèle immédiatement la piste si les joueurs ont trouvé avant la fin des 20s.
        Garantit qu'il reste la durée complète de découverte (10s par défaut)."""
        if self._state == "countdown":
            self._trigger_reveal()

    def _on_prev_track_clicked(self) -> None:
        """Revient à 0 d'abord si la manche a déjà démarré (> 2s ou révélée),
        ou passe réellement au morceau précédent si au tout début.
        Si on est au premier morceau (index 0) et qu'on ne boucle pas, redémarre la manche 0."""
        self._session_playing = True

        repeat_all = getattr(self.player, "repeat_mode", None) == RepeatMode.ALL
        cur_idx = getattr(self.player, "current_index", 0)
        is_first_track = isinstance(cur_idx, int) and cur_idx <= 0 and not repeat_all

        if self._current_round_elapsed > 2 or self._state == "revealed" or is_first_track:
            self._restart_current_round()
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

            self.player.play()

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
        if self._is_active_page:
            auto_play = self._session_playing or self.player.is_playing
            self._start_round_for_track(track, auto_play=auto_play)

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

    @property
    def countdown_label(self) -> ZoomFadeLabel:
        return self.lbl_countdown

    @property
    def btn_previous(self) -> QPushButton:
        return self.btn_prev

    @property
    def cover_label(self) -> QLabel:
        return self.lbl_cover

    @property
    def lbl_header_title(self) -> QLabel:
        return self.lbl_page_title

    @property
    def cover_opacity_effect(self) -> QGraphicsOpacityEffect:
        return self.cover_opacity

    @property
    def session_progress_label(self) -> QLabel:
        return self.lbl_session_progress

    @property
    def file_name_label(self) -> QLabel:
        return self.lbl_file_name

    @property
    def _is_revealed(self) -> bool:
        return self._state == "revealed"

    @property
    def _countdown_duration(self) -> int:
        return self._countdown_remain

    @property
    def _reveal_duration(self) -> int:
        return self._reveal_remain

    @property
    def _fade_duration_prop(self) -> int:
        return self._configured_fade

    @property
    def _is_fade_active(self) -> bool:
        return self._is_fading

    @property
    def _remaining_seconds(self) -> int:
        return self._countdown_remain if self._state == "countdown" else self._reveal_remain

    @_remaining_seconds.setter
    def _remaining_seconds(self, val: int) -> None:
        if self._state == "countdown":
            self._countdown_remain = val
        else:
            self._reveal_remain = val

    def _on_track_loaded(self, track: TrackRecord | None) -> None:
        self._start_round_for_track(track, auto_play=self.player.is_playing)

    def _tick(self) -> None:
        self._on_game_tick()

    def _on_state_changed(self, state: str) -> None:
        self._on_playback_state_changed(state)

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
