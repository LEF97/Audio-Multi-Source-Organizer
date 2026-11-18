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
from PySide6.QtMultimedia import QAudioDevice, QAudioFormat, QAudioSink, QMediaDevices

logger = logging.getLogger(__name__)

# `read_pcm(max_bytes)` → (octets, nombre d'octets de silence ajoutés faute de données)
ReadPcm = Callable[[int], tuple[bytes, int]]

# Un sink en mode pull ne lit que si le périphérique annonce des données disponibles ; la source complète
# elle-même par du silence, elle n'est donc jamais « vide ».
_ALWAYS_AVAILABLE = 1 << 20
_INIT_TIMEOUT_S = 5.0
_SHUTDOWN_TIMEOUT_MS = 3000
AUTO_DEVICE_ID = "auto"


def device_id_hex(device: QAudioDevice) -> str:
    """Retourne un identifiant ASCII stable (hexadécimal) pour un QAudioDevice."""
    return bytes(device.id().data()).hex() if not device.isNull() else ""


def list_audio_output_devices() -> list[tuple[str, str]]:
    """Liste les sorties audio disponibles sous forme de paires (id_hex, libellé)."""
    return [(device_id_hex(dev), dev.description()) for dev in QMediaDevices.audioOutputs() if not dev.isNull()]


def resolve_audio_output_device(device_id: str) -> QAudioDevice:
    """Résout un identifiant ('auto' ou id hex) vers le QAudioDevice correspondant (repli sur défaut)."""
    if device_id and device_id != AUTO_DEVICE_ID:
        for dev in QMediaDevices.audioOutputs():
            if device_id_hex(dev) == device_id:
                return dev
    return QMediaDevices.defaultAudioOutput()


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

    def __init__(
        self,
        audio_format: QAudioFormat,
        buffer_size: int,
        volume: float,
        read_pcm: ReadPcm,
        device_id: str = AUTO_DEVICE_ID,
    ) -> None:
        super().__init__()
        self._format = audio_format
        self._buffer_size = buffer_size
        self._volume = volume
        self._read_pcm = read_pcm
        self._device_id = device_id or AUTO_DEVICE_ID
        self._active_device_id = ""
        self._sink: QAudioSink | None = None
        self._device: PcmPullDevice | None = None
        self._silenced = False
        self._is_started = False
        self._is_paused = False
        self._generation = 0
        self.ready = threading.Event()
        self.created = False

    def _build_sink(self, target: QAudioDevice) -> QAudioSink:
        sink = QAudioSink(target, self._format)
        sink.setBufferSize(self._buffer_size)
        sink.setVolume(0.0 if (self._silenced or self._is_paused) else self._volume)
        return sink

    @Slot()
    def create(self) -> None:
        try:
            target = resolve_audio_output_device(self._device_id)
            if target.isNull():
                logger.warning("Aucun périphérique de sortie audio disponible à l'initialisation.")
                return
            device = PcmPullDevice(self._read_pcm)
            device.open(QIODevice.OpenModeFlag.ReadOnly)
            self._sink = self._build_sink(target)
            self._device = device
            self._active_device_id = device_id_hex(target)
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
        self._is_started = True
        self._is_paused = paused
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
        self._is_paused = True
        if self._sink:
            self._set_silenced(True)
            self._sink.suspend()

    @Slot()
    def resume(self) -> None:
        self._generation += 1
        self._is_paused = False
        if self._sink:
            self._set_silenced(False)
            self._sink.resume()

    @Slot()
    def stop(self) -> None:
        self._generation += 1
        self._is_started = False
        self._is_paused = False
        if self._sink:
            # Un stop() depuis l'état suspendu laisse le tampon interne : reset() le vide avant, sinon la reprise
            # suivante rejoue la fin de l'ancien titre.
            self._set_silenced(True)
            self._sink.reset()
            self._sink.stop()

    @Slot(str)
    def switch_device(self, device_id: str) -> None:
        """Recrée le QAudioSink sur le périphérique demandé sans vider le tampon PCM du moteur."""
        self._device_id = device_id or AUTO_DEVICE_ID
        target = resolve_audio_output_device(self._device_id)
        if target.isNull():
            logger.warning("Aucun périphérique de sortie audio disponible pour la bascule (%s).", self._device_id)
            return
        target_id = device_id_hex(target)
        if self._sink is not None and target_id == self._active_device_id:
            return
        if self._device is None:
            self._device = PcmPullDevice(self._read_pcm)
            self._device.open(QIODevice.OpenModeFlag.ReadOnly)
        if self._sink is not None:
            self._sink.stop()
            self._sink.deleteLater()
            self._sink = None
        try:
            self._sink = self._build_sink(target)
            self._active_device_id = target_id
            self.created = True
            if self._is_started:
                self._sink.start(self._device)
                if self._is_paused:
                    self._sink.suspend()
                else:
                    self._set_silenced(False)
            logger.info("Sortie audio basculée vers : %s", target.description())
        except Exception as exc:
            logger.error("Impossible de basculer la sortie audio vers %s : %s", target.description(), exc)

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

    devices_changed = Signal()

    _create = Signal()
    _start = Signal(bool, int)
    _suspend = Signal()
    _resume = Signal()
    _stop = Signal()
    _flush_suspended = Signal()
    _set_volume = Signal(float)
    _switch_device = Signal(str)

    def __init__(
        self,
        audio_format: QAudioFormat,
        buffer_size: int,
        volume: float,
        read_pcm: ReadPcm,
        device_id: str = AUTO_DEVICE_ID,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._selected_device_id = device_id or AUTO_DEVICE_ID
        self._thread = QThread()
        self._worker = _SinkWorker(audio_format, buffer_size, volume, read_pcm, self._selected_device_id)
        self._worker.moveToThread(self._thread)
        for signal, slot in (
            (self._create, self._worker.create),
            (self._start, self._worker.start),
            (self._suspend, self._worker.suspend),
            (self._resume, self._worker.resume),
            (self._stop, self._worker.stop),
            (self._flush_suspended, self._worker.flush_suspended),
            (self._set_volume, self._worker.set_volume),
            (self._switch_device, self._worker.switch_device),
        ):
            signal.connect(slot)
        self._media_devices = QMediaDevices(self)
        self._media_devices.audioOutputsChanged.connect(self._on_audio_outputs_changed)
        self._finalizer = weakref.finalize(self, _stop_audio_thread, self._thread, self._worker)
        self._thread.start()
        self._create.emit()
        self._worker.ready.wait(_INIT_TIMEOUT_S)

    @property
    def selected_device_id(self) -> str:
        return self._selected_device_id

    @Slot()
    def _on_audio_outputs_changed(self) -> None:
        self._switch_device.emit(self._selected_device_id)
        self.devices_changed.emit()

    def set_device(self, device_id: str) -> None:
        """Sélectionne un périphérique de sortie ('auto' ou id hex) et bascule à chaud."""
        self._selected_device_id = device_id or AUTO_DEVICE_ID
        self._switch_device.emit(self._selected_device_id)

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
