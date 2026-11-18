"""Service Windows ITaskbarList3 (boutons miniature et barre de progression)."""

from __future__ import annotations

import ctypes
import logging
import sys
from dataclasses import dataclass
from enum import IntEnum
from typing import Any

logger = logging.getLogger(__name__)

# Constantes Win32 Taskbar
WM_COMMAND = 0x0111
WM_HOTKEY = 0x0312
WM_APPCOMMAND = 0x0319
THBN_CLICKED = 0x1800

# Touches média globales Win32 (RegisterHotKey / WM_APPCOMMAND)
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3
MOD_NOREPEAT = 0x4000

_APPCOMMAND_MEDIA_NEXTTRACK = 11
_APPCOMMAND_MEDIA_PREVIOUSTRACK = 12
_APPCOMMAND_MEDIA_STOP = 13
_APPCOMMAND_MEDIA_PLAY_PAUSE = 14
_APPCOMMAND_MEDIA_PLAY = 46
_APPCOMMAND_MEDIA_PAUSE = 47

_HOTKEY_PREV_ID = 0xA101
_HOTKEY_PLAY_PAUSE_ID = 0xA102
_HOTKEY_NEXT_ID = 0xA103
_HOTKEY_STOP_ID = 0xA104

_HOTKEY_MAP: dict[int, tuple[int, str]] = {
    _HOTKEY_PREV_ID: (VK_MEDIA_PREV_TRACK, "previous"),
    _HOTKEY_PLAY_PAUSE_ID: (VK_MEDIA_PLAY_PAUSE, "play_pause"),
    _HOTKEY_NEXT_ID: (VK_MEDIA_NEXT_TRACK, "next"),
    _HOTKEY_STOP_ID: (VK_MEDIA_STOP, "stop"),
}

_APPCOMMAND_MAP: dict[int, str] = {
    _APPCOMMAND_MEDIA_PREVIOUSTRACK: "previous",
    _APPCOMMAND_MEDIA_PLAY_PAUSE: "play_pause",
    _APPCOMMAND_MEDIA_NEXTTRACK: "next",
    _APPCOMMAND_MEDIA_STOP: "stop",
    _APPCOMMAND_MEDIA_PLAY: "play",
    _APPCOMMAND_MEDIA_PAUSE: "pause",
}

THB_BITMAP = 0x0001
THB_ICON = 0x0002
THB_TOOLTIP = 0x0004
THB_FLAGS = 0x0008

THBF_ENABLED = 0x0000
THBF_DISABLED = 0x0001
THBF_DISMISSONCLICK = 0x0002
THBF_NOBACKGROUND = 0x0004
THBF_HIDDEN = 0x0008
THBF_NONINTERACTIVE = 0x0010


class TaskbarProgressState(IntEnum):
    """États d'affichage de la barre de progression sur l'icône Windows."""

    NO_PROGRESS = 0x0
    INDETERMINATE = 0x1
    NORMAL = 0x2
    ERROR = 0x4
    PAUSED = 0x8


@dataclass(slots=True)
class ThumbButtonSpec:
    """Description d'un bouton de la miniature Windows."""

    button_id: int
    hicon: int = 0
    tooltip: str = ""
    enabled: bool = True
    hidden: bool = False


