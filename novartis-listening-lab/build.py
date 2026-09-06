#!/usr/bin/env python3
"""Build Novartis Listening Lab static site.
Reads data/lessons.json + official transcript blocks + per-clip VTT,
slices the official transcript per clip, and renders index + lesson pages."""
import json, os, re, html

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data", "lessons.json")
BLOCKS = os.path.join(ROOT, "assets", "transcript", "blocks.json")
VTTDIR = os.path.join(ROOT, "assets", "vtt")
OUT_LESSONS = os.path.join(ROOT, "lessons")
INDEX = os.path.join(ROOT, "index.html")

LESSONS_META = {
    # map lesson slide hint -> fallback slice size (blocks to include if cue match fails)
}
DISCLAIMER = "来源：Novartis 2024 Q2 Investor Presentation & Q&A（2024-07）。逐字稿为诺华官方文本，字幕由 AI 本地转写并对齐时间轴；仅供个人英语学习，内容为历史信息，不代表当前业务状态。"

def norm(s):
    s = html.unescape(s)
    s = s.replace("®", "").replace("™", "")
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower())
    s = re.sub(r"\s+", " ", s).strip()
    return s

def load_vtt(path):
    """Return list of (start, end, text) cues; None if file missing."""
    if not os.path.exists(path):
        return None
    cues = []
    for block in open(path, encoding="utf-8").read().split("\n\n"):
        block = block.strip()
        if not block or block.startswith("WEBVTT"):
            continue
        lines = block.split("\n")
        # first line may be a cue id or timestamp
        i = 0
        if "-->" not in lines[0]:
            i = 1
        if i >= len(lines) or "-->" not in lines[i]:
            continue
        ts = lines[i]
        m = re.match(r"(\d\d:\d\d:\d\d\.\d{3})\s*-->\s*(\d\d:\d\d:\d\d\.\d{3})", ts)
        if not m:
            continue
        text = " ".join(lines[i+1:]).strip()
        if text:
            cues.append((m.group(1), m.group(2), text))
    return cues

def slice_transcript(blocks, cues, slide_hint):
    """Return list of blocks (dicts) covering this clip.
    Scans ALL cues, locates each in the official transcript via longest contiguous
    word-run, and slices from the first matchable cue to the last. Cues that don't
    appear in the official text (e.g. operator boilerplate) are skipped."""
    if not cues or not blocks:
        return fallback_slice(blocks, slide_hint)
    norm_blocks = [norm(b["text"]) for b in blocks]
    norm_block_words = [nb.split() for nb in norm_blocks]
    norm_block_joined = [" " + " ".join(w) + " " for w in norm_block_words]

    def match_cue(txt):
        cw = norm(txt).split()
        if len(cw) < 4:
            return None
        best_block, best_run = None, 0
        for idx, jstr in enumerate(norm_block_joined):
            if not norm_block_words[idx]:
                continue
            maxrun = 0
            for n in range(min(len(cw), 12), 3, -1):
                hit = False
                for i in range(0, len(cw) - n + 1):
                    gram = " " + " ".join(cw[i:i+n]) + " "
                    if gram in jstr:
                        maxrun = n; hit = True; break
                if hit:
                    break
            if maxrun > best_run:
                best_run = maxrun; best_block = idx
        return best_block if best_run >= 5 else None

    matched = []
    for c in cues:
        b = match_cue(c[2])
        if b is not None:
            matched.append(b)
    if not matched:
        return fallback_slice(blocks, slide_hint)
    start_b = matched[0]
    end_b = matched[-1]
    if end_b < start_b:
        start_b, end_b = end_b, start_b
    start_b = max(0, start_b)
    end_b = min(len(blocks) - 1, end_b)
    return blocks[start_b:end_b + 1]

def fallback_slice(blocks, slide_hint):
    if not blocks:
        return []
    # find first block with slide == slide_hint, else near
    start = 0
    for i, b in enumerate(blocks):
        if b.get("slide") == slide_hint:
            start = i
            break
    return blocks[start:start + 6]

def esc(s):
    return html.escape(str(s), quote=False)

