# LiveFaceCam Roadmap

The full backlog: verified bugs, improvements and new features, collected from
the Codex code review, the speed/memory research on an RTX 3050 Laptop (4 GB),
the face-model research and our own testing. Last updated: 2026-10-10.

Status: ✅ done · 🚧 in progress · ⬜ to do

---

## 1. Bugs

| # | Bug | Source | Verified | Severity | Effort | Status |
|---|---|---|---|---|---|---|
| B1 | **App can freeze when switching swap model while a model is loading.** `update_status()` calls `processEvents()` on the UI thread while `get_face_swapper()` holds the non-reentrant `THREAD_LOCK`; a model change re-enters `reset_face_swapper()` and deadlocks. Fix: make model switching lock-free (compare the loaded model key) and stop pumping events from status updates. | Codex | ✅ code | High | M | ⬜ |
| B2 | **Corrupted `switch_states.json` crashes startup** (`[]` → `AttributeError`; unknown `ui_theme` → `KeyError` in the theme button). Fix: validate the whole settings schema before applying. | Codex | ✅ tested | High | S | ⬜ |
| B3 | **`_paste_cache` shared between threads.** Mask and key are published separately; live + file processing at different crop sizes can read the other's mask. Fix: dict keyed cache, return local reference. | Codex | ✅ code | High | S | ⬜ |
| B4 | **Live preview freezes silently on a worker exception** (detector, enhancer, virtual camera); capture keeps running. Fix: catch, report status, set the stop event. | Codex | ✅ code | Medium | S | ⬜ |
| B5 | **Saved Light/Dark theme not applied after restart** (theme applied before settings load; only the button label restores). Fix: load settings before `apply_theme`. | Codex | ✅ tested | Medium | S | ⬜ |
| B6 | **Model download race**: pick model A (downloading), then B; A activates when its download finishes. Fix: selection-generation token, activate on UI thread, serialise saves. | Codex | ✅ code | Medium | S | ⬜ |
| B7 | **"Random AI face" only works once in Live**: same temp filename, live source cache compares path only. Fix: unique filename per fetch or a source revision counter. | Codex | ✅ code | Medium | S | ⬜ |
| B8 | **One failed detail-boost frame turns High/Ultra off globally** for the rest of a video while the UI still shows it. Fix: local fallback per call. | Codex | ✅ code | Medium | S | ⬜ |
| B9 | **A stalled camera can still block the UI briefly**: FPS-probe deadline is checked only after a blocking read. Fix: start capture and probe off the UI thread. | Codex | ✅ code | Medium | M | ⬜ |
| B10 | CUDA-graph session not released on model switch (only when PyTorch is installed). | Codex | code | Low | S | ⬜ |
| B11 | `Setup.bat` shortcut step breaks on install paths containing `'`; `move` failure not propagated. | Codex | code | Low | S | ⬜ |
| — | ~~Photo thumbnail cleared by `setText("")`~~ | Codex | ❌ tested, **not a bug** | — | — | — |

## 2. Improvements (speed & quality)

| # | Improvement | Source | Measured / expected gain | Effort | Status |
|---|---|---|---|---|---|
| I1 | **TensorRT "Turbo mode"**: FP32 TensorRT for the swap model, FP16 TensorRT for detection, engine cache, one-time build screen. | Speed research (measured on RTX 3050) | Swap 41.8 → 21.5 ms (2×), detection 13.2 → 4.2 ms (3×); live ~22 → 30+ fps. Cost: +1–2 GB download, ~4–5 min first build, then ~2 s. | M | ⬜ |
| I2 | **Face tracking between detections** (smooth landmarks, adaptive detection interval, latency telemetry). | Codex | Less jitter on head turns | L | ⬜ |
| I3 | **XSeg occlusion + BiSeNet region masks** (optional). | Codex + model research | Hands/mic/glasses reliably in front | L | ⬜ |
| I4 | **68-point alignment** (2DFAN4 / HRFFA → 5/68 points). | Model research + Codex | Less wobble/misalignment | M | ⬜ |
| I5 | **Auto fast detection** (320px when the face is large). | Speed research | Detection 13 → 5 ms | S | ⬜ |
| I6 | **Benchmark HyperSwap 1A / 1B / 1C and AlphaFace-256**; FaceFusion defaults to 1A. | Codex | Possibly a better default | M | ⬜ |

