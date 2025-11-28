# utils/helpers.py
import subprocess
import os
import sys
import ctypes
import random

def run_subprocess_no_console(cmd, timeout=30, capture_output=True):
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = 0
    creationflags = subprocess.CREATE_NO_WINDOW

    result = subprocess.run(
        cmd,
        startupinfo=startupinfo,
        creationflags=creationflags,
        stdout=subprocess.PIPE if capture_output else subprocess.DEVNULL,
        stderr=subprocess.PIPE if capture_output else subprocess.DEVNULL,
        stdin=subprocess.PIPE,
        timeout=timeout,
        text=capture_output
    )
    return result

def get_lib_path(filename):
    import sys, os

    if getattr(sys, "_MEIPASS", False):
        # Ejecutando como .exe — usar carpeta temporal
        base_path = sys._MEIPASS
    else:
        # Ejecutando como .py — usar ruta real del proyecto
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, "libs", filename)

def hide_console():
    if sys.platform == "win32":
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 0)
            ctypes.windll.kernel32.CloseHandle(whnd)
def get_random_hacking_text(self):
    hacking_phrases = [
        "Initializing secure connection...",
        "Bypassing security protocols...",
        "Establishing encrypted tunnel...",
        "Decrypting security tokens...",
        "Accessing secure partition...",
        "Verifying cryptographic signatures...",
        "Establishing handshake protocol...",
        "Scanning system vulnerabilities...",
        "Injecting security payload...",
        "Establishing secure shell...",
        "Decrypting firmware keys...",
        "Accessing secure boot chain...",
        "Verifying system integrity...",
        "Establishing secure communication...",
        "Bypassing hardware restrictions..."
    ]
    return random.choice(hacking_phrases)
