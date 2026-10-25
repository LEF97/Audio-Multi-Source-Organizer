"""Mixin d'orchestration d'une manche de Blind Test (décompte, révélation, préchargement)."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget

from amso.core.database import TrackRecord
from amso.core.i18n import tr
from amso.ui.views.cover_helper import get_default_cover_pixmap, load_cover_async

if TYPE_CHECKING:
    _MixinBase = QWidget
else:
    _MixinBase = object


class BlindTestRoundMixin(_MixinBase):
    """Logique d'avancement des manches de Blind Test, décompte et animation de découverte."""

    if TYPE_CHECKING:

        def __getattr__(self, name: str) -> Any: ...

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

    def _restart_current_round(self, auto_play: bool = True) -> None:
        """Remet à zéro la manche courante du Blind Test avec fondu entrant si auto_play."""
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

        if auto_play:
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
        else:
            self._session_playing = False
            self.player.pause()
            if hasattr(self, "effect_canvas") and self.effect_canvas:
                self.effect_canvas.set_playback_state("stopped")
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