**Measured traps, do not do:**
- TensorRT `trt_fp16_enable` on the swap model destroys identity (cosine 0.85 → 0.04).
- FP16-converted GFPGAN ruins output (PSNR ~10 dB).
- FP16 conversion of `det_10g` with onnxconverter-common produces an invalid model.
- `prefer_nhwc` makes InSwapper 2× slower (41 → 75 ms); CUDA graphs and conv-algo options gave no gain.

## 3. New features

| # | Feature | Source | Why | Effort | Status |
|---|---|---|---|---|---|
| F1 | **Expression & mouth restoration**: blend the real mouth and eyes back in for natural talking and blinking. | Codex (Rope-Live, VisoMaster) | Lip-sync and expression in calls | L | ✅ |
| F2 | **Enhance-only mode** (enhance a face without swapping). | Upstream issue #1867 | Top community request | S | ⬜ |
| F3 | **CodeFormer enhancer** with fidelity slider (`weight` input is float64). | Model research + Codex | Better photo/video restoration | M | ⬜ |
| F4 | **OBS-missing detector** with install link for the virtual camera. | Issues review | Fewer "camera doesn't work" reports | S | ⬜ |
| F5 | **Model auto-repair**: verify sizes/hashes, re-download corrupt files. | Issues review (#1898, #1628) | Fewer support issues | S | ⬜ |
| F6 | **GPU self-check** with fix-it hints (CUDA/cuDNN DLLs, provider actually loaded). | Issues review | Easier setup | M | ⬜ |
| F7 | **Portable installer, auto-update, rollback.** | Codex (competitors) | Easier distribution | L | ⬜ |
| F8 | **Voice changer / audio routing.** | Codex (Magicam, Akool) | Full live-persona feature | L | ⬜ |
| F9 | **Demo GIF + launch posts** (r/StableDiffusion, Show HN, awesome-lists). | Marketing research | Stars and downloads | S | ⬜ |

## 4. Recommended order
1. Bugs B1–B8 (small, low risk).
2. I1 TensorRT Turbo mode (biggest measured speed win).
3. F2, F4, F5 (quick wins).
4. I2, I3, F1 (big quality upgrades).

## 5. Done so far
- v1.0.0: rebrand, virtual camera, one-click `Setup.bat`, close-up source fix, camera freeze fix, upstream PRs #1928 / #1918, VRAM leak fix.
- v1.1.0: sidebar redesign (Plus Jakarta Sans, Lucide, light/dark), face detail pixel boost, face editing, HD/FHD detection, new icon.
- v1.2.0: HyperSwap 256 default, lazy TensorFlow (−1.7 s, −130 MB RAM), lean CUDA memory (−28% VRAM), ~13 → ~19 fps.
- v1.2.1: live skips detail boost and Poisson blending (5 → 21 fps with heavy settings), face coverage and edge softness for jaw/beard.

- Next release: expression restoration (Real mouth / Real eyes sliders in Face quality, about 10 ms per frame).

## 6. Licences to respect
Our code is AGPL-3.0. Model weights carry their own terms: HyperSwap (ResearchRAIL-MS, research only), InSwapper / ArcFace / AlphaFace / GPEN (non-commercial), CodeFormer (S-Lab, non-commercial), GFPGAN (Apache-2.0), XSeg (GPL-3.0), BiSeNet / 2DFAN4 (MIT). LiveFaceCam stays free and non-commercial.
