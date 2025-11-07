import os
import threading
import time
from typing import Optional

# Make audio optional so the application can still start when dependencies
# like pygame or pyaudio are not installed on the system. If the optional
# packages are available we use them; otherwise we provide a no-op fallback
# implementation that logs calls but doesn't crash the app.

try:
    import pygame
    _HAS_PYGAME = True
except Exception:
    pygame = None
    _HAS_PYGAME = False

try:
    import pyaudio
    _HAS_PYAUDIO = True
except Exception:
    pyaudio = None
    _HAS_PYAUDIO = False


class MusicPlayer:
    """Simple music player wrapper. If pygame/pyaudio are not available
    this class becomes a safe no-op implementation so imports don't fail.
    """

    def __init__(self, music_file_path: str):
        self.music_file_path = music_file_path
        self.play_music_continuously = False
        self.music_thread: Optional[threading.Thread] = None
        self._enabled = False

        if _HAS_PYGAME and _HAS_PYAUDIO and self.check_audio_devices():
            try:
                # At this point we have checked availability; help type checkers
                # by asserting pygame is not None so static analyzers know mixer
                # attribute exists.
                assert pygame is not None
                pygame.mixer.init()
                self._enabled = True
                print("Audio: pygame+mixer initialized")
            except Exception as e:
                print("Audio init failed:", e)
                self._enabled = False
        else:
            if not _HAS_PYGAME:
                print("Audio disabled: pygame not installed")
            if not _HAS_PYAUDIO:
                print("Audio disabled: pyaudio not installed")
            if _HAS_PYGAME and _HAS_PYAUDIO:
                print("Audio disabled: no audio output device found")

    def check_audio_devices(self) -> bool:
        """Return True if an output audio device exists. If pyaudio is
        unavailable we return False.
        """
        if not _HAS_PYAUDIO:
            return False

        try:
            # help the type checker know pyaudio is present
            assert pyaudio is not None
            p = pyaudio.PyAudio()
            info = p.get_host_api_info_by_index(0)
            # normalize to int for safe iteration (info.get can return str/None)
            num_devices = int(info.get('deviceCount') or 0)

            for i in range(num_devices):
                device_info = p.get_device_info_by_host_api_device_index(0, i)
                # normalize channel count
                max_out = int(device_info.get('maxOutputChannels') or 0)
                if max_out > 0:
                    return True
        except Exception:
            return False

        return False

    def play_music(self):
        """Play music in a loop on a background thread. If audio is not
        enabled this method returns immediately.
        """
        if not self._enabled or not _HAS_PYGAME:
            print("play_music requested but audio is disabled")
            return

        try:
            assert pygame is not None
            pygame.mixer.init()
            self.play_music_continuously = True
            pygame.mixer.music.load(self.music_file_path)

            while self.play_music_continuously:
                pygame.mixer.music.play()

                # Wait for the music to finish playing
                while pygame.mixer.music.get_busy() and self.play_music_continuously:
                    time.sleep(0.2)

                # small pause before repeating
                time.sleep(0.5)
        except Exception as e:
            print("Error while playing music:", e)

    def start_music(self):
        if not self._enabled:
            print("start_music called but audio is disabled")
            return

        if self.music_thread and self.music_thread.is_alive():
            return

        self.music_thread = threading.Thread(target=self.play_music, daemon=True)
        self.music_thread.start()

    def stop_music(self):
        self.play_music_continuously = False

        if not _HAS_PYGAME:
            return

        try:
            # Stop the music gracefully if mixer was initialized
            assert pygame is not None
            pygame.mixer.music.pause()
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception:
            pass