if sys.platform == "win32":

    class _GUID(ctypes.Structure):
        _fields_ = [
            ("Data1", ctypes.c_uint32),
            ("Data2", ctypes.c_uint16),
            ("Data3", ctypes.c_uint16),
            ("Data4", ctypes.c_uint8 * 8),
        ]

    class _ThumbButton(ctypes.Structure):
        _fields_ = [
            ("dwMask", ctypes.c_uint32),
            ("iId", ctypes.c_uint32),
            ("iBitmap", ctypes.c_uint32),
            ("hIcon", ctypes.c_void_p),
            ("szTip", ctypes.c_wchar * 260),
            ("dwFlags", ctypes.c_uint32),
        ]

    class _WinMsg(ctypes.Structure):
        _fields_ = [
            ("hwnd", ctypes.c_void_p),
            ("message", ctypes.c_uint),
            ("wParam", ctypes.c_size_t),
            ("lParam", ctypes.c_ssize_t),
            ("time", ctypes.c_ulong),
            ("pt_x", ctypes.c_long),
            ("pt_y", ctypes.c_long),
        ]

    class _IconInfo(ctypes.Structure):
        _fields_ = [
            ("fIcon", ctypes.c_int),
            ("xHotspot", ctypes.c_uint32),
            ("yHotspot", ctypes.c_uint32),
            ("hbmMask", ctypes.c_void_p),
            ("hbmColor", ctypes.c_void_p),
        ]

    _CLSID_TASKBAR_LIST = _GUID(
        0x56FDF344,
        0xFD6D,
        0x11D0,
        (ctypes.c_uint8 * 8)(0x95, 0x8A, 0x00, 0x60, 0x97, 0xC9, 0xA0, 0x90),
    )
    _IID_ITASKBAR_LIST3 = _GUID(
        0xEA1AFB91,
        0x9E28,
        0x4B86,
        (ctypes.c_uint8 * 8)(0x90, 0xE9, 0x9E, 0x9F, 0x8A, 0x5E, 0xEF, 0xAF),
    )

    _CLSCTX_INPROC_SERVER = 0x1
    _COINIT_APARTMENTTHREADED = 0x2

    _ole32 = ctypes.windll.ole32
    _user32 = ctypes.windll.user32
    _gdi32 = ctypes.windll.gdi32

    # Typage explicite des handles 64 bits pour éviter toute troncature c_int
    _gdi32.CreateBitmap.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p]
    _gdi32.CreateBitmap.restype = ctypes.c_void_p
    _gdi32.DeleteObject.argtypes = [ctypes.c_void_p]
    _gdi32.DeleteObject.restype = ctypes.c_int
    _user32.CreateIconIndirect.argtypes = [ctypes.POINTER(_IconInfo)]
    _user32.CreateIconIndirect.restype = ctypes.c_void_p
    _user32.DestroyIcon.argtypes = [ctypes.c_void_p]
    _user32.DestroyIcon.restype = ctypes.c_int
    _user32.RegisterWindowMessageW.argtypes = [ctypes.c_wchar_p]
    _user32.RegisterWindowMessageW.restype = ctypes.c_uint
    _user32.ChangeWindowMessageFilterEx.argtypes = [
        ctypes.c_void_p,
        ctypes.c_uint,
        ctypes.c_uint,
        ctypes.c_void_p,
    ]
    _user32.ChangeWindowMessageFilterEx.restype = ctypes.c_int
    _user32.RegisterHotKey.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_uint, ctypes.c_uint]
    _user32.RegisterHotKey.restype = ctypes.c_int
    _user32.UnregisterHotKey.argtypes = [ctypes.c_void_p, ctypes.c_int]
    _user32.UnregisterHotKey.restype = ctypes.c_int

    _MSGFLT_ALLOW = 1
    _E_NOTIMPL = -2147467263  # 0x80004001 : retourné par HrInit sur certaines builds Windows 11

    # Indices de la vtable COM ITaskbarList3
    _VTABLE_RELEASE = 2
    _VTABLE_HR_INIT = 3
    _VTABLE_SET_PROGRESS_VALUE = 9
    _VTABLE_SET_PROGRESS_STATE = 10
    _VTABLE_THUMB_BAR_ADD_BUTTONS = 15
    _VTABLE_THUMB_BAR_UPDATE_BUTTONS = 16


def create_hicon_from_bgra(width: int, height: int, bgra_bytes: bytes) -> int:
    """Crée un HICON Win32 depuis un tampon BGRA 32 bits (no-op hors Windows)."""
    if sys.platform != "win32" or width <= 0 or height <= 0 or not bgra_bytes:
        return 0

    hbm_color = _gdi32.CreateBitmap(width, height, 1, 32, bgra_bytes)
    if not hbm_color:
        return 0
    hbm_mask = _gdi32.CreateBitmap(width, height, 1, 1, None)
    if not hbm_mask:
        _gdi32.DeleteObject(hbm_color)
        return 0

    try:
        info = _IconInfo(fIcon=1, xHotspot=0, yHotspot=0, hbmMask=hbm_mask, hbmColor=hbm_color)
        hicon = _user32.CreateIconIndirect(ctypes.byref(info))
        return int(hicon) if hicon else 0
    finally:
        _gdi32.DeleteObject(hbm_color)
        _gdi32.DeleteObject(hbm_mask)


def destroy_hicon(hicon: int) -> None:
    """Libère un HICON Win32 alloué par create_hicon_from_bgra."""
    if sys.platform == "win32" and hicon:
        _user32.DestroyIcon(ctypes.c_void_p(hicon))


