"""Mixin de rétrocompatibilité pour les propriétés et accesseurs de tests du Blind Test."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtWidgets import QGraphicsOpacityEffect, QLabel, QPushButton, QWidget

from amso.core.database import TrackRecord
from amso.ui.views.blind_test.zoom_fade_label import ZoomFadeLabel

if TYPE_CHECKING:
    _MixinBase = QWidget
else:
    _MixinBase = object


class BlindTestCompatMixin(_MixinBase):
    """Accesseurs de compatibilité utilisés par la suite de tests et les modules historiques."""

    if TYPE_CHECKING:

        def __getattr__(self, name: str) -> Any: ...

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
