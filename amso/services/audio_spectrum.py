"""Service de capture et d'analyse spectrale audio en temps réel pour AMSO.

Capture le flux audio réel sous Windows (WASAPI Loopback) avec calcul
de transformée de Fourier (FFT 1024 points) et découpage logarithmique
en bandes de fréquences (basses, médiums, aigus).

Aucune dépendance externe requise (utilise l'API Core Audio native via ctypes).
Fournit un repli gracieux si indisponible.
"""

from __future__ import annotations

import ctypes
import logging
import math
import sys
import threading
import time
from ctypes import POINTER, Structure, byref, c_float, c_int, c_int64, c_uint64, c_void_p, cast, wintypes

logger = logging.getLogger(__name__)


class AudioSpectrumService:
    """Service de capture audio loopback et d'analyse FFT multi-bandes."""

    _instance: AudioSpectrumService | None = None

    @classmethod
    def get_instance(cls) -> AudioSpectrumService:
        if cls._instance is None:
            cls._instance = AudioSpectrumService()
        return cls._instance

    def __init__(self) -> None:
        self._running: bool = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._is_available: bool = sys.platform == "win32"

        # Taille de la fenêtre FFT (1024 échantillons = ~21.3 ms à 48 kHz)
        self.N: int = 1024
        self._buffer: list[float] = [0.0] * self.N
        self._has_audio: bool = False
        self._peak_envelope: float = 0.15

        # Précalculs FFT pour des performances optimales (< 1 ms par trame)
        bits = int(math.log2(self.N))
        self._rev: list[int] = [0] * self.N
        for i in range(self.N):
            r = 0
            for j in range(bits):
                if (i >> j) & 1:
                    r |= 1 << (bits - 1 - j)
            self._rev[i] = r

        self._twiddles: list[complex] = [math.e ** (-2j * math.pi * k / self.N) for k in range(self.N // 2)]
        self._hann: list[float] = [0.5 - 0.5 * math.cos(2.0 * math.pi * i / self.N) for i in range(self.N)]
        self._cached_bands: dict[tuple[int, int], list[tuple[int, int]]] = {}

    @property
    def is_available(self) -> bool:
        return self._is_available

    def _get_bands(self, num_bars: int, sample_rate: int = 48000) -> list[tuple[int, int]]:
        """Calcule les intervalles de fréquences logarithmiques (35 Hz à 16 kHz)."""
        key = (num_bars, sample_rate)
        if key in self._cached_bands:
            return self._cached_bands[key]

        bin_width = sample_rate / self.N
        f_min = 35.0
        f_max = 16000.0
        bands: list[tuple[int, int]] = []
        for i in range(num_bars):
            flow = f_min * ((f_max / f_min) ** (i / num_bars))
            fhigh = f_min * ((f_max / f_min) ** ((i + 1) / num_bars))
            klow = max(1, int(flow / bin_width))
            khigh = max(klow + 1, int(math.ceil(fhigh / bin_width)))
            bands.append((klow, min(khigh, self.N // 2)))

        self._cached_bands[key] = bands
        return bands

    def start(self) -> None:
        """Démarre la boucle de capture audio en tâche de fond si non active."""
        if not self._is_available or self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._capture_worker,
            name="AMSO_WASAPI_Loopback_Thread",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        """Arrête la capture et libère les ressources audio."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.6)
        self._thread = None
        with self._lock:
            self._buffer = [0.0] * self.N
            self._has_audio = False

    def _capture_worker(self) -> None:
        """Boucle de capture Windows Core Audio (WASAPI Loopback) sans blocage."""
        if sys.platform != "win32":
            return

        ole32 = ctypes.oledll.ole32
        ole32.CoInitialize(None)

        try:

            class GUID(Structure):
                _fields_ = [
                    ("Data1", wintypes.DWORD),
                    ("Data2", wintypes.WORD),
                    ("Data3", wintypes.WORD),
                    ("Data4", wintypes.BYTE * 8),
                ]

            CLSID_MMDeviceEnumerator = GUID(
                0xBCDE0395, 0xE52F, 0x467C, (wintypes.BYTE * 8)(0x8E, 0x3D, 0xC4, 0x57, 0x92, 0x91, 0x69, 0x2E)
            )
            IID_IMMDeviceEnumerator = GUID(
                0xA95664D2, 0x9614, 0x4F35, (wintypes.BYTE * 8)(0xA7, 0x46, 0xDE, 0x8D, 0xB6, 0x36, 0x17, 0xE6)
            )
            IID_IAudioClient = GUID(
                0x1CB9AD4C, 0xDBFA, 0x4C32, (wintypes.BYTE * 8)(0xB1, 0x78, 0xC2, 0xF5, 0x68, 0xA7, 0x03, 0xB2)
            )
            IID_IAudioCaptureClient = GUID()
            ole32.IIDFromString("{C8ADBD64-E71E-48A0-A4DE-185C395CD317}", byref(IID_IAudioCaptureClient))

            enumerator = c_void_p()
            hr = ole32.CoCreateInstance(
                byref(CLSID_MMDeviceEnumerator), None, 1, byref(IID_IMMDeviceEnumerator), byref(enumerator)
            )
            if hr != 0:
                logger.debug("WASAPI: CoCreateInstance MMDeviceEnumerator hr=%x", hr)
                return

            vtable_enum = cast(cast(enumerator, POINTER(c_void_p)).contents, POINTER(c_void_p))
            GetDefaultAudioEndpoint = ctypes.WINFUNCTYPE(c_int, c_void_p, c_int, c_int, POINTER(c_void_p))(
                vtable_enum[4]
            )

            device = c_void_p()
            hr = GetDefaultAudioEndpoint(enumerator, 0, 0, byref(device))  # eRender=0, eConsole=0
            if hr != 0 or not device.value:
                return

            vtable_dev = cast(cast(device, POINTER(c_void_p)).contents, POINTER(c_void_p))
            Activate = ctypes.WINFUNCTYPE(c_int, c_void_p, POINTER(GUID), wintypes.DWORD, c_void_p, POINTER(c_void_p))(
                vtable_dev[3]
            )

            audio_client = c_void_p()
            hr = Activate(device, byref(IID_IAudioClient), 7, None, byref(audio_client))
            if hr != 0 or not audio_client.value:
                return

            vtable_ac = cast(cast(audio_client, POINTER(c_void_p)).contents, POINTER(c_void_p))
            GetMixFormat = ctypes.WINFUNCTYPE(c_int, c_void_p, POINTER(c_void_p))(vtable_ac[8])
            pwfx = c_void_p()
            hr = GetMixFormat(audio_client, byref(pwfx))
            if hr != 0 or not pwfx.value:
                return

            # Initialisation du client en mode LOOPBACK partagé
            Initialize = ctypes.WINFUNCTYPE(
                c_int, c_void_p, c_int, wintypes.DWORD, c_int64, c_int64, c_void_p, POINTER(GUID)
            )(vtable_ac[3])
            buffer_duration = 5000000  # 500 ms en unités 100ns
            hr = Initialize(audio_client, 0, 0x00020000, buffer_duration, 0, pwfx, None)
            if hr != 0:
                logger.debug("WASAPI: Initialize loopback hr=%x", hr)
                return

            GetService = ctypes.WINFUNCTYPE(c_int, c_void_p, POINTER(GUID), POINTER(c_void_p))(vtable_ac[14])
            capture_client = c_void_p()
            hr = GetService(audio_client, byref(IID_IAudioCaptureClient), byref(capture_client))
            if hr != 0 or not capture_client.value:
                return

            Start = ctypes.WINFUNCTYPE(c_int, c_void_p)(vtable_ac[10])
            Stop = ctypes.WINFUNCTYPE(c_int, c_void_p)(vtable_ac[11])
            Start(audio_client)

            vtable_cc = cast(cast(capture_client, POINTER(c_void_p)).contents, POINTER(c_void_p))
            GetBuffer = ctypes.WINFUNCTYPE(
                c_int,
                c_void_p,
                POINTER(POINTER(c_float)),
                POINTER(wintypes.UINT),
                POINTER(wintypes.DWORD),
                POINTER(c_uint64),
                POINTER(c_uint64),
            )(vtable_cc[3])
            ReleaseBuffer = ctypes.WINFUNCTYPE(c_int, c_void_p, wintypes.UINT)(vtable_cc[4])
            GetNextPacketSize = ctypes.WINFUNCTYPE(c_int, c_void_p, POINTER(wintypes.UINT))(vtable_cc[5])

            p_data = POINTER(c_float)()
            num_frames = wintypes.UINT()
            flags = wintypes.DWORD()
            pos = c_uint64()
            qpc = c_uint64()
            packet_size = wintypes.UINT()

            ring = [0.0] * self.N

            while self._running:
                hr = GetNextPacketSize(capture_client, byref(packet_size))
                if hr == 0 and packet_size.value > 0:
                    hr = GetBuffer(
                        capture_client, byref(p_data), byref(num_frames), byref(flags), byref(pos), byref(qpc)
                    )
                    if hr == 0:
                        nf = num_frames.value
                        is_silent = bool(flags.value & 1)
                        if nf > 0:
                            if is_silent or not p_data:
                                ring = ring[nf:] + [0.0] * min(nf, self.N)
                                with self._lock:
                                    self._buffer = list(ring[-self.N :])
                                    self._has_audio = False
                            else:
                                step = 1 if nf <= self.N else max(1, nf // self.N)
                                new_samples = []
                                for idx in range(0, nf, step):
                                    mono = (p_data[idx * 2] + p_data[idx * 2 + 1]) * 0.5
                                    new_samples.append(mono)
                                n_add = len(new_samples)
                                ring = ring[n_add:] + new_samples[-self.N :]
                                with self._lock:
                                    self._buffer = list(ring[-self.N :])
                                    self._has_audio = True

                            ReleaseBuffer(capture_client, nf)
                time.sleep(0.015)

            Stop(audio_client)
        except Exception as exc:
            logger.debug("WASAPI Loopback exception: %s", exc)
        finally:
            ole32.CoUninitialize()

    def get_spectrum(self, num_bars: int) -> list[float] | None:
        """Calcule et retourne les niveaux réels du spectre instantané (0.0 à 1.0).

        Retourne None si la capture n'est pas disponible (active le moteur de repli).
        """
        if not self._is_available:
            return None

        # Si le service n'est pas encore lancé, le démarrer à chaud
        if not self._running:
            self.start()

        with self._lock:
            samples = list(self._buffer)
            has_audio = self._has_audio

        if not has_audio:
            # Silence réel : amortit doucement le niveau de crête pour les transitions
            self._peak_envelope = max(0.08, self._peak_envelope * 0.95)
            return [0.0] * num_bars

        # Détection de silence via puissance moyenne (RMS)
        rms_sq = sum(s * s for s in samples) / len(samples)
        if rms_sq < 0.000001:
            self._peak_envelope = max(0.08, self._peak_envelope * 0.95)
            return [0.0] * num_bars

        # 1. Fenêtrage de Hann pour éliminer les fuites spectrales
        hann_samples = [samples[i] * self._hann[i] for i in range(self.N)]

        # 2. FFT itérative rapide O(N log N)
        a: list[complex] = [complex(hann_samples[self._rev[i]]) for i in range(self.N)]
        step = 2
        while step <= self.N:
            half = step // 2
            tw_step = self.N // step
            for group in range(0, self.N, step):
                for k in range(half):
                    u = a[group + k]
                    v = a[group + k + half] * self._twiddles[k * tw_step]
                    a[group + k] = u + v
                    a[group + k + half] = u - v
            step *= 2

        half_n = self.N // 2
        mags = [abs(c) / half_n for c in a[:half_n]]

        # 3. Extraction logarithmique des bandes
        bands = self._get_bands(num_bars, 48000)
        raw_levels = []
        for i, (klow, khigh) in enumerate(bands):
            seg = mags[klow:khigh]
            avg = (sum(seg) / len(seg)) if seg else 0.0
            # Pondération psychoacoustique progressive (+3dB par octave vers les aigus)
            tilt = 1.0 + (i / float(num_bars)) * 2.3
            raw_levels.append(avg * tilt)

        # 4. Contrôle Automatique de Gain (AGC) pour une dynamique vibrante
        max_level = max(raw_levels) if raw_levels else 0.0
        if max_level > self._peak_envelope:
            # Attaque vive
            self._peak_envelope = max_level
        else:
            # Décroissance lente
            self._peak_envelope = max(0.04, self._peak_envelope * 0.985)

        norm_factor = 1.0 / max(0.015, self._peak_envelope)

        levels = []
        for raw in raw_levels:
            scaled = raw * norm_factor
            # Compression logarithmique naturelle style VU-mètre
            comp = math.log10(1.0 + 9.0 * scaled)
            levels.append(max(0.0, min(1.0, comp)))

        return levels


def get_audio_spectrum_service() -> AudioSpectrumService:
    """Fournit l'instance globale du service de spectre audio."""
    return AudioSpectrumService.get_instance()
