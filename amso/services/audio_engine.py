"""Moteur de streaming audio continu WASAPI / Qt 6.

Fournit une lecture bit-perfect ininterrompue sans réinitialisation
matérielle du périphérique audio :
- Flux unique QAudioSink en mode Push.
- Décodage asynchrone des fichiers locaux ou réseau via QAudioDecoder.
- Enchaînement parfait (Standard avec silence propre, Gapless 0 au sample près,
  Crossfade mathématique à égale puissance).
"""

from __future__ import annotations

import array
import logging
import math
import os
import threading

from PySide6.QtCore import QByteArray, QIODevice, QObject, Signal
from PySide6.QtMultimedia import (
    QAudioFormat,
    QAudioSink,
    QMediaDevices,
)

logger = logging.getLogger(__name__)

SAMPLE_RATE = 44100
CHANNELS = 2
BYTES_PER_SAMPLE = 2  # Int16
BYTES_PER_FRAME = CHANNELS * BYTES_PER_SAMPLE  # 4 octets par frame stéréo
BUFFER_SIZE_SINK = 32768  # ~185ms de tampon réactif


class ContinuousAudioEngine(QObject):
    """Moteur de lecture audio continue à flux unique (QAudioSink Push Mode)."""

    # Signaux
    position_updated = Signal(int, int, float)  # position_ms, total_ms, ratio
    state_changed = Signal(str)  # "playing", "paused", "stopped"
    track_finished = Signal()  # émis quand la piste active atteint son terme
    error_occurred = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._format = QAudioFormat()
        self._format.setSampleRate(SAMPLE_RATE)
        self._format.setChannelCount(CHANNELS)
        self._format.setSampleFormat(QAudioFormat.SampleFormat.Int16)

        self._sink: QAudioSink | None = None
        self._audio_io: QIODevice | None = None
        self._volume: float = 1.0  # 0.0 à 1.0
        self._is_muted: bool = False

        self._is_playing: bool = False
        self._is_paused: bool = False

        # État du streaming
        self._current_pcm: bytearray = bytearray()
        self._play_offset: int = 0
        self._base_offset_ms: int = 0
        self._total_duration_ms: int = 0
        self._current_file_path: str = ""
        self._is_feed_complete: bool = False
        self._track_finished_emitted: bool = False
        self._crossfade_next_path: str = ""

        self._lock = threading.Lock()
        self._init_sink()

    def _init_sink(self) -> bool:
        """Initialise la sortie audio unique."""
        try:
            device = QMediaDevices.defaultAudioOutput()
            self._sink = QAudioSink(device, self._format)
            self._sink.setBufferSize(BUFFER_SIZE_SINK)
            self._sink.setVolume(0.0 if self._is_muted else self._volume)
            return True
        except Exception as exc:
            logger.error("Impossible d'initialiser QAudioSink : %s", exc)
            self._sink = None
            return False

    @property
    def is_available(self) -> bool:
        return self._sink is not None

    @property
    def is_playing(self) -> bool:
        return self._is_playing and not self._is_paused

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    @property
    def current_time_ms(self) -> int:
        return self._base_offset_ms + int((self._play_offset / BYTES_PER_FRAME) / (SAMPLE_RATE / 1000.0))

    @property
    def total_duration_ms(self) -> int:
        return self._total_duration_ms

    def set_volume(self, vol_percent: int) -> None:
        """Volume de 0 à 100."""
        self._volume = max(0.0, min(1.0, vol_percent / 100.0))
        if self._sink and not self._is_muted:
            self._sink.setVolume(self._volume)

    def set_muted(self, muted: bool) -> None:
        """Active ou désactive le mode muet."""
        self._is_muted = muted
        if self._sink:
            self._sink.setVolume(0.0 if muted else self._volume)

    def stop(self) -> None:
        """Stoppe la lecture et réinitialise les tampons."""
        self._is_playing = False
        self._is_paused = False
        if self._sink:
            self._sink.stop()
            self._audio_io = None
        with self._lock:
            self._current_pcm.clear()
            self._play_offset = 0
            self._base_offset_ms = 0
            self._total_duration_ms = 0
            self._current_file_path = ""
            self._crossfade_next_path = ""
        self.state_changed.emit("stopped")

    def play_track(
        self,
        file_path: str,
        pcm_data: bytes,
        duration_ms: int,
        start_offset_ms: int = 0,
        start_paused: bool = False,
    ) -> bool:
        """Démarre la lecture immédiate d'une piste à partir de son PCM décodé."""
        if not self._sink:
            if not self._init_sink():
                self.error_occurred.emit("Sortie audio non disponible")
                return False

        with self._lock:
            self._current_file_path = file_path
            self._current_pcm = bytearray(pcm_data)
            self._total_duration_ms = duration_ms
            self._base_offset_ms = start_offset_ms
            self._is_feed_complete = False
            self._track_finished_emitted = False
            self._play_offset = 0

        if self._sink:
            if self._audio_io is None:
                self._audio_io = self._sink.start()
            if start_paused:
                self._sink.suspend()
            elif self._is_paused:
                self._sink.resume()

        self._is_playing = True
        self._is_paused = start_paused
        self.state_changed.emit("paused" if start_paused else "playing")
        return True

    def mark_feed_complete(self, file_path: str) -> None:
        """Indique que tout le fichier a été décodé et transféré dans le buffer."""
        with self._lock:
            if not self._current_file_path or not file_path:
                self._is_feed_complete = True
            elif os.path.normcase(os.path.normpath(file_path)) == os.path.normcase(
                os.path.normpath(self._current_file_path)
            ):
                self._is_feed_complete = True

    def append_chunk(self, file_path: str, chunk_pcm: bytes) -> None:
        """Ajoute un bloc de données PCM décodé en cours de lecture pour la piste courante."""
        if not file_path or not chunk_pcm:
            return
        with self._lock:
            if not self._current_file_path:
                return
            n_file = os.path.normcase(os.path.normpath(file_path))
            n_curr = os.path.normcase(os.path.normpath(self._current_file_path))
            next_p = getattr(self, "_crossfade_next_path", "")
            n_next = os.path.normcase(os.path.normpath(next_p)) if next_p else ""
            if n_file == n_curr or (n_next and n_file == n_next):
                self._current_pcm.extend(chunk_pcm)

    @property
    def is_feed_complete(self) -> bool:
        return self._is_feed_complete

    @property
    def base_offset_ms(self) -> int:
        return self._base_offset_ms

    def reset_buffer_for_seek(self, start_offset_ms: int) -> None:
        """Réinitialise le tampon lors d'un déplacement temporel hors des données décodées."""
        with self._lock:
            self._current_pcm.clear()
            self._play_offset = 0
            self._base_offset_ms = start_offset_ms
            self._is_feed_complete = False
            self._track_finished_emitted = False

    def seek_ms(self, target_ms: int) -> None:
        """Déplace la position de lecture dans le flux audio courant."""
        with self._lock:
            byte_offset = int(((target_ms - self._base_offset_ms) / 1000.0) * SAMPLE_RATE * BYTES_PER_FRAME)
            self._play_offset = max(0, min(byte_offset, len(self._current_pcm)))

    def pause(self) -> None:
        """Met en pause la lecture."""
        if not self._is_playing or self._is_paused:
            return
        self._is_paused = True
        if self._sink:
            self._sink.suspend()
        self.state_changed.emit("paused")

    def resume(self) -> None:
        """Reprend la lecture en pause."""
        if not self._is_playing or not self._is_paused:
            return
        self._is_paused = False
        if self._sink:
            self._sink.resume()
        self.state_changed.emit("playing")

    def pump_audio(self) -> None:
        """Transfère les données du tampon continu vers la carte son."""
        if not self._is_playing or self._is_paused or not self._sink or not self._audio_io:
            return

        free_bytes = self._sink.bytesFree()
        if free_bytes <= 0:
            return

        with self._lock:
            available = len(self._current_pcm) - self._play_offset
            if available > 0:
                chunk_len = min(free_bytes, available)
                chunk = self._current_pcm[self._play_offset : self._play_offset + chunk_len]
                written = self._audio_io.write(QByteArray(chunk))
                if written > 0:
                    self._play_offset += written

        # Calcul de la position courante en ms
        current_ms = self.current_time_ms
        ratio = (current_ms / self._total_duration_ms) if self._total_duration_ms > 0 else 0.0
        self.position_updated.emit(current_ms, self._total_duration_ms, min(1.0, ratio))

        # Vérification si la piste s'est réellement terminée (décodage complet + fin du buffer)
        with self._lock:
            should_emit_finished = (
                self._is_feed_complete
                and not self._track_finished_emitted
                and len(self._current_pcm) > 0
                and self._play_offset >= len(self._current_pcm)
            )
            if should_emit_finished:
                self._track_finished_emitted = True

        if should_emit_finished:
            self.track_finished.emit()

    def append_gapless(self, next_pcm: bytes, total_duration_ms: int, file_path: str = "") -> None:
        """Raccorde immédiatement la piste suivante au sample près (Gapless 0)."""
        with self._lock:
            if self._play_offset > 0:
                del self._current_pcm[: self._play_offset]
                self._play_offset = 0
            self._current_pcm.extend(next_pcm)
            if file_path:
                self._current_file_path = file_path
            self._total_duration_ms = total_duration_ms
            self._base_offset_ms = 0
            self._is_feed_complete = False
            self._track_finished_emitted = False

    def append_with_silence(
        self, next_pcm: bytes, silence_ms: int, total_duration_ms: int, file_path: str = ""
    ) -> None:
        """Raccorde avec un court silence numérique propre (Mode Standard / Pas de fondu)."""
        silence_bytes = int((silence_ms / 1000.0) * SAMPLE_RATE * BYTES_PER_FRAME)
        with self._lock:
            if self._play_offset > 0:
                del self._current_pcm[: self._play_offset]
                self._play_offset = 0
            self._current_pcm.extend(b"\x00" * silence_bytes)
            self._current_pcm.extend(next_pcm)
            if file_path:
                self._current_file_path = file_path
            self._total_duration_ms = total_duration_ms
            self._base_offset_ms = 0
            self._is_feed_complete = False
            self._track_finished_emitted = False

    def append_with_crossfade(
        self, next_pcm: bytes, fade_seconds: float, total_duration_ms: int = 0, file_path: str = ""
    ) -> int:
        """Raccorde avec un fondu croisé mathématique à égale puissance (Crossfade)."""
        fade_frames = int(fade_seconds * SAMPLE_RATE)
        fade_bytes = fade_frames * BYTES_PER_FRAME

        with self._lock:
            avail_end = len(self._current_pcm) - self._play_offset
            actual_fade_bytes = min(fade_bytes, avail_end, len(next_pcm))
            actual_fade_bytes = (actual_fade_bytes // BYTES_PER_FRAME) * BYTES_PER_FRAME
            actual_fade_samples = actual_fade_bytes // BYTES_PER_SAMPLE

            zone_a = bytes(self._current_pcm[self._play_offset : self._play_offset + actual_fade_bytes])
            head_b = bytes(next_pcm[:actual_fade_bytes])
            tail_b = bytes(next_pcm[actual_fade_bytes:])

            if actual_fade_samples > 0:
                arr_a = array.array("h")
                arr_a.frombytes(zone_a)

                arr_b = array.array("h")
                arr_b.frombytes(head_b)

                arr_mixed = array.array("h", [0] * actual_fade_samples)
                num_frames = actual_fade_samples // 2

                for frame_idx in range(num_frames):
                    t = frame_idx / num_frames if num_frames > 0 else 0.0
                    gain_b = math.sin(t * (math.pi / 2.0))
                    gain_a = math.cos(t * (math.pi / 2.0))
                    idx = frame_idx * 2
                    val_l = int(arr_a[idx] * gain_a + arr_b[idx] * gain_b)
                    val_r = int(arr_a[idx + 1] * gain_a + arr_b[idx + 1] * gain_b)
                    arr_mixed[idx] = max(-32768, min(32767, val_l))
                    arr_mixed[idx + 1] = max(-32768, min(32767, val_r))

                mixed_bytes = arr_mixed.tobytes()
            else:
                mixed_bytes = b""

            fade_end = self._play_offset + actual_fade_bytes
            del self._current_pcm[self._play_offset :]
            self._current_pcm.extend(mixed_bytes)
            self._current_pcm.extend(tail_b)

            if file_path:
                self._crossfade_next_path = file_path
            return fade_end

    def finish_crossfade(self, file_path: str, total_duration_ms: int, fade_duration_ms: int) -> None:
        """Finalise le fondu croisé en purgeant les données lues et en recalant le repère temporel."""
        with self._lock:
            if self._play_offset > 0:
                del self._current_pcm[: self._play_offset]
                self._play_offset = 0

            self._current_file_path = file_path
            self._crossfade_next_path = ""
            self._total_duration_ms = total_duration_ms
            self._base_offset_ms = max(0, fade_duration_ms)
            self._is_feed_complete = False
            self._track_finished_emitted = False
