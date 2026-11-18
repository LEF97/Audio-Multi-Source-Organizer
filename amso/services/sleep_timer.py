"""Minuterie d'arrêt de lecture (Sleep Timer) pour AMSO."""

from __future__ import annotations

from PySide6.QtCore import QObject, QTimer, Signal

SLEEP_TIMER_MODES: dict[str, int] = {
    "off": 0,
    "15m": 15 * 60,
    "30m": 30 * 60,
    "45m": 45 * 60,
    "60m": 60 * 60,
    "end_of_track": 0,
    "end_of_queue": 0,
}


class SleepTimerController(QObject):
    """Gère le compte à rebours ou l'arrêt en fin de piste / file d'attente."""

    changed = Signal(str, int)  # (mode, remaining_seconds)
    triggered = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._mode: str = "off"
        self._remaining_s: int = 0
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._on_tick)

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def remaining_seconds(self) -> int:
        return self._remaining_s

    def set_mode(self, mode: str) -> None:
        normalized = mode if mode in SLEEP_TIMER_MODES else "off"
        self._timer.stop()
        self._mode = normalized
        self._remaining_s = SLEEP_TIMER_MODES[normalized]
        if self._remaining_s > 0:
            self._timer.start()
        self.changed.emit(self._mode, self._remaining_s)

    def on_track_finished(self, queue_ended: bool) -> bool:
        """Retourne True et déclenche l'arrêt si le mode correspond à la fin atteinte."""
        if self._mode == "end_of_track" or (self._mode == "end_of_queue" and queue_ended):
            self._fire()
            return True
        return False

    def _on_tick(self) -> None:
        if self._remaining_s <= 1:
            self._fire()
            return
        self._remaining_s -= 1
        self.changed.emit(self._mode, self._remaining_s)

    def _fire(self) -> None:
        self._timer.stop()
        self._mode = "off"
        self._remaining_s = 0
        self.changed.emit(self._mode, 0)
        self.triggered.emit()
