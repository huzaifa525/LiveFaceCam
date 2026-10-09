"""Per-thread runtime state shared by the UI and frame processors.

The live webcam loop marks its worker thread so frame-rate-heavy options
(detail boost, Poisson blending) are skipped there: at 1080p they took the live
preview from ~22 fps to ~5 fps, which froze lip movement and made the face jump
on head turns. They still apply to photo and video conversion.
"""
import threading

_THREAD_MODE = threading.local()


def set_live_thread(live: bool) -> None:
    _THREAD_MODE.live = live


def is_live_thread() -> bool:
    return getattr(_THREAD_MODE, "live", False)
