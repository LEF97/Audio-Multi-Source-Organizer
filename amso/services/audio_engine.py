"""Moteur de streaming audio continu WASAPI / Qt 6.

Fournit une lecture bit-perfect ininterrompue sans réinitialisation
matérielle du périphérique audio :
- Flux unique QAudioSink en mode pull, hébergé dans un thread dédié (voir `audio_output.py`).
- Décodage asynchrone des fichiers locaux ou réseau via QAudioDecoder.
- Enchaînement parfait (Standard avec silence propre, Gapless 0 au sample près,
  Crossfade mathématique à égale puissance).
"""

from __future__ import annotations

import logging
import os
import threading

from PySide6.QtCore import QObject, Signal
from PySide6.QtMultimedia import QAudioFormat

from amso.core.dsp_equalizer import Equalizer10Band
from amso.core.pcm_mixer import StreamingCrossfade, bytes_to_ms, linear_fade, ms_to_bytes
from amso.core.replaygain import apply_gain_pcm, replaygain_db_to_linear
from amso.services.audio_output import SinkOutput
from amso.services.cue_continuation import CueContinuation

logger = logging.getLogger(__name__)

SAMPLE_RATE = 44100
CHANNELS = 2
BYTES_PER_SAMPLE = 2  # Int16
BYTES_PER_FRAME = CHANNELS * BYTES_PER_SAMPLE  # 4 octets par frame stéréo
BUFFER_SIZE_SINK = 32768  # ~185ms de tampon réactif
STALE_OUTPUT_DRAIN_MS = 190  # un peu plus que BUFFER_SIZE_SINK (~185 ms)
CUT_FADE_MS = 10  # micro-fondu à la coupure d'un titre (changement manuel) et à l'entrée du suivant


