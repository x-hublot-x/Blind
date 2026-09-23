"""Windows Startup Registry helper for autostart functionality."""

import sys
import os
import winreg

APP_REG_NAME = "SamsungEdgeSnipPin"


def get_executable_command() -> str:
    """Returns the full execution command for autostart."""
    # When running as a python script or packaged exe
    python_exe = sys.executable
    if getattr(sys, 'frozen', False):
        return f'"{sys.executable}"'
    
    # Path to main.py
    main_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
    
    # Use pythonw.exe if available to avoid opening a console window on startup
    pythonw = python_exe.replace("python.exe", "pythonw.exe")
    if os.path.exists(pythonw):
        return f'"{pythonw}" "{main_py}"'
    return f'"{python_exe}" "{main_py}"'


def is_autostart_enabled() -> bool:
    """Checks if autostart registry entry exists in HKCU."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ
        )
        val, _ = winreg.QueryValueEx(key, APP_REG_NAME)
        winreg.CloseKey(key)
        return bool(val)
    except FileNotFoundError:
        return False
    except Exception:
        return False


def set_autostart(enable: bool) -> bool:
    """Enables or disables autostart in Windows registry."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        if enable:
            cmd = get_executable_command()
            winreg.SetValueEx(key, APP_REG_NAME, 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(key, APP_REG_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Error setting autostart: {e}")
        return False
