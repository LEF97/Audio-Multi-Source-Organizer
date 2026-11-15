"""Sortie matérielle du moteur `buffer` : un unique QAudioSink en mode pull, hébergé dans son propre thread.

Sous Windows le sink réclame ses données depuis le thread qui l'a créé, par un timer. Hébergé dans le thread
d'interface, il était privé de données dès que ce thread était occupé (déplacement ou redimensionnement de la
fenêtre : jusqu'à 400 ms mesurés pour un tampon de 185 ms) et le son s'altérait. Dans un thread dédié, seul le
verrou du tampon PCM peut le retarder.
"""

from __future__ import annotations

import logging
import threading
import weakref
from collections.abc import Callable

from PySide6.QtCore import QIODevice, QMetaObject, QObject, Qt, QThread, QTimer, Signal, Slot
from PySide6.QtMultimedia import QAudioFormat, QAudioSink, QMediaDevices

logger = logging.getLogger(__name__)

# `read_pcm(max_bytes)` → (octets, nombre d'octets de silence ajoutés faute de données)
ReadPcm = Callable[[int], tuple[bytes, int]]

# Un sink en mode pull ne lit que si le périphérique annonce des données disponibles ; la source complète
# elle-même par du silence, elle n'est donc jamais « vide ».
_ALWAYS_AVAILABLE = 1 << 20
_INIT_TIMEOUT_S = 5.0
_SHUTDOWN_TIMEOUT_MS = 3000


class PcmPullDevice(QIODevice):
    """Périphérique lu par le sink : délègue au tampon PCM du moteur."""

    def __init__(self, read_pcm: ReadPcm) -> None:
        super().__init__()
        self._read_pcm = read_pcm

    def isSequential(self) -> bool:
        return True

    def bytesAvailable(self) -> int:
        return _ALWAYS_AVAILABLE

    def readData(self, maxlen: int) -> bytes:
        return self._read_pcm(maxlen)[0]

    def writeData(self, data: bytes | bytearray | memoryview, size: int = 0, /) -> int:
        return 0


class _SinkWorker(QObject):
    """Vit dans le thread audio : toutes les opérations sur le QAudioSink passent par ses slots."""

    def __init__(self, audio_format: QAudioFormat, buffer_size: int, volume: float, read_pcm: ReadPcm) -> None:
        super().__init__()
        self._format = audio_format
        self._buffer_size = buffer_size
        self._volume = volume
        self._read_pcm = read_pcm
        self._sink: QAudioSink | None = None
        self._device: PcmPullDevice | None = None
        self._silenced = False
        self._generation = 0
        self.ready = threading.Event()
        self.created = False

    @Slot()
    def create(self) -> None:
        try:
            sink = QAudioSink(QMediaDevices.defaultAudioOutput(), self._format)
            sink.setBufferSize(self._buffer_size)
            sink.setVolume(self._volume)
            device = PcmPullDevice(self._read_pcm)
            device.open(QIODevice.OpenModeFlag.ReadOnly)
            self._sink, self._device = sink, device
            self.created = True
        except Exception as exc:
            logger.error("Impossible d'initialiser QAudioSink : %s", exc)
        finally:
            self.ready.set()

    def _state(self) -> str:
        return self._sink.state().name if self._sink else "aucun"

    def _set_silenced(self, silenced: bool) -> None:
        # Volume de session à 0 tant que rien ne joue : test d'écoute des claquements aux démarrages/coupures du sink.
        self._silenced = silenced
        if self._sink:
            self._sink.setVolume(0.0 if silenced else self._volume)

    @Slot(bool, int)
    def start(self, paused: bool, drain_ms: int) -> None:
        if self._sink and self._device:
            self._generation += 1
            # Le tampon de la session précédente survit au stop() et se joue à la réouverture : muet le temps qu'il
            # se vide, pendant que le moteur ne sert encore que du silence (latence de décodage).
            self._set_silenced(paused or drain_ms > 0)
            self._sink.start(self._device)
            if paused:
                self._sink.suspend()
            elif drain_ms > 0:
                generation = self._generation
                QTimer.singleShot(drain_ms, lambda: self._end_drain(generation))

    def _end_drain(self, generation: int) -> None:
        if generation == self._generation:
            self._set_silenced(False)

    @Slot()
    def suspend(self) -> None:
        self._generation += 1
        if self._sink:
            self._set_silenced(True)
            self._sink.suspend()

    @Slot()
    def resume(self) -> None:
        self._generation += 1
        if self._sink:
            self._set_silenced(False)
            self._sink.resume()

    @Slot()
    def stop(self) -> None:
        self._generation += 1
        if self._sink:
            # Un stop() depuis l'état suspendu laisse le tampon interne : reset() le vide avant, sinon la reprise
            # suivante rejoue la fin de l'ancien titre.
            self._set_silenced(True)
            self._sink.reset()
            self._sink.stop()

    @Slot()
    def flush_suspended(self) -> None:
        # Le tampon interne du sink survit à suspend() : le vider impose un stop/start, relancé aussitôt en pause.
        if self._sink and self._device:
            self._set_silenced(True)
            self._sink.reset()
            self._sink.stop()
            self._sink.start(self._device)
            self._sink.suspend()

    @Slot(float)
    def set_volume(self, volume: float) -> None:
        self._volume = volume
        if self._sink and not self._silenced:
            self._sink.setVolume(volume)

    @Slot()
    def destroy(self) -> None:
        if self._sink:
            self._sink.stop()
        self._sink = None
        self._device = None


