"""Utilitaire Windows : réactive la session audio du processus (CoreAudio / WASAPI)."""

from __future__ import annotations

import logging
import sys

logger = logging.getLogger(__name__)


def ensure_windows_audio_session_active() -> None:
    """S'assure sous Windows que la session audio du processus n'est pas mise en sourdine
    ou atténuée par le mélangeur de volume Windows (CoreAudio / WASAPI).

    Corrige le problème où Windows Audio Mixer attenue une nouvelle version ou un nouvel
    exécutable déployé (ex: communications ducking ou ancienne session à 0%).
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes
        from ctypes import POINTER, Structure, byref, c_float, c_int, c_void_p, cast, wintypes

        class GUID(Structure):
            _fields_ = [
                ("Data1", wintypes.DWORD),
                ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD),
                ("Data4", wintypes.BYTE * 8),
            ]

            def __init__(self, d1, d2, d3, d4):
                super().__init__(d1, d2, d3, (wintypes.BYTE * 8)(*d4))

        CLSID_MMDeviceEnumerator = GUID(0xBCDE0395, 0xE52F, 0x467C, [0x8E, 0x3D, 0xC4, 0x57, 0x92, 0x91, 0x69, 0x2E])
        IID_IMMDeviceEnumerator = GUID(0xA95664D2, 0x9614, 0x4F35, [0xA7, 0x46, 0xDE, 0x8D, 0xB6, 0x36, 0x17, 0xE6])
        IID_IAudioSessionManager2 = GUID(0x77AA99A0, 0x1BD6, 0x484F, [0x8B, 0xC7, 0x2C, 0x65, 0x4C, 0x9A, 0x9B, 0x6F])

        ole32 = ctypes.windll.ole32
        ole32.CoInitialize(None)
        enumerator = c_void_p()
        if (
            ole32.CoCreateInstance(
                byref(CLSID_MMDeviceEnumerator), None, 1, byref(IID_IMMDeviceEnumerator), byref(enumerator)
            )
            == 0
        ):
            vtable = cast(enumerator, POINTER(POINTER(c_void_p))).contents
            GetDefaultAudioEndpoint = ctypes.WINFUNCTYPE(c_int, c_void_p, c_int, c_int, POINTER(c_void_p))(vtable[4])
            device = c_void_p()
            if GetDefaultAudioEndpoint(enumerator, 0, 0, byref(device)) == 0:
                dev_vtable = cast(device, POINTER(POINTER(c_void_p))).contents
                Activate = ctypes.WINFUNCTYPE(c_int, c_void_p, POINTER(GUID), c_int, c_void_p, POINTER(c_void_p))(
                    dev_vtable[3]
                )
                session_manager = c_void_p()
                if Activate(device, byref(IID_IAudioSessionManager2), 1, None, byref(session_manager)) == 0:
                    mgr_vtable = cast(session_manager, POINTER(POINTER(c_void_p))).contents
                    GetSimpleAudioVolume = ctypes.WINFUNCTYPE(
                        c_int, c_void_p, c_void_p, wintypes.DWORD, POINTER(c_void_p)
                    )(mgr_vtable[4])
                    simple_vol = c_void_p()
                    if GetSimpleAudioVolume(session_manager, None, 0, byref(simple_vol)) == 0 and simple_vol.value:
                        vol_vtable = cast(simple_vol, POINTER(POINTER(c_void_p))).contents
                        GetMasterVolume = ctypes.WINFUNCTYPE(c_int, c_void_p, POINTER(c_float))(vol_vtable[4])
                        GetMute = ctypes.WINFUNCTYPE(c_int, c_void_p, POINTER(wintypes.BOOL))(vol_vtable[6])
                        SetMasterVolume = ctypes.WINFUNCTYPE(c_int, c_void_p, c_float, c_void_p)(vol_vtable[3])
                        SetMute = ctypes.WINFUNCTYPE(c_int, c_void_p, wintypes.BOOL, c_void_p)(vol_vtable[5])

                        curr_vol = c_float()
                        curr_mute = wintypes.BOOL()
                        GetMasterVolume(simple_vol, byref(curr_vol))
                        GetMute(simple_vol, byref(curr_mute))

                        if curr_mute.value:
                            SetMute(simple_vol, False, None)
                        if curr_vol.value < 0.8:
                            SetMasterVolume(simple_vol, 1.0, None)
    except Exception as exc:
        logger.debug("Vérification audio session Windows non disponible : %s", exc)