def render_transcript(slice_blocks):
    out = []
    cur_slide = None
    for b in slice_blocks:
        if b.get("slide") and b["slide"] != cur_slide:
            out.append(f'<span class="slide-mark">— Slide {b["slide"]} —</span>')
            cur_slide = b["slide"]
        out.append(f'<p>{esc(b["text"])}</p>')
    return "\n".join(out) if out else '<p class="idle">（该片段逐字稿将在转写完成后生成）</p>'

def render_transcript_ai(cues):
    """Render a lesson transcript from its own (offset) VTT cues when no official
    transcript exists. Marked AI-transcribed, non-official — for核对 use only."""
    if not cues:
        return '<p class="idle">（该片段无逐字稿）</p>'
    out = ['<span class="slide-mark">— AI 转写 · 非官方文本，可能有误，以字幕音频为准 —</span>']
    for c in cues:
        out.append(f'<p>{esc(c[2])}</p>')
    return "\n".join(out)

LESSON_TMPL = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{id} · {title} — Novartis Listening Lab</title>
<link rel="stylesheet" href="../css/style.css">
</head>
<body data-lesson="{id}">
<div class="wrap">
<header class="top">
  <span class="brand">Novartis Listening Lab</span>
  <span class="sub">商务英语听力 · Week 1</span>
  <a class="back" href="../index.html">← 课程目录</a>
</header>
<main class="lesson">
  <h1>{id} · {title}</h1>
  <p class="theme">训练重点：{theme}</p>
  <div class="flow"><b>每段听两遍</b>第一遍：裸听，不开字幕，抓大意与数字，填四格。<br>第二遍：点「显示英文字幕」，把漏掉的声音和含义对位；再展开逐字稿核对。</div>
  <div class="meta">来源：<b>{source}</b>（{date}）<br>发言者：{speaker} · 时长 {duration}<br><a href="{sourceUrl}" target="_blank" rel="noopener">官方页面 ↗</a></div>

  <div class="audio-wrap">
    <audio controls preload="metadata">
      <source src="../assets/audio/{audioFile}" type="audio/mpeg">
      {track}
    </audio>
    <button class="subbtn" type="button">🎬 显示英文字幕</button>
    <div class="subs"></div>
  </div>

  <details class="transcript">
    <summary>{transcriptLabel}</summary>
    <div class="transcript-body">
{transcript}
    </div>
  </details>

  <section class="block">
    <h2>四格会议地图（听后填写）</h2>
    <div class="mm-grid">
      <div><label>Topic 主题</label><textarea data-mm="topic" placeholder="这段在讲什么？"></textarea></div>
      <div><label>Speaker positions 立场</label><textarea data-mm="speakers" placeholder="各方立场/态度"></textarea></div>
      <div><label>Decision / status 决策状态</label><textarea data-mm="status" placeholder="结论/承诺/条件"></textarea></div>
      <div><label>Next action / uncertainty 后续</label><textarea data-mm="action" placeholder="行动项/负责人/不确定"></textarea></div>
    </div>
  </section>

  <section class="block">
    <h2>关键语块</h2>
    <ul class="terms">{terms}</ul>
  </section>

  <section class="block quiz">
    <h2>理解检查（核对：展开上方逐字稿）</h2>
    {questions}
  </section>

  <section class="block">
    <h2>自评</h2>
    <div class="score-row">
      <div><label>首听</label><input data-score="first" type="number" min="0" max="10" placeholder="__"></div>
      <div><label>辅助后</label><input data-score="assisted" type="number" min="0" max="10" placeholder="__"></div>
      <div><label>疲劳</label><input data-score="fatigue" type="number" min="0" max="10" placeholder="__"></div>
      <button type="button">保存</button>
      <span class="saved"></span>
    </div>
  </section>

  <p class="disclaimer">{disclaimer}</p>
</main>
<footer class="bottom">{disclaimer}</footer>
</div>
<script src="../js/site.js"></script>
</body>
</html>
"""

INDEX_TMPL = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Novartis Listening Lab · 诺华商务英语听力</title>
<link rel="stylesheet" href="css/style.css">
</head>
<body>
<div class="wrap">
<header class="top">
  <span class="brand">Novartis Listening Lab</span>
  <span class="sub">诺华高管发言 · 商务英语听力</span>
</header>
<main>
  <p style="color:var(--muted);font-size:14px;margin:0 0 14px">诺华高管发言 · 商务英语听力。每段听两遍：第一遍裸听抓大意，第二遍开英文字幕对位，再用逐字稿核对。</p>
{groups}
  <p style="font-size:12px;color:#8295a8;margin-top:18px">来源：Novartis 2024 Q2、2026 Q1/Q2 Investor Presentation。2024 逐字稿为诺华官方文本，2026 逐字稿为 AI 转写（非官方）；字幕均由 AI 本地转写。仅供个人英语学习，内容为历史信息，不代表当前业务状态。</p>
</main>
</div>
</body>
</html>
"""