class WindowsTaskbarController:
    """Encapsule l'interface COM ITaskbarList3 avec repli no-op hors Windows."""

    def __init__(self) -> None:
        self._com_ptr: Any = None
        self._vtable: Any = None
        self._hwnd: int = 0
        self._buttons_added: bool = False
        self._registered_hotkeys: list[int] = []
        self._taskbar_created_msg: int = 0
        if sys.platform == "win32":
            self._taskbar_created_msg = int(_user32.RegisterWindowMessageW("TaskbarButtonCreated"))

    @property
    def taskbar_created_msg(self) -> int:
        """Identifiant du message Win32 TaskbarButtonCreated (0 hors Windows)."""
        return self._taskbar_created_msg

    @property
    def buttons_added(self) -> bool:
        """Indique si ThumbBarAddButtons a déjà été appelé pour la fenêtre active."""
        return self._buttons_added

    def attach(self, hwnd: int) -> bool:
        """Initialise COM ITaskbarList3 et attache le handle de fenêtre."""
        if sys.platform != "win32" or not hwnd:
            return False

        self._hwnd = int(hwnd)
        if self._taskbar_created_msg:
            _user32.ChangeWindowMessageFilterEx(
                ctypes.c_void_p(self._hwnd),
                self._taskbar_created_msg,
                _MSGFLT_ALLOW,
                None,
            )
            _user32.ChangeWindowMessageFilterEx(
                ctypes.c_void_p(self._hwnd),
                WM_COMMAND,
                _MSGFLT_ALLOW,
                None,
            )
        if self._com_ptr is not None:
            return True

        try:
            _ole32.CoInitializeEx(None, _COINIT_APARTMENTTHREADED)
            ptr = ctypes.c_void_p()
            hr = _ole32.CoCreateInstance(
                ctypes.byref(_CLSID_TASKBAR_LIST),
                None,
                _CLSCTX_INPROC_SERVER,
                ctypes.byref(_IID_ITASKBAR_LIST3),
                ctypes.byref(ptr),
            )
            if hr != 0 or not ptr.value:
                logger.debug("ITaskbarList3 indisponible (HRESULT=0x%08x)", hr & 0xFFFFFFFF)
                return False

            vtable = ctypes.cast(ptr, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p)))[0]
            hr_init = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p)(vtable[_VTABLE_HR_INIT])
            init_res = hr_init(ptr)
            if init_res not in (0, 1, _E_NOTIMPL):
                logger.debug("ITaskbarList3.HrInit a échoué (HRESULT=0x%08x)", init_res & 0xFFFFFFFF)
                self._release_ptr(ptr, vtable)
                return False

            self._com_ptr = ptr
            self._vtable = vtable
            return True
        except OSError as exc:
            logger.debug("Impossible d'initialiser ITaskbarList3 : %s", exc)
            return False

    def _release_ptr(self, ptr: Any, vtable: Any) -> None:
        try:
            release_fn = ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)(vtable[_VTABLE_RELEASE])
            release_fn(ptr)
        except OSError as exc:
            logger.debug("Erreur lors de Release ITaskbarList3 : %s", exc)

    def dispose(self) -> None:
        """Libère les raccourcis média globaux et le pointeur COM ITaskbarList3."""
        self.unregister_media_hotkeys()
        if sys.platform == "win32" and self._com_ptr is not None and self._vtable is not None:
            self._release_ptr(self._com_ptr, self._vtable)
        self._com_ptr = None
        self._vtable = None
        self._buttons_added = False

    def register_media_hotkeys(self, hwnd: int) -> list[str]:
        """Enregistre les touches média clavier globales sous Windows."""
        if sys.platform != "win32" or not hwnd:
            return []
        self._hwnd = int(hwnd)
        registered: list[str] = []
        for hk_id, (vk_code, action_name) in _HOTKEY_MAP.items():
            if hk_id in self._registered_hotkeys:
                registered.append(action_name)
                continue
            ok = _user32.RegisterHotKey(ctypes.c_void_p(self._hwnd), hk_id, MOD_NOREPEAT, vk_code)
            if ok:
                self._registered_hotkeys.append(hk_id)
                registered.append(action_name)
            else:
                logger.debug("RegisterHotKey ignoré pour %s (déjà utilisé par une autre application)", action_name)
        return registered

    def unregister_media_hotkeys(self) -> None:
        """Désenregistre les touches média clavier globales."""
        if sys.platform != "win32" or not self._hwnd:
            self._registered_hotkeys.clear()
            return
        for hk_id in self._registered_hotkeys:
            _user32.UnregisterHotKey(ctypes.c_void_p(self._hwnd), hk_id)
        self._registered_hotkeys.clear()

    def parse_media_command(self, event_type: bytes, message: Any) -> str | None:
        """Extrait une action média ('previous', 'play_pause', 'next', 'stop', 'play', 'pause') de WM_HOTKEY/WM_APPCOMMAND."""
        if sys.platform != "win32" or event_type != b"windows_generic_MSG" or message is None:
            return None
        addr = int(message)
        if not addr:
            return None
        msg = ctypes.cast(addr, ctypes.POINTER(_WinMsg)).contents
        if msg.message == WM_HOTKEY:
            entry = _HOTKEY_MAP.get(int(msg.wParam))
            return entry[1] if entry else None
        if msg.message == WM_APPCOMMAND:
            cmd = (int(msg.lParam) >> 16) & 0x0FFF
            return _APPCOMMAND_MAP.get(cmd)
        return None

    def parse_native_message(self, event_type: bytes, message: Any) -> tuple[bool, int | None]:
        """Analyse un message natif Qt.

        Retourne `(taskbar_created, clicked_button_id)`.
        """
        if sys.platform != "win32" or event_type != b"windows_generic_MSG" or message is None:
            return False, None

        # shiboken6.VoidPtr vaut False en contexte booléen : tester son adresse entière.
        addr = int(message)
        if not addr:
            return False, None

        msg = ctypes.cast(addr, ctypes.POINTER(_WinMsg)).contents
        if self._taskbar_created_msg and msg.message == self._taskbar_created_msg:
            self._buttons_added = False
            return True, None

        if msg.message == WM_COMMAND and ((msg.wParam >> 16) & 0xFFFF) == THBN_CLICKED:
            return False, int(msg.wParam & 0xFFFF)

        return False, None

    def set_thumb_buttons(self, buttons: list[ThumbButtonSpec]) -> bool:
        """Ajoute ou met à jour les boutons de la miniature barre des tâches."""
        if sys.platform != "win32" or self._com_ptr is None or not self._hwnd or not buttons:
            return False

        count = len(buttons)
        arr = (_ThumbButton * count)()
        for idx, spec in enumerate(buttons):
            flags = THBF_ENABLED if spec.enabled else THBF_DISABLED
            if spec.hidden:
                flags |= THBF_HIDDEN
            arr[idx].dwMask = THB_ICON | THB_TOOLTIP | THB_FLAGS
            arr[idx].iId = spec.button_id
            arr[idx].hIcon = ctypes.c_void_p(spec.hicon) if spec.hicon else None
            arr[idx].szTip = spec.tooltip[:259]
            arr[idx].dwFlags = flags

        vtable_idx = _VTABLE_THUMB_BAR_UPDATE_BUTTONS if self._buttons_added else _VTABLE_THUMB_BAR_ADD_BUTTONS
        fn = ctypes.WINFUNCTYPE(
            ctypes.c_long,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.POINTER(_ThumbButton),
        )(self._vtable[vtable_idx])

        hr = fn(self._com_ptr, ctypes.c_void_p(self._hwnd), count, arr)
        if hr == 0:
            self._buttons_added = True
            return True
        logger.warning("ThumbBar*Buttons a échoué (HRESULT=0x%08x, added=%s)", hr & 0xFFFFFFFF, self._buttons_added)
        return False

    def set_progress_state(self, state: TaskbarProgressState) -> bool:
        """Définit l'état visuel de la barre de progression sur l'icône."""
        if sys.platform != "win32" or self._com_ptr is None or not self._hwnd:
            return False

        fn = ctypes.WINFUNCTYPE(
            ctypes.c_long,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_int,
        )(self._vtable[_VTABLE_SET_PROGRESS_STATE])
        hr = fn(self._com_ptr, ctypes.c_void_p(self._hwnd), int(state))
        return hr == 0

    def set_progress_value(self, completed: int, total: int) -> bool:
        """Met à jour la valeur de progression (0..total) sur l'icône."""
        if sys.platform != "win32" or self._com_ptr is None or not self._hwnd:
            return False

        safe_total = max(1, int(total))
        safe_completed = max(0, min(int(completed), safe_total))
        fn = ctypes.WINFUNCTYPE(
            ctypes.c_long,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint64,
            ctypes.c_uint64,
        )(self._vtable[_VTABLE_SET_PROGRESS_VALUE])
        hr = fn(self._com_ptr, ctypes.c_void_p(self._hwnd), safe_completed, safe_total)
        return hr == 0
