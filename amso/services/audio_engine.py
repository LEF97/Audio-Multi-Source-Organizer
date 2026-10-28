"""Moteur de streaming audio continu WASAPI / Qt 6.

Fournit une lecture bit-perfect ininterrompue sans réinitialisation
matérielle du périphérique audio :
- Flux unique QAudioSink en mode Push.
- Décodage asynchrone des fichiers locaux ou réseau via QAudioDecoder.
- Enchaînement parfait (Standard avec silence propre, Gapless 0 au sample près,
  Crossfade mathématique à égale puissance).
"""

from __future__ import annotations

import logging
import os
import threading

from PySide6.QtCore import QByteArray, QIODevice, QObject, Signal
from PySide6.QtMultimedia import (
    QAudioFormat,
    QAudioSink,
    QMediaDevices,
)

from amso.core.pcm_mixer import StreamingCrossfade, bytes_to_ms, ms_to_bytes

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
    crossfade_mixed = Signal()  # émis quand la zone de fondu est entièrement mixée dans le tampon
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
        self._xfade: StreamingCrossfade | None = None  # armé dès le préchargement, actif à l'entrée de la zone de fondu
        self._xfade_fade_ms: int = 0
        self._xfade_mixing: bool = False
        self._xfade_end_offset: int | None = None  # fin de la zone mixée dans le tampon, une fois le mixage terminé
        self._xfade_mixed_ms: float = 0.0

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

    def stop(self, keep_output: bool = False) -> None:
        """Stoppe la lecture et réinitialise les tampons.

        `keep_output=True` laisse la sortie matérielle ouverte : enchaînement automatique de deux titres, où la fin
        du précédent finit de se jouer et où la session audio ne doit être ni fermée ni recréée.
        """
        self._is_playing = False
        self._is_paused = False
        if self._sink and not keep_output:
            self._sink.stop()
            self._audio_io = None
        with self._lock:
            self._current_pcm.clear()
            self._play_offset = 0
            self._base_offset_ms = 0
            self._total_duration_ms = 0
            self._current_file_path = ""
            self._reset_crossfade_locked()
        self.state_changed.emit("stopped")

    def reset_output(self) -> bool:
        """Ferme puis recrée la session audio (changement de configuration à chaud, jamais entre deux titres).

        `_sink` doit rester non nul : `is_available` en dépend, et le lecteur bascule sur le chemin VLC dès qu'il
        est faux, ce qui rend muettes la lecture et le seek du moteur `buffer`.
        """
        self.stop()
        if self._sink:
            try:
                self._sink.stop()
            except RuntimeError as exc:
                logger.debug("QAudioSink déjà détruit lors de la réinitialisation : %s", exc)
        self._sink = None
        self._audio_io = None
        return self._init_sink()

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
            self._reset_crossfade_locked()

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
        mixed = False
        with self._lock:
            if not self._current_file_path or not file_path or _same_path(file_path, self._current_file_path):
                if self._xfade is not None:
                    # La piste sortante s'achève avant la fin théorique du fondu (durée des tags approximative)
                    self._finalize_crossfade_locked()
                    mixed = True
                else:
                    self._is_feed_complete = True
        if mixed:
            self.crossfade_mixed.emit()

    def append_chunk(self, file_path: str, chunk_pcm: bytes) -> None:
        """Ajoute un bloc de données PCM décodé en cours de lecture pour la piste courante."""
        if not file_path or not chunk_pcm:
            return
        mixed = False
        with self._lock:
            if not self._current_file_path or not _same_path(file_path, self._current_file_path):
                return
            if self._xfade is None:
                self._current_pcm.extend(chunk_pcm)
            else:
                mixed = self._append_into_crossfade_locked(chunk_pcm)
        if mixed:
            self.crossfade_mixed.emit()

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
            self._reset_crossfade_locked()

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

    # -------------------------------------------------------------------------
    # Fondu croisé au fil du décodage
    # -------------------------------------------------------------------------

    @property
    def is_crossfade_armed(self) -> bool:
        return self._xfade is not None

    @property
    def crossfade_pending(self) -> bool:
        """Un fondu est armé, en cours de mixage, ou mixé et pas encore traversé par la lecture."""
        return self._xfade is not None or self._xfade_end_offset is not None

    def arm_crossfade(self, fade_ms: int, next_path: str) -> None:
        """Prépare le fondu : la zone de `fade_ms` commencera à `durée - fade_ms` de la piste courante."""
        with self._lock:
            self._xfade = StreamingCrossfade(ms_to_bytes(fade_ms))
            self._xfade_fade_ms = fade_ms
            self._xfade_mixing = False
            self._xfade_end_offset = None
            self._crossfade_next_path = next_path

    def feed_crossfade_incoming(self, chunk_pcm: bytes) -> None:
        """Reçoit les blocs décodés de la piste entrante tant que le fondu n'est pas mixé."""
        with self._lock:
            if self._xfade is not None:
                self._xfade.incoming.extend(chunk_pcm)

    def cancel_crossfade(self) -> None:
        """Abandonne un fondu armé ou en cours ; un fondu déjà mixé reste dans le tampon."""
        with self._lock:
            if self._xfade_end_offset is None:
                self._reset_crossfade_locked()

    def crossfade_played_through(self) -> bool:
        """Vrai quand la lecture a traversé toute la zone mixée : la piste entrante devient la piste courante."""
        with self._lock:
            return self._xfade_end_offset is not None and self._play_offset >= self._xfade_end_offset

    def finish_crossfade(self, file_path: str, total_duration_ms: int) -> int:
        """Purge les données lues et recale la position sur la piste entrante ; retourne sa position en ms."""
        with self._lock:
            end = self._xfade_end_offset or 0
            overshoot = max(0, self._play_offset - end)
            if self._play_offset > 0:
                del self._current_pcm[: self._play_offset]
                self._play_offset = 0
            self._current_file_path = file_path
            self._total_duration_ms = total_duration_ms
            self._base_offset_ms = int(self._xfade_mixed_ms + bytes_to_ms(overshoot))
            self._reset_crossfade_locked()
            return self._base_offset_ms

    def _reset_crossfade_locked(self) -> None:
        self._xfade = None
        self._xfade_mixing = False
        self._xfade_end_offset = None
        self._crossfade_next_path = ""

    def _append_into_crossfade_locked(self, chunk: bytes) -> bool:
        """Ajoute un bloc de la piste sortante ; retourne True quand la zone de fondu vient d'être entièrement mixée."""
        xfade = self._xfade
        if xfade is None:
            return False
        if not self._xfade_mixing:
            zone_start = ms_to_bytes(self._total_duration_ms - self._xfade_fade_ms)
            split = zone_start - (ms_to_bytes(self._base_offset_ms) + len(self._current_pcm))
            if split >= len(chunk):
                self._current_pcm.extend(chunk)
                return False
            split = max(0, split) // BYTES_PER_FRAME * BYTES_PER_FRAME
            self._current_pcm.extend(chunk[:split])
            chunk = chunk[split:]
            self._xfade_mixing = True
        mixed, _consumed = xfade.mix_outgoing(bytes(chunk))
        self._current_pcm.extend(mixed)
        if xfade.complete:
            self._finalize_crossfade_locked()
            return True
        return False

    def _finalize_crossfade_locked(self) -> None:
        xfade = self._xfade
        if xfade is None:
            return
        self._xfade_mixed_ms = xfade.mixed_ms
        self._xfade_end_offset = len(self._current_pcm)
        self._current_pcm.extend(xfade.incoming)
        self._current_file_path = self._crossfade_next_path
        self._xfade = None
        self._xfade_mixing = False
        self._is_feed_complete = False
        self._track_finished_emitted = False


def _same_path(left: str, right: str) -> bool:
    return os.path.normcase(os.path.normpath(left)) == os.path.normcase(os.path.normpath(right))
