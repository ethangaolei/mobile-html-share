#!/usr/bin/env python3
"""Transcribe MP3s to WebVTT with faster-whisper (local, large-v3, CPU int8).

Usage:
  HF_HUB_OFFLINE=1 python3 scripts/transcribe.py                      # all assets/audio/*.mp3
  HF_HUB_OFFLINE=1 python3 scripts/transcribe.py D4-market-opportunity.mp3   # specific files

Reads MP3s from assets/audio/, writes .vtt next to each MP3.
Uses the local model at ~/whisper-models/faster-whisper-large-v3 if present
(no network); otherwise falls back to the HuggingFace "large-v3" repo id
(requires network / HF_ENDPOINT mirror).
"""
import sys, os, time
from faster_whisper import WhisperModel

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(ROOT, "assets", "audio")
LOCAL_MODEL = os.path.expanduser("~/whisper-models/faster-whisper-large-v3")
model_src = LOCAL_MODEL if os.path.exists(os.path.join(LOCAL_MODEL, "model.bin")) else "large-v3"
print(f"loading model from: {model_src} (cpu/int8)...", flush=True)
t_load = time.time()
model = WhisperModel(model_src, device="cpu", compute_type="int8")
print(f"model loaded in {time.time()-t_load:.1f}s", flush=True)

def fmt(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"

def to_vtt(path):
    t0 = time.time()
    # language forced en; vad_filter trims long silences; segment-level timestamps (enough for subtitles)
    segments, info = model.transcribe(path, language="en", beam_size=5, vad_filter=True)
    segs = list(segments)
    dur = time.time() - t0
    out = os.path.splitext(path)[0] + ".vtt"
    with open(out, "w") as f:
        f.write("WEBVTT\n\n")
        for s in segs:
            text = s.text.strip()
            if text:
                f.write(f"{fmt(s.start)} --> {fmt(s.end)}\n{text}\n\n")
    audio_dur = info.duration if hasattr(info, "duration") else 0
    rt = (audio_dur / dur) if dur else 0
    print(f"{os.path.basename(path)}: {len(segs)} segs | audio {audio_dur:.0f}s -> {dur:.1f}s | {rt:.2f}x realtime -> {os.path.basename(out)}", flush=True)

files = sys.argv[1:] or sorted(f for f in os.listdir(AUDIO_DIR) if f.endswith(".mp3"))
for fn in files:
    to_vtt(os.path.join(AUDIO_DIR, fn) if not os.path.isabs(fn) else fn)
print("DONE", flush=True)
