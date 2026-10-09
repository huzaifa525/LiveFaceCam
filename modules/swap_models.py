"""Catalogue of face-swap models and on-demand download."""
import os
import threading
import urllib.request
from typing import Callable, Dict, Optional

from modules.paths import MODELS_DIR

HYPERSWAP_URL = "https://huggingface.co/facefusion/models-3.3.0/resolve/main/{name}"

# kind: "inswapper" uses insightface's INSwapper (128px, emap embedding);
#       "hyperswap" is FaceFusion's HyperSwap (256px, plain arcface embedding,
#       outputs its own occlusion-aware mask).
SWAP_MODELS: Dict[str, dict] = {
    "hyperswap_1b_256": {
        "label": "HyperSwap 1B · 256px (recommended)",
        "file": "hyperswap_1b_256.onnx", "kind": "hyperswap", "size": 256,
        "min_bytes": 380_000_000,
    },
    "hyperswap_1a_256": {
        "label": "HyperSwap 1A · 256px",
        "file": "hyperswap_1a_256.onnx", "kind": "hyperswap", "size": 256,
        "min_bytes": 380_000_000,
    },
    "hyperswap_1c_256": {
        "label": "HyperSwap 1C · 256px",
        "file": "hyperswap_1c_256.onnx", "kind": "hyperswap", "size": 256,
        "min_bytes": 380_000_000,
    },
    "inswapper_128": {
        "label": "InSwapper · 128px (classic)",
        "file": "inswapper_128_fp16.onnx", "kind": "inswapper", "size": 128,
        "min_bytes": 250_000_000,
    },
}
DEFAULT_SWAP_MODEL = "hyperswap_1b_256"

_download_lock = threading.Lock()
_downloading: set = set()


def model_path(key: str) -> str:
    return os.path.join(MODELS_DIR, SWAP_MODELS[key]["file"])


def is_available(key: str) -> bool:
    info = SWAP_MODELS.get(key)
    if info is None:
        return False
    path = model_path(key)
    return os.path.isfile(path) and os.path.getsize(path) >= info["min_bytes"]


def download(key: str, on_progress: Optional[Callable[[str], None]] = None) -> bool:
    """Download a HyperSwap model into models/. Blocking; safe to call from a thread."""
    info = SWAP_MODELS[key]
    if info["kind"] != "hyperswap":
        return is_available(key)
    with _download_lock:
        if key in _downloading:
            return False
        _downloading.add(key)
    dest = model_path(key)
    part = dest + ".part"
    try:
        os.makedirs(MODELS_DIR, exist_ok=True)
        req = urllib.request.Request(HYPERSWAP_URL.format(name=info["file"]),
                                     headers={"User-Agent": "LiveFaceCam"})
        with urllib.request.urlopen(req, timeout=30) as resp, open(part, "wb") as out:
            total = int(resp.headers.get("Content-Length") or 0)
            done, last_pct = 0, -1
            while True:
                chunk = resp.read(1 << 20)
                if not chunk:
                    break
                out.write(chunk)
                done += len(chunk)
                pct = int(done * 100 / total) if total else 0
                if on_progress and pct != last_pct and pct % 5 == 0:
                    on_progress(f"Downloading {info['label']}: {pct}%")
                    last_pct = pct
        if os.path.getsize(part) < info["min_bytes"]:
            raise IOError("download incomplete")
        os.replace(part, dest)
        return True
    except Exception as e:
        if on_progress:
            on_progress(f"Could not download {info['label']}: {e}")
        try:
            os.remove(part)
        except OSError:
            pass
        return False
    finally:
        with _download_lock:
            _downloading.discard(key)
