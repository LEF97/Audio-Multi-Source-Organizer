"""Gestion de la playlist, du mode aléatoire et de la répétition (mixin de PlayerService)."""

from __future__ import annotations

import logging
import os
import random
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from amso.core.config import get_config_manager
from amso.core.database import TrackRecord

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from amso.services.player_types import PlayerStateBase

    _MixinBase = PlayerStateBase
else:
    _MixinBase = object


class PlayerQueueMixin(_MixinBase):
    """Gestion de la playlist, du mode aléatoire et de la répétition (mixin de PlayerService)."""

    if TYPE_CHECKING:
        # Les attributs/méthodes de PlayerService sont résolus dynamiquement (typage uniquement)
        def __getattr__(self, name: str) -> Any: ...

    # -------------------------------------------------------------------------
    # Gestion de la Playlist
    # -------------------------------------------------------------------------

    def play_tracks(self, tracks: Sequence[TrackRecord], start_index: int = 0) -> None:
        """Remplace la playlist courante par une nouvelle liste et lance la lecture."""
        if not tracks:
            self.clear_playlist()
            return

        self._playlist = list(tracks)
        valid_index = max(0, min(start_index, len(self._playlist) - 1))

        if self._shuffle:
            self._unshuffled_playlist = list(tracks)
        else:
            self._unshuffled_playlist = None

        self._shuffle_order = list(range(len(self._playlist)))
        self._pending_seek_ms = 0
        self._current_index = -1
        self.play_index(valid_index)
        self.playlist_updated.emit()

    def load_playlist(
        self, tracks: Sequence[TrackRecord], current_index: int = 0, initial_position_ms: int = 0
    ) -> None:
        """Charge une playlist en mémoire sans lancer la lecture automatiquement."""
        if not tracks:
            self.clear_playlist()
            return

        self._playlist = list(tracks)
        self._current_index = max(0, min(current_index, len(self._playlist) - 1))
        self._unshuffled_playlist = list(tracks) if self._shuffle else None
        self._shuffle_order = list(range(len(self._playlist)))
        dur_ms = int((self.current_track.duration_seconds or 0) * 1000) if self.current_track else 0
        clamped_pos_ms = max(0, initial_position_ms)
        if dur_ms > 0 and clamped_pos_ms >= dur_ms:
            clamped_pos_ms = 0

        self._pending_seek_ms = clamped_pos_ms
        self._current_time_ms = clamped_pos_ms

        self.playlist_updated.emit()
        if self.current_track:
            self.track_changed.emit(self.current_track)
            self._total_time_ms = dur_ms
            ratio = min(1.0, max(0.0, self._pending_seek_ms / dur_ms)) if dur_ms > 0 else 0.0
            self.position_changed.emit(self._pending_seek_ms, dur_ms, ratio)

    def play_track_now(self, track: TrackRecord) -> None:
        """Joue immédiatement une piste unique (l'ajoute si nécessaire)."""
        if not track:
            return

        self._pending_seek_ms = 0

        # Si déjà présente, on s'y positionne
        for idx, t in enumerate(self._playlist):
            if (
                t.source_path
                and track.source_path
                and os.path.normcase(t.source_path) == os.path.normcase(track.source_path)
                and t.cue_start_ms == track.cue_start_ms
            ):
                self._current_index = -1
                self.play_index(idx)
                return

        # Sinon on l'insère après la piste courante et on la joue
        insert_pos = self._current_index + 1 if self._current_index >= 0 else 0
        self._playlist.insert(insert_pos, track)
        self._rebuild_shuffle_order()
        self.playlist_updated.emit()
        self._current_index = -1
        self.play_index(insert_pos)

    def insert_next(self, tracks: Sequence[TrackRecord], auto_play: bool = False) -> None:
        """Insère une ou plusieurs pistes juste après la piste en cours de lecture sans forcer la lecture."""
        if not tracks:
            return

        if not self._playlist:
            self._playlist = list(tracks)
            if self._shuffle:
                self._unshuffled_playlist = list(tracks)
            self._current_index = 0
            self._rebuild_shuffle_order()
            self.playlist_updated.emit()
            self.track_changed.emit(self.current_track)
            if auto_play:
                self.play_index(0)
            return

        if self._current_index < 0:
            insert_pos = 0
            for i, t in enumerate(tracks):
                self._playlist.insert(insert_pos + i, t)
            if self._unshuffled_playlist is not None:
                for i, t in enumerate(tracks):
                    self._unshuffled_playlist.insert(insert_pos + i, t)
            self._current_index = 0
            self._rebuild_shuffle_order()
            self.playlist_updated.emit()
            self.track_changed.emit(self.current_track)
            if auto_play:
                self.play_index(0)
            return

        insert_pos = self._current_index + 1
        for i, t in enumerate(tracks):
            self._playlist.insert(insert_pos + i, t)

        if self._unshuffled_playlist is not None:
            cur = self.current_track
            unshuf_pos = len(self._unshuffled_playlist)
            if cur and cur in self._unshuffled_playlist:
                unshuf_pos = self._unshuffled_playlist.index(cur) + 1
            for i, t in enumerate(tracks):
                self._unshuffled_playlist.insert(unshuf_pos + i, t)

        self._rebuild_shuffle_order()
        self.playlist_updated.emit()

    def append_tracks(self, tracks: Sequence[TrackRecord], auto_play: bool = False) -> None:
        """Ajoute des pistes à la fin de la file d'attente sans forcer la lecture."""
        if not tracks:
            return

        was_empty = len(self._playlist) == 0
        self._playlist.extend(tracks)
        if self._unshuffled_playlist is not None:
            self._unshuffled_playlist.extend(tracks)
        elif self._shuffle and was_empty:
            self._unshuffled_playlist = list(self._playlist)
        self._rebuild_shuffle_order()

        if was_empty or self._current_index < 0:
            self._current_index = 0
            self.track_changed.emit(self.current_track)
            if auto_play:
                self.play_index(0)

        self.playlist_updated.emit()

    def remove_at(self, index: int) -> None:
        """Supprime une piste de la playlist à l'index donné."""
        if not (0 <= index < len(self._playlist)):
            return

        track_to_remove = self._playlist[index]
        if self._unshuffled_playlist is not None and track_to_remove in self._unshuffled_playlist:
            try:
                self._unshuffled_playlist.remove(track_to_remove)
            except ValueError:
                pass

        is_current = index == self._current_index
        del self._playlist[index]

        if not self._playlist:
            self.stop()
            self._unshuffled_playlist = None
            self._current_index = -1
            self.playlist_updated.emit()
            self.track_changed.emit(None)
            return

        if index < self._current_index:
            self._current_index -= 1
        elif is_current:
            # On rejoue la nouvelle piste qui a pris cet index (ou la dernière si on était au bout)
            new_idx = min(index, len(self._playlist) - 1)
            self._current_index = -1
            self.play_index(new_idx)

        self._rebuild_shuffle_order()
        self.playlist_updated.emit()

    def clear_playlist(self) -> None:
        """Vide entièrement la playlist et stoppe la lecture."""
        self.stop()
        self._playlist.clear()
        self._unshuffled_playlist = None
        self._shuffle_order.clear()
        self._current_index = -1
        self.playlist_updated.emit()
        self.track_changed.emit(None)

    def shuffle_all_tracks(self) -> None:
        """Mélange l'ensemble complet des titres de la playlist et repositionne l'index de la piste active."""
        if len(self._playlist) <= 1:
            return

        if self._shuffle and self._unshuffled_playlist is None:
            self._unshuffled_playlist = list(self._playlist)

        current_track = self.current_track
        random.shuffle(self._playlist)

        if current_track is not None:
            try:
                for idx, t in enumerate(self._playlist):
                    if t is current_track:
                        self._current_index = idx
                        break
                else:
                    self._current_index = self._playlist.index(current_track)
            except ValueError:
                self._current_index = max(0, min(self._current_index, len(self._playlist) - 1))

        self._shuffle_order = list(range(len(self._playlist)))
        self.playlist_updated.emit()

    def shuffle_playlist(self, below_current: bool = False) -> None:
        """Mélange les pistes de la file d'attente (playlist).

        Si below_current est True et qu'un morceau est en cours de lecture, les morceaux
        situés avant et le morceau en cours restent inchangés, et seuls tous les morceaux
        en dessous sont mélangés aléatoirement.
        Sinon (comportement par défaut), toute la playlist est mélangée et la piste en cours
        peut se retrouver à n'importe quelle position.
        """
        if len(self._playlist) <= 1:
            return

        if below_current and 0 <= self._current_index < len(self._playlist) - 1:
            to_shuffle = self._playlist[self._current_index + 1 :]
            if len(to_shuffle) > 1:
                random.shuffle(to_shuffle)
                self._playlist = self._playlist[: self._current_index + 1] + to_shuffle
            self._shuffle_order = list(range(len(self._playlist)))
            self.playlist_updated.emit()
        else:
            self.shuffle_all_tracks()

    def move_tracks(self, from_rows: list[int], to_row: int) -> None:
        """Déplace un groupe de pistes vers une nouvelle position dans la playlist (Drag & Drop)."""
        if not from_rows or not self._playlist:
            return

        current_track = self.current_track
        from_rows = sorted({r for r in from_rows if 0 <= r < len(self._playlist)})
        if not from_rows:
            return

        moving_tracks = [self._playlist[r] for r in from_rows]
        remaining = [t for i, t in enumerate(self._playlist) if i not in from_rows]

        offset = sum(1 for r in from_rows if r < to_row)
        insert_idx = max(0, min(to_row - offset, len(remaining)))

        remaining[insert_idx:insert_idx] = moving_tracks
        self._playlist = remaining

        if current_track and current_track in self._playlist:
            self._current_index = self._playlist.index(current_track)

        if self._unshuffled_playlist is not None:
            self._unshuffled_playlist = list(self._playlist)

        self._shuffle_order = list(range(len(self._playlist)))
        self.playlist_updated.emit()

    def set_shuffle(self, shuffle: bool) -> None:
        """Définit l'état de lecture aléatoire."""
        if self._shuffle != shuffle:
            self._shuffle = shuffle
            try:
                get_config_manager().set_player_shuffle(self._shuffle)
            except Exception:
                pass

            if self._shuffle:
                # Activation : mémorise l'ordre initial et mélange toute la playlist
                if self._unshuffled_playlist is None:
                    self._unshuffled_playlist = list(self._playlist)
                self.shuffle_all_tracks()
            else:
                # Désactivation : reprend l'ordre des pistes initial
                if self._unshuffled_playlist is not None:
                    current_track = self.current_track
                    self._playlist = list(self._unshuffled_playlist)
                    self._unshuffled_playlist = None
                    if current_track is not None:
                        try:
                            for idx, t in enumerate(self._playlist):
                                if t is current_track:
                                    self._current_index = idx
                                    break
                            else:
                                self._current_index = self._playlist.index(current_track)
                        except ValueError:
                            self._current_index = max(0, min(self._current_index, len(self._playlist) - 1))
                    self._shuffle_order = list(range(len(self._playlist)))
                    self.playlist_updated.emit()

            self.shuffle_changed.emit(self._shuffle)

    def toggle_shuffle(self) -> None:
        """Active ou désactive la lecture aléatoire."""
        self.set_shuffle(not self._shuffle)

    def set_repeat_mode(self, mode: int) -> None:
        """Définit le mode de répétition (RepeatMode.OFF, ALL, ONE)."""
        new_mode = mode % 3
        if self._repeat_mode != new_mode:
            self._repeat_mode = new_mode
            self.repeat_changed.emit(self._repeat_mode)

    def toggle_repeat(self) -> None:
        """Bascule le mode de répétition : OFF -> ALL -> ONE -> OFF."""
        self.set_repeat_mode((self._repeat_mode + 1) % 3)

    def _rebuild_shuffle_order(self) -> None:
        self._shuffle_order = list(range(len(self._playlist)))
