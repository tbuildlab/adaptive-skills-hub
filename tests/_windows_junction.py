"""Create a local Windows junction for hermetic tests without a subprocess."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import struct


def create_junction(link: Path, target: Path) -> None:
    """Make a test-only mount-point reparse entry to an existing local directory."""
    if os.name != "nt":
        raise OSError("Windows junction fixture is unavailable on this platform")
    if link.exists() or not target.is_dir() or target.is_symlink():
        raise OSError("Windows junction fixture paths are invalid")

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    create_file = kernel.CreateFileW
    create_file.argtypes = [
        wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
        wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
    ]
    create_file.restype = wintypes.HANDLE
    device_io_control = kernel.DeviceIoControl
    device_io_control.argtypes = [
        wintypes.HANDLE, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD,
        wintypes.LPVOID, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
        wintypes.LPVOID,
    ]
    device_io_control.restype = wintypes.BOOL
    close_handle = kernel.CloseHandle
    close_handle.argtypes = [wintypes.HANDLE]

    target_path = str(target.resolve(strict=True))
    substitute = ("\\??\\" + target_path).encode("utf-16-le")
    display = target_path.encode("utf-16-le")
    path_buffer = substitute + b"\0\0" + display + b"\0\0"
    payload = struct.pack("<HHHH", 0, len(substitute), len(substitute) + 2, len(display)) + path_buffer
    reparse_data = struct.pack("<IHH", 0xA0000003, len(payload), 0) + payload

    link.mkdir()
    handle = create_file(str(link), 0x40000000, 7, None, 3, 0x02200000, None)
    if handle == wintypes.HANDLE(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        returned = wintypes.DWORD()
        buffer = ctypes.create_string_buffer(reparse_data)
        if not device_io_control(
            handle, 0x000900A4, buffer, len(reparse_data), None, 0,
            ctypes.byref(returned), None,
        ):
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        close_handle(handle)
    if not link.is_junction() or not os.path.samefile(link, target):
        raise OSError("Windows junction fixture was not established")