def _stop_audio_thread(thread: QThread, worker: _SinkWorker) -> None:
    """Ferme le sink dans son thread puis le thread. Appelé à la destruction de la façade ou à la sortie de Python.

    Un QThread encore actif à sa destruction fait planter le processus : le finaliseur ne doit pas référencer la
    façade (sinon il ne serait jamais déclenché avant la sortie).
    """
    if thread.isRunning():
        QMetaObject.invokeMethod(worker, "destroy", Qt.ConnectionType.BlockingQueuedConnection)
        thread.quit()
        if not thread.wait(_SHUTDOWN_TIMEOUT_MS):
            logger.warning("Le thread audio ne s'est pas arrêté dans le délai imparti")


class SinkOutput(QObject):
    """Façade utilisable depuis le thread d'interface : les commandes sont postées au thread audio, dans l'ordre."""

    _create = Signal()
    _start = Signal(bool, int)
    _suspend = Signal()
    _resume = Signal()
    _stop = Signal()
    _flush_suspended = Signal()
    _set_volume = Signal(float)

    def __init__(
        self,
        audio_format: QAudioFormat,
        buffer_size: int,
        volume: float,
        read_pcm: ReadPcm,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._thread = QThread()
        self._worker = _SinkWorker(audio_format, buffer_size, volume, read_pcm)
        self._worker.moveToThread(self._thread)
        for signal, slot in (
            (self._create, self._worker.create),
            (self._start, self._worker.start),
            (self._suspend, self._worker.suspend),
            (self._resume, self._worker.resume),
            (self._stop, self._worker.stop),
            (self._flush_suspended, self._worker.flush_suspended),
            (self._set_volume, self._worker.set_volume),
        ):
            signal.connect(slot)
        self._finalizer = weakref.finalize(self, _stop_audio_thread, self._thread, self._worker)
        self._thread.start()
        self._create.emit()
        self._worker.ready.wait(_INIT_TIMEOUT_S)

    @property
    def available(self) -> bool:
        return self._worker.created

    def start(self, paused: bool = False, drain_ms: int = 0) -> None:
        self._start.emit(paused, drain_ms)

    def suspend(self) -> None:
        self._suspend.emit()

    def resume(self) -> None:
        self._resume.emit()

    def stop(self) -> None:
        self._stop.emit()

    def flush_suspended(self) -> None:
        self._flush_suspended.emit()

    def set_volume(self, volume: float) -> None:
        self._set_volume.emit(volume)

    def shutdown(self) -> None:
        """Ferme le sink puis le thread audio ; sans effet si déjà fait."""
        self._finalizer()
