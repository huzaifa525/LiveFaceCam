"""Send processed live frames to a virtual webcam (OBS Virtual Camera on Windows).

Apps like Teams/Zoom can then pick "OBS Virtual Camera" as their camera.
Requires OBS Studio installed; OBS's own "Start Virtual Camera" must be off.
"""
from typing import Optional

import cv2
import numpy as np

VCAM_WIDTH = 1280
VCAM_HEIGHT = 720
VCAM_FPS = 30


class VirtualCamOutput:
    def __init__(self) -> None:
        self._cam = None
        self._failed = False

    def _open(self) -> bool:
        if self._cam is not None:
            return True
        if self._failed:
            return False
        try:
            import pyvirtualcam

            self._cam = pyvirtualcam.Camera(
                VCAM_WIDTH, VCAM_HEIGHT, VCAM_FPS,
                fmt=pyvirtualcam.PixelFormat.BGR,
            )
            print(f"[DLC.VCAM] Virtual camera started: {self._cam.device}", flush=True)
            return True
        except Exception as e:
            # Don't retry every frame; user can toggle off/on to retry.
            self._failed = True
            print(
                f"[DLC.VCAM] Could not start virtual camera: {e}\n"
                "[DLC.VCAM] Install OBS Studio and make sure OBS's own "
                "'Start Virtual Camera' is stopped.",
                flush=True,
            )
            return False

    def send(self, frame: np.ndarray) -> None:
        if frame is None or not self._open():
            return
        self._cam.send(_letterbox(frame, VCAM_WIDTH, VCAM_HEIGHT))

    def close(self) -> None:
        self._failed = False
        if self._cam is not None:
            try:
                self._cam.close()
            except Exception:
                pass
            self._cam = None
            print("[DLC.VCAM] Virtual camera stopped", flush=True)


def _letterbox(frame: np.ndarray, width: int, height: int) -> np.ndarray:
    h, w = frame.shape[:2]
    if (w, h) == (width, height):
        return frame
    scale = min(width / w, height / h)
    nw, nh = int(w * scale), int(h * scale)
    resized = cv2.resize(frame, (nw, nh), interpolation=cv2.INTER_AREA)
    canvas: Optional[np.ndarray] = np.zeros((height, width, 3), dtype=np.uint8)
    x, y = (width - nw) // 2, (height - nh) // 2
    canvas[y:y + nh, x:x + nw] = resized
    return canvas
