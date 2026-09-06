#!/usr/bin/env python3
"""Slice a full-presentation MP3 into 2-3 min lessons at Whisper segment boundaries.

Usage:
  python3 scripts/slice.py <full_mp3> <full_vtt> <start_num> <id_prefix> <quarter_label>
  e.g. python3 scripts/slice.py assets/audio/raw/q1-2026.mp3 assets/audio/raw/q1-2026.vtt 7 q1-2026 "2026 Q1"

Reads the full VTT (segment cues with start/end), groups cues until ~150s, cuts
at the last cue end within [120s,195s] (never mid-sentence), and writes per-lesson
MP3 + offset VTT + a manifest. Uses PyAV re-encode (reliable on mono speech).
"""
import sys, os, re, json, av

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN_DUR, TARGET, MAX_DUR = 120.0, 150.0, 195.0  # 2-3.25 min window, aim ~2.5

def t_to_sec(ts):
    s = 0.0
    for p in ts.split(":"):
        s = s * 60 + float(p)
    return s

def sec_to_vtt(s):
    h = int(s // 3600); m = int((s % 3600) // 60); sec = s % 60
    return f"{h:02d}:{m:02d}:{sec:06.3f}"

def load_vtt_cues(path):
    cues = []
    for block in open(path, encoding="utf-8").read().split("\n\n"):
        block = block.strip()
        if not block or block.startswith("WEBVTT"):
            continue
        lines = block.split("\n")
        i = 0 if "-->" in lines[0] else 1
        if i >= len(lines) or "-->" not in lines[i]:
            continue
        m = re.match(r"([\d:.]+)\s*-->\s*([\d:.]+)", lines[i])
        if not m:
            continue
        text = " ".join(lines[i+1:]).strip()
        if text:
            cues.append((t_to_sec(m.group(1)), t_to_sec(m.group(2)), text))
    return cues

def find_cut_points(cues, total):
    """Return list of (start,end) lesson spans in seconds, cut on cue boundaries."""
    if not cues:
        s = 0.0
        spans = []
        while s < total - 5:
            e = min(s + TARGET, total)
            spans.append((s, e)); s = e
        return spans
    spans = []
    cs = 0.0  # current span start
    for (st, en, _) in cues:
        if st < cs:
            continue
        span_end = en - cs  # duration if we cut at this cue end
        if span_end >= MAX_DUR:
            # over cap: must cut here
            spans.append((cs, en)); cs = en
        elif span_end >= TARGET:
            # in good range: cut
            spans.append((cs, en)); cs = en
    # tail
    if cs < total - 5:
        last = total - cs
        if last < 90 and spans:
            ps, _ = spans[-1]
            spans[-1] = (ps, total)  # merge tail into previous
        else:
            spans.append((cs, total))
    return spans

def cut_mp3(src, dst, t0, t1):
    inp = av.open(src)
    in_s = inp.streams.audio[0]
    tb = in_s.time_base
    inp.seek(int(t0 / tb), stream=in_s)  # fast-forward to near t0
    out = av.open(dst, "w")
    out_s = out.add_stream("mp3", rate=in_s.rate)
    out_s.layout = in_s.layout
    for frame in inp.decode(in_s):
        t = (frame.pts * tb) if frame.pts is not None else 0.0
        if t < t0:
            continue
        if t >= t1:
            break
        for pkt in out_s.encode(frame):
            out.mux(pkt)
    for pkt in out_s.encode(None):  # flush
        out.mux(pkt)
    out.close(); inp.close()

def write_offset_vtt(cues, t0, t1, dst):
    sub = [(st, en, tx) for (st, en, tx) in cues if st >= t0 - 0.5 and st < t1]
    with open(dst, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for (st, en, tx) in sub:
            f.write(f"{sec_to_vtt(st - t0)} --> {sec_to_vtt(en - t0)}\n{tx}\n\n")

def main():
    full_mp3, full_vtt, start_num, prefix, label = sys.argv[1:6]
    full_mp3 = os.path.join(ROOT, full_mp3) if not os.path.isabs(full_mp3) else full_mp3
    full_vtt = os.path.join(ROOT, full_vtt) if not os.path.isabs(full_vtt) else full_vtt
    cues = load_vtt_cues(full_vtt)
    total = cues[-1][1] if cues else 0.0
    spans = find_cut_points(cues, total)
    audio_dir = os.path.join(ROOT, "assets", "audio")
    vtt_dir = os.path.join(ROOT, "assets", "vtt")
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(vtt_dir, exist_ok=True)
    n = int(start_num)
    manifest = []
    for (t0, t1) in spans:
        lid = f"D{n}"
        mp3_out = os.path.join(audio_dir, f"{lid}-{prefix}.mp3")
        vtt_out = os.path.join(vtt_dir, f"{lid}-{prefix}.vtt")
        cut_mp3(full_mp3, mp3_out, t0, t1)
        write_offset_vtt(cues, t0, t1, vtt_out)
        seg_cues = [c for c in cues if c[0] >= t0 - 0.5 and c[0] < t1]
        preview = " ".join(c[2] for c in seg_cues[:3])[:160]
        manifest.append({
            "id": lid, "quarter": label, "source": prefix,
            "start": round(t0, 1), "end": round(t1, 1),
            "duration": round(t1 - t0, 1), "preview": preview,
        })
        print(f"{lid} ({prefix}): {t1-t0:4.0f}s  {preview[:70]}")
        n += 1
    mf = os.path.join(ROOT, "data", f"slices-{prefix}.json")
    json.dump(manifest, open(mf, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"-> {mf} ({len(manifest)} lessons)")

if __name__ == "__main__":
    main()
