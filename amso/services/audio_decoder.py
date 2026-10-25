"""Décodeur audio asynchrone universel basé sur LibVLC (amem) pour ContinuousAudioEngine.

Décode les fichiers locaux ou distants (NAS SMB) directement en mémoire vive
sans passer par la sortie haut-parleur :
- Démarrage instantané dès les premiers échantillons décodés (latence < 100ms).
- Support natif de tous les formats (FLAC, MP3, AAC, OGG, etc.) et des fichiers réseau.
- Repositionnement temporel immédiat (seek) sans saturation mémoire.
"""

from __future__ import annotations

import ctypes
import logging
import os
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, QTimer, Signal

from amso.services.vlc_binding import vlc

logger = logging.getLogger(__name__)

SAMPLE_RATE = 44100
CHANNELS = 2
BYTES_PER_SAMPLE = 2  # Int16
BYTES_PER_FRAME = CHANNELS * BYTES_PER_SAMPLE  # 4 octets


class AsyncAudioDecoder(QObject):
    """Décodeur audio asynchrone alimentant le ContinuousAudioEngine en PCM brut."""

    # Signaux
    ready_to_play = Signal(str, bytes, int)  # file_path, premier bloc pcm, duration_ms
    chunk_decoded = Signal(str, bytes)  # file_path, bloc pcm supplémentaire
    decoding_finished = Signal(str, bytes, int)  # file_path, pcm total, duration_ms
    error_occurred = Signal(str, str)  # file_path, message d'erreur

    def __init__(self, vlc_instance: Any = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._vlc_instance = vlc_instance
        self._player: Any = None
        self._current_path: str = ""
        self._accumulated_pcm = bytearray()
        self._has_emitted_ready: bool = False
        self._is_finished: bool = False
        self._duration_ms: int = 0
        self._min_initial_bytes: int = int(0.2 * SAMPLE_RATE * BYTES_PER_FRAME)  # 200ms
        self._on_play_cb: Any = None
        self._on_end_cb: Any = None
        self._monitor_timer = QTimer(self)
        self._monitor_timer.setInterval(80)
        self._monitor_timer.timeout.connect(self._check_player_state)

    @property
    def is_finished(self) -> bool:
        return self._is_finished

    @property
    def is_decoding(self) -> bool:
        return bool(
            self._player and self._player.get_state() in (vlc.State.Playing, vlc.State.Buffering, vlc.State.Opening)
        )

    def _ensure_player(self) -> bool:
        """Initialise le lecteur VLC configuré en mode décodeur mémoire (amem)."""
        if self._player is not None:
            return True
        if not self._vlc_instance:
            if not vlc.available:
                return False
            self._vlc_instance = vlc.Instance("--no-video", "--quiet")
        if not self._vlc_instance:
            return False

        try:
            self._player = self._vlc_instance.media_player_new()
            self._player.audio_set_format("S16N", SAMPLE_RATE, CHANNELS)

            @vlc.CallbackDecorators.AudioPlayCb
            def _audio_play(opaque: Any, samples: int, count: int, pts: int) -> None:
                num_bytes = count * BYTES_PER_FRAME
                chunk = ctypes.string_at(samples, num_bytes)
                self._handle_pcm_samples(chunk)

            self._on_play_cb = _audio_play
            self._player.audio_set_callbacks(self._on_play_cb, None, None, None, None, None)

            # Écoute de l'événement de fin de flux VLC pour notifier la fin complète du décodage
            em = self._player.event_manager()

            def _on_vlc_end(event: Any) -> None:
                self._on_vlc_end_reached()

            self._on_end_cb = _on_vlc_end
            em.event_attach(vlc.EventType.MediaPlayerEndReached, self._on_end_cb)
            return True
        except Exception as exc:
            logger.error("Erreur d'initialisation du décodeur VLC amem : %s", exc)
            self._player = None
            return False

    def _on_vlc_end_reached(self) -> None:
        """Déclenché lorsque LibVLC a terminé de décoder l'intégralité du flux audio."""
        if self._is_finished or not self._current_path:
            return
        self._is_finished = True
        self._monitor_timer.stop()
        logger.debug("Décodage amem complet pour %s (%d octets)", self._current_path, len(self._accumulated_pcm))
        self.decoding_finished.emit(self._current_path, bytes(self._accumulated_pcm), self._duration_ms)

    def _check_player_state(self) -> None:
        """Vérifie périodiquement l'état du lecteur VLC pour garantir la détection de fin."""
        if not self._player or self._is_finished or not self._has_emitted_ready:
            return
        state = self._player.get_state()
        if state in (vlc.State.Ended, vlc.State.Stopped):
            self._on_vlc_end_reached()

    def _handle_pcm_samples(self, chunk: bytes) -> None:
        """Réceptionne les échantillons PCM décodés depuis le thread audio de VLC."""
        if not chunk or self._is_finished or not self._current_path:
            return
        self._accumulated_pcm.extend(chunk)

        if not self._has_emitted_ready and len(self._accumulated_pcm) >= self._min_initial_bytes:
            self._has_emitted_ready = True
            dur = self._duration_ms
            if dur <= 0 and self._player:
                dur = max(0, self._player.get_length())
                self._duration_ms = dur
            self.ready_to_play.emit(self._current_path, bytes(self._accumulated_pcm), dur)
        elif self._has_emitted_ready:
            self.chunk_decoded.emit(self._current_path, chunk)

    def start_decode(
        self, file_path: str, start_offset_ms: int = 0, duration_ms: int = 0, stop_offset_ms: int = 0, key: str = ""
    ) -> None:
        """Lance le décodage asynchrone du fichier spécifié.

        `stop_offset_ms` (> 0) arrête le décodage à cette position du fichier ; `key` remplace le chemin comme
        identifiant du flux dans les signaux (pistes CUE : plusieurs portions d'un même fichier).
        """
        self.stop()
        if not file_path or not Path(file_path).exists():
            self.error_occurred.emit(file_path, f"Fichier introuvable : {file_path}")
            return

        if not self._ensure_player():
            self.error_occurred.emit(file_path, "Impossible d'initialiser le décodeur audio")
            return

        self._current_path = key or file_path
        self._duration_ms = duration_ms
        self._accumulated_pcm.clear()
        self._has_emitted_ready = False
        self._is_finished = False

        try:
            norm_path = os.path.normpath(file_path)
            media = self._vlc_instance.media_new_path(norm_path)
            media.add_option(":no-video")
            media.add_option(":file-caching=300")
            media.add_option(":network-caching=1000")
            if start_offset_ms > 0:
                media.add_option(f":start-time={start_offset_ms / 1000.0:.2f}")
            if stop_offset_ms > 0:
                media.add_option(f":stop-time={stop_offset_ms / 1000.0:.2f}")

            self._player.set_media(media)
            self._player.play()
            self._monitor_timer.start()
            logger.debug("Décodage amem lancé pour : %s (offset: %d ms)", file_path, start_offset_ms)
        except Exception as exc:
            logger.error("Échec du lancement du décodage pour %s : %s", file_path, exc)
            self.error_occurred.emit(file_path, str(exc))

    def seek_ms(self, target_ms: int) -> None:
        """Repositionne la tête de décodage à la position souhaitée."""
        if self._player and self._player.get_state() in (vlc.State.Playing, vlc.State.Paused):
            try:
                self._player.set_time(target_ms)
            except Exception as exc:
                logger.debug("Erreur seek décodeur : %s", exc)

    def stop(self) -> None:
        """Arrête le décodage en cours."""
        self._is_finished = True
        self._monitor_timer.stop()
        if self._player:
            try:
                self._player.stop()
            except Exception:
                pass
        self._current_path = ""
        self._accumulated_pcm.clear()
        self._has_emitted_ready = False
