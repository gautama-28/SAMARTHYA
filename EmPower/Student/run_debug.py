"""run_debug.py

Small helper to inspect the local Python environment and optional modules
used by this project. Run without arguments to print diagnostics. Use
`--run` to start `main.pyw` with the same interpreter after the checks.

Usage:
    python run_debug.py        # show diagnostics
    python run_debug.py --run  # run the GUI after diagnostics
"""
from __future__ import annotations

import sys
import platform
import subprocess
import traceback
from pathlib import Path


def info(msg: str) -> None:
    print(msg)


def check_import(import_name: str, friendly_name: str | None = None):
    """Attempt to import a module and print basic info. Returns True if import succeeded."""
    name = friendly_name or import_name
    try:
        module = __import__(import_name)
        ver = getattr(module, '__version__', None) or getattr(module, 'version', None)
        if ver is None:
            # some modules expose version differently
            try:
                ver = module.VERSION
            except Exception:
                ver = 'unknown'
        print(f"[OK] {name}: import succeeded, version={ver}")
        return True
    except Exception as e:
        print(f"[MISSING] {name}: import failed: {e.__class__.__name__}: {e}")
        return False


def show_environment():
    print("\n=== Python environment ===")
    print("executable:", sys.executable)
    print("version:", sys.version.replace('\n', ' '))
    print("platform:", platform.platform())
    print("architecture:", platform.architecture())
    print("cwd:", Path.cwd())
    print("is_venv:", sys.prefix != getattr(sys, 'base_prefix', sys.prefix))


def check_requirements():
    print("\n=== Requirements / optional modules ===")

    # modules we want to verify
    checks = [
        ('PyQt5', 'PyQt5'),
        ('pygame', 'pygame'),
        ('pyaudio', 'pyaudio'),
        ('cv2', 'opencv-python (cv2)'),
    ]

    for mod, nice in checks:
        check_import(mod, nice)

    # check Backend.AudioPlayer import specifically
    print('\n=== Project imports ===')
    try:
        import Backend.AudioPlayer as ap
        print('[OK] Backend.AudioPlayer: import succeeded')
    except Exception:
        print('[ERROR] Backend.AudioPlayer: import failed')
        traceback.print_exc()


def run_main():
    """Run main.pyw using the same Python interpreter. This will actually
    start the GUI (if available)."""
    main_path = Path(__file__).parent / 'main.pyw'
    if not main_path.exists():
        print(f"main.pyw not found at {main_path}")
        return 1

    print(f"Launching {main_path} with interpreter: {sys.executable}")
    # Use subprocess so the current diagnostic output is preserved and the
    # GUI runs in a child process.
    try:
        return subprocess.call([sys.executable, str(main_path)])
    except Exception:
        traceback.print_exc()
        return 2


def main():
    show_environment()
    check_requirements()

    if '--run' in sys.argv:
        rc = run_main()
        print(f"main.pyw exited with return code: {rc}")


if __name__ == '__main__':
    main()
