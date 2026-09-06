# Novartis Listening Lab

把诺华制药高管发言变成**商务英语听力学习站**。每课包含：同步英文字幕 + 诺华官方逐字稿 + 四格会议地图 + 关键语块 + 理解检查 + 自评（本地保存）。

> 来源：Novartis 2024 Q2 Investor Presentation & Q&A（2024-07）。字幕由 AI 本地转写并对齐时间轴，逐字稿为诺华官方文本；仅供个人英语学习，内容为历史信息，不代表当前业务状态。

## 线上地址

https://ethangaolei.github.io/mobile-html-share/novartis-listening-lab/

## 目录结构

```
novartis-listening-lab/
├── index.html              # 课程目录页（build.py 生成）
├── lessons/D1..D6.html     # 6 个课页（build.py 生成）
├── css/style.css           # 诺华配色样式
├── js/site.js              # 字幕同步 + 四格/自评 localStorage 持久化
├── build.py                # 静态站生成器：lessons.json + 官方逐字稿 + VTT → HTML
├── data/lessons.json       # 课程清单（元数据 + 语块 + 问题）
├── assets/
│   ├── audio/*.mp3         # 6 段音频（内容资产）
│   ├── vtt/*.vtt           # 6 个同步字幕（Whisper 转写）
│   └── transcript/
│       ├── blocks.json     # 诺华官方逐字稿，按 slide 分块（231 块）
│       └── full-official.txt
└── scripts/transcribe.py   # MP3 → WebVTT（本地 Whisper large-v3, CPU int8）
```

## 依赖

```bash
pip install -r requirements.txt
```

`build.py` 只用标准库；`scripts/transcribe.py` 需要 `faster-whisper` + `av`。

Whisper 模型放在 `~/whisper-models/faster-whisper-large-v3/`（本地，离线）。脚本会自动检测该目录；若不存在会回退到 HuggingFace `large-v3` repo id（在国内需配 `HF_ENDPOINT=https://hf-mirror.com`，且容易因 SSL 失败——建议保留本地模型）。

## 快速构建

```bash
python3 build.py        # 读 lessons.json + blocks.json + VTT → 生成 index + lessons/Dn.html
```

## 新增一课

1. 把音频放到 `assets/audio/`，命名 `Dn-xxx.mp3`（如 `D7-cash-flow.mp3`）。
2. 在 `data/lessons.json` 追加一条，字段照 D1–D6 的格式：`id / title / titleCn / theme / source / sourceUrl / date / speaker / duration / audioFile / vttFile / slide / terms[] / questions[]`。
3. 生成字幕：
   ```bash
   HF_HUB_OFFLINE=1 python3 scripts/transcribe.py D7-cash-flow.mp3
   ```
   （不传文件名则转写 `assets/audio/` 下全部 mp3。）
4. 重跑 `python3 build.py`，生成 `lessons/D7.html` 并更新目录页。
5. 部署（见下）。

## 字幕 vs 逐字稿（两套对齐逻辑）

- **字幕（`assets/vtt/*.vtt`）**：AI 本地 Whisper large-v3 转写，带时间轴，`<audio>` + `<track>` 渲染，点按钮开关。
- **逐字稿（lessons 页里的 `<details>`）**：诺华官方文本。`build.py` 的 `slice_transcript()` 扫描该课所有 VTT cue，用「最长连续词串 ≥5 词」在 `blocks.json` 里定位，从第一个可匹配 cue 切到最后一个可匹配 cue；跳过不在官方文本里的 cue（如接线员套话）。匹配失败则按 `slide` 字段 fallback 取 6 块。

所以字幕和逐字稿是**自动对齐到同一段发言**的，但来源不同：字幕管「听」，逐字稿管「核对」。

## 部署到 GitHub Pages（slug 模式）

发布到已有的 `mobile-html-share` 仓库（git push 凭证已缓存，全自动；无需 `gh`）：

```bash
SRC=~/novartis-listening-lab
DST=~/.hermes/workspace/mobile-html-share/novartis-listening-lab
rm -rf "$DST" && mkdir -p "$DST" && cp -R "$SRC"/* "$DST"/
cd ~/.hermes/workspace/mobile-html-share
git add novartis-listening-lab
git commit -m "publish: Novartis Listening Lab — <说明>"
git pull --rebase origin main && git push origin main
# 线上：ethangaolei.github.io/mobile-html-share/novartis-listening-lab/
```

## 已知约束

- 国内网络下 `huggingface.co` 不可达；模型用 `hf-mirror.com` + curl 下载到本地（见 `~/whisper-models/`）。
- 官方逐字稿 `blocks.json` 覆盖 2024 Q2 全场 slide 0–25；新增课若发言落在该范围之外，`slice_transcript` 会 fallback 到按 slide 取 6 块，需手动核对。
- 纯静态站，无后端；四格会议地图和自评存浏览器 localStorage（key `nll:<id>`），按课隔离、不跨设备同步。

## 版权与用途

音频与逐字稿源自诺华公开投资者关系页面；本项目仅作个人英语听力训练用途，不商用、不二次分发。字幕为 AI 转写，可能有误，以官方逐字稿为准。