def main():
    lessons = json.load(open(DATA, encoding="utf-8"))
    blocks = []
    if os.path.exists(BLOCKS):
        blocks = json.load(open(BLOCKS, encoding="utf-8"))
    os.makedirs(OUT_LESSONS, exist_ok=True)
    built = []
    for L in lessons:
        cues = load_vtt(os.path.join(VTTDIR, L["vttFile"]))
        if L.get("transcriptMode") == "ai" and cues:
            transcript_html = render_transcript_ai(cues)
            nblk = len(cues)
            transcript_label = "完整英文逐字稿（AI 转写·非官方，核对用）"
        else:
            sl = slice_transcript(blocks, cues, L.get("slide"))
            transcript_html = render_transcript(sl)
            nblk = len(sl)
            transcript_label = "完整英文逐字稿（诺华官方文本，核对用）"
        has_vtt = cues is not None and len(cues) > 0
        track = (f'<track kind="subtitles" src="../assets/vtt/{L["vttFile"]}" '
                 f'srclang="en" label="English" default>') if has_vtt else '<!-- VTT 未就绪，字幕待生成 -->'
        terms = "".join(f'<li><b>{esc(t["en"])}</b><span>{esc(t["cn"])}</span></li>' for t in L.get("terms", []))
        qs = "".join(f'<div class="q"><p class="q-text">{esc(q)}</p><p class="q-hint">提示：展开上方逐字稿核对要点。</p></div>' for q in L.get("questions", []))
        page = LESSON_TMPL.format(
            id=L["id"], title=esc(L["title"]), theme=esc(L["theme"]),
            source=esc(L["source"]), date=esc(L["date"]), speaker=esc(L["speaker"]),
            duration=esc(L["duration"]), sourceUrl=esc(L["sourceUrl"]),
            audioFile=esc(L["audioFile"]), track=track, transcript=transcript_html,
            transcriptLabel=transcript_label,
            terms=terms, questions=qs, disclaimer=esc(DISCLAIMER),
        )
        out = os.path.join(OUT_LESSONS, f'{L["id"]}.html')
        open(out, "w", encoding="utf-8").write(page)
        built.append((L, has_vtt, nblk))
        print(f"{L['id']}: vtt={'yes' if has_vtt else 'NO'} | transcript cues={nblk} -> {out}")

    # index — group by quarter
    from collections import OrderedDict
    groups = OrderedDict()
    for L, has_vtt, nblk in built:
        g = L.get("group") or "2024 Q2 · Week 1"
        groups.setdefault(g, []).append((L, has_vtt))
    group_html = []
    for g, members in groups.items():
        lis = []
        for L, has_vtt in members:
            badge = "" if has_vtt else ' <span style="color:#c0392b;font-size:11px">(字幕待生成)</span>'
            lis.append(
                f'<li><a href="lessons/{L["id"]}.html">'
                f'<span class="num">{L["id"]}</span>'
                f'<span class="info"><h2>{esc(L["title"])} · {esc(L["titleCn"])}{badge}</h2>'
                f'<p>{esc(L["theme"])} · {esc(L["speaker"])}</p></span>'
                f'<span class="dur">{esc(L["duration"])}</span></a></li>'
            )
        group_html.append(f'<section class="grp"><h2>{esc(g)}</h2><ol class="lesson-list">{"".join(lis)}</ol></section>')
    open(INDEX, "w", encoding="utf-8").write(INDEX_TMPL.format(groups="\n".join(group_html)))
    print(f"index -> {INDEX}")
    print(f"built {len(built)} lessons; vtt ready: {sum(1 for _,h,_ in built if h)}/{len(built)}")

if __name__ == "__main__":
    main()