class ContinuousAudioEngine(QObject):
    """Moteur de lecture audio continue à flux unique (QAudioSink en mode pull)."""

    # Signaux
    position_updated = Signal(int, int, float)  # position_ms, total_ms, ratio
    state_changed = Signal(str)  # "playing", "paused", "stopped"
    track_finished = Signal()  # émis quand la piste active atteint son terme
    crossfade_mixed = Signal()  # émis quand la zone de fondu est entièrement mixée dans le tampon
    cue_track_advanced = Signal(int)  # nombre de pistes CUE franchies dans le flux continu
    output_devices_changed = Signal()
    error_occurred = Signal(str)

    def __init__(self, parent: QObject | None = None, device_id: str = "auto") -> None:
        super().__init__(parent)
        self._device_id: str = device_id or "auto"
        self._format = QAudioFormat()
        self._format.setSampleRate(SAMPLE_RATE)
        self._format.setChannelCount(CHANNELS)
        self._format.setSampleFormat(QAudioFormat.SampleFormat.Int16)

        self._output: SinkOutput | None = None
        self._output_started: bool = False
        self._starved_bytes: int = 0  # silence servi faute de données, une fois la lecture réellement commencée
        self._has_served_data: bool = False
        self._volume: float = 1.0  # 0.0 à 1.0
        self._is_muted: bool = False

        self._is_playing: bool = False
        self._is_paused: bool = False

        # État du streaming
        self._current_pcm: bytearray = bytearray()
        self._cut_tail = bytearray()  # fin fondue du titre coupé, servie avant le tampon du suivant
        self._fade_in_next: bool = False
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
        self._cue = CueContinuation()
        self._eq = Equalizer10Band()
        self._replaygain_enabled: bool = False
        self._track_gain_linear: float = 1.0
        self._playback_rate: float = 1.0

        self._lock = threading.Lock()
        self._init_sink()

    def _init_sink(self) -> bool:
        """Initialise la sortie audio unique (thread audio dédié)."""
        output = SinkOutput(
            self._format,
            BUFFER_SIZE_SINK,
            0.0 if self._is_muted else self._volume,
            self.read_pcm,
            device_id=self._device_id,
        )
        if not output.available:
            output.shutdown()
            self._output = None
            return False
        output.devices_changed.connect(self.output_devices_changed)
        self._output = output
        self._output_started = False
        return True

    def set_output_device(self, device_id: str) -> None:
        """Change le périphérique de sortie audio à chaud ('auto' ou id hex)."""
        self._device_id = device_id or "auto"
        if self._output is not None:
            self._output.set_device(self._device_id)

    @property
    def is_available(self) -> bool:
        return self._output is not None

    @property
    def starved_ms(self) -> float:
        """Durée de silence servie à la carte son faute de données (0 si la lecture n'a jamais manqué de PCM)."""
        return bytes_to_ms(self._starved_bytes)

    def read_pcm(self, max_bytes: int) -> tuple[bytes, int]:
        """Appelé par le thread audio : sert jusqu'à `max_bytes` de PCM, complétés par du silence si le tampon est vide.

        Le silence ne fait pas avancer la position : la lecture reprend exactement où elle s'est interrompue.
        """
        wanted = max_bytes // BYTES_PER_FRAME * BYTES_PER_FRAME
        with self._lock:
            tail = bytes(self._cut_tail[:wanted])
            del self._cut_tail[: len(tail)]
            available = len(self._current_pcm) - self._play_offset
            take = min(wanted - len(tail), available) // BYTES_PER_FRAME * BYTES_PER_FRAME
            chunk = tail + bytes(self._current_pcm[self._play_offset : self._play_offset + take])
            self._play_offset += take
        padded = wanted - len(chunk)
        if chunk:
            self._has_served_data = True
            if self._replaygain_enabled:
                chunk = apply_gain_pcm(chunk, self._track_gain_linear)
            chunk = self._eq.process_pcm(chunk)
        elif padded and self._has_served_data:
            self._starved_bytes += padded
        return (chunk + bytes(padded) if padded else chunk), padded

    def set_equalizer(self, enabled: bool, gains: list[float]) -> None:
        """Configure l'égaliseur logiciel 10 bandes (moteur buffer uniquement)."""
        self._eq.set_gains(gains)
        self._eq.set_enabled(enabled)

    def set_replaygain_enabled(self, enabled: bool) -> None:
        """Active ou désactive l'application du gain ReplayGain sur le flux PCM."""
        self._replaygain_enabled = bool(enabled)

    def set_track_gain_db(self, gain_db: float) -> None:
        """Définit le gain ReplayGain (en dB) de la piste en cours."""
        self._track_gain_linear = replaygain_db_to_linear(gain_db)

    def set_playback_rate(self, rate: float) -> None:
        """Met à jour le facteur d'échelle de la position temporelle selon la vitesse."""
        self._playback_rate = max(0.5, min(2.0, float(rate)))

    def shutdown(self) -> None:
        """Arrête le thread audio (fermeture de l'application)."""
        if self._output is not None:
            self._output.shutdown()

    @property
    def is_playing(self) -> bool:
        return self._is_playing and not self._is_paused

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    @property
    def current_time_ms(self) -> int:
        return self._base_offset_ms + int(
            (self._play_offset / BYTES_PER_FRAME) / (SAMPLE_RATE / 1000.0) * self._playback_rate
        )

    @property
    def total_duration_ms(self) -> int:
        return self._total_duration_ms

    def set_volume(self, vol_percent: int) -> None:
        """Volume de 0 à 100."""
        self._volume = max(0.0, min(1.0, vol_percent / 100.0))
        if self._output and not self._is_muted:
            self._output.set_volume(self._volume)

    def set_muted(self, muted: bool) -> None:
        """Active ou désactive le mode muet."""
        self._is_muted = muted
        if self._output:
            self._output.set_volume(0.0 if muted else self._volume)

    def stop(self, keep_output: bool = False, fade_out: bool = False) -> None:
        """Stoppe la lecture et réinitialise les tampons.

        `keep_output=True` laisse la sortie matérielle ouverte : enchaînement automatique de deux titres, où la fin
        du précédent finit de se jouer et où la session audio ne doit être ni fermée ni recréée.
        `fade_out=True` (changement manuel de titre en pleine lecture, avec `keep_output=True`) termine le titre par un
        micro-fondu au lieu d'une coupure en pleine onde (pop) et fond aussi l'entrée du titre suivant.
        """
        self._is_playing = False
        self._is_paused = False
        if self._output and not keep_output:
            self._output.stop()
            self._output_started = False
            self._has_served_data = False
        with self._lock:
            self._cut_tail = bytearray(self._faded_tail_locked()) if fade_out else bytearray()
            self._fade_in_next = fade_out
            self._current_pcm.clear()
            self._play_offset = 0
            self._base_offset_ms = 0
            self._total_duration_ms = 0
            self._current_file_path = ""
            self._reset_crossfade_locked()
            self._cue.clear()
        self.state_changed.emit("stopped")

    def discard_output_buffer(self) -> None:
        """Vide le tampon interne de la sortie (titre rechargé en pause) sans la fermer à froid pour de bon.

        Suspendu, le sink garde quelques centaines de ms de l'ancien titre, rejouées à la reprise.
        """
        if self._output and self._output_started:
            self._output.flush_suspended()
            self._has_served_data = False

    def _faded_tail_locked(self) -> bytes:
        """Les `CUT_FADE_MS` de PCM suivant la position lue, ramenés à zéro (moins si le tampon est plus court)."""
        start = self._play_offset
        end = min(len(self._current_pcm), start + ms_to_bytes(CUT_FADE_MS))
        return linear_fade(bytes(self._current_pcm[start:end]), rising=False)

    def prepare_output(self, paused: bool = False) -> None:
        """Ouvre la sortie avant l'arrivée du premier bloc décodé : elle joue du silence pendant le décodage.

        Une session WASAPI ouverte à froid sur de l'audio réel accroche le début d'un son tenu ; ouverte pendant la
        latence de décodage (~200 ms), elle est stabilisée quand `play_track` livre le PCM.
        `paused=True` (titre chargé en pause) : ouverte puis suspendue sur du silence, sinon `start` suivi de
        `suspend` laisse passer quelques ms du début du titre.
        """
        if self._output and not self._output_started:
            self._output.start(paused, 0 if paused else STALE_OUTPUT_DRAIN_MS)
            self._output_started = True

    def reset_output(self) -> bool:
        """Ferme puis recrée la session audio (changement de configuration à chaud, jamais entre deux titres).

        `_output` doit rester non nul : `is_available` en dépend, et le lecteur bascule sur le chemin VLC dès qu'il
        est faux, ce qui rend muettes la lecture et le seek du moteur `buffer`.
        """
        self.stop()
        if self._output:
            self._output.shutdown()
        self._output = None
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
        if not self._output:
            if not self._init_sink():
                self.error_occurred.emit("Sortie audio non disponible")
                return False

        with self._lock:
            self._current_file_path = file_path
            if self._fade_in_next:
                self._fade_in_next = False
                fade_bytes = ms_to_bytes(CUT_FADE_MS)
                pcm_data = linear_fade(pcm_data[:fade_bytes], rising=True) + pcm_data[fade_bytes:]
            self._current_pcm = bytearray(pcm_data)
            self._total_duration_ms = duration_ms
            self._base_offset_ms = start_offset_ms
            self._is_feed_complete = False
            self._track_finished_emitted = False
            self._play_offset = 0
            self._reset_crossfade_locked()

        if self._output:
            if not self._output_started:
                self._output.start(start_paused)
                self._output_started = True
            elif start_paused:
                self._output.suspend()
            elif self._is_paused:
                self._output.resume()

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
            self._cue.clear()  # le décodage est relancé : le lecteur réarme les pistes à enchaîner

    def arm_cue_continuation(self, durations_ms: list[int]) -> None:
        """Déclare les pistes CUE que le décodage en cours enchaîne après la piste courante (durées en ms)."""
        with self._lock:
            self._cue.arm(durations_ms)

    @property
    def buffered_ahead_ms(self) -> float:
        """PCM décodé pas encore lu."""
        return bytes_to_ms(len(self._current_pcm) - self._play_offset)

    @property
    def cue_continues(self) -> bool:
        """Vrai si la piste suivante est déjà dans le flux décodé : aucun préchargement ni raccord à faire."""
        return self._cue.active

    def _advance_cue_boundaries(self) -> int:
        """Franchit les frontières de pistes CUE déjà lues ; purge le tampon de la piste terminée (mémoire bornée)."""
        steps = 0
        with self._lock:
            while crossing := self._cue.crossing(self._play_offset, self._total_duration_ms, self._base_offset_ms):
                boundary, next_duration_ms = crossing
                del self._current_pcm[:boundary]
                self._play_offset -= boundary
                self._base_offset_ms = 0
                self._total_duration_ms = next_duration_ms
                self._track_finished_emitted = False
                steps += 1
        return steps

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
        if self._output:
            self._output.suspend()
        self.state_changed.emit("paused")

    def resume(self) -> None:
        """Reprend la lecture en pause."""
        if not self._is_playing or not self._is_paused:
            return
        self._is_paused = False
        if self._output:
            self._output.resume()
        self.state_changed.emit("playing")

    def poll_progress(self) -> None:
        """Publie la position et détecte la fin de piste (la carte son est alimentée par `read_pcm`)."""
        if not self._is_playing or self._is_paused or not self._output_started:
            return

        if steps := self._advance_cue_boundaries():
            self.cue_track_advanced.emit(steps)

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
