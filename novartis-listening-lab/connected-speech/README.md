# NVS Executive Connected Speech Lab

入口：https://ethangaolei.github.io/mobile-html-share/novartis-listening-lab/connected-speech/

原始 30 组、60 句于 2026-10-07 从「商务英语连读清单」原 HTML 浏览器预览逐项恢复；核心组为第 1—14 组，Analyst Question 为第 29—30 组。例句为训练材料，不是诺华官方逐字引用。

无需 API key、安装依赖或服务器后端。直接作为 GitHub Pages 静态目录发布。语音是 Mac 已安装 Samantha 合成英文语音，175 words/min，预生成 60 个单声道 22050Hz WAV。播放器使用实际音频文件及保留音高的 playbackRate；备用英文 TTS 仅在播放失败时可选。

手机：在 Safari / Chrome 打开 HTTPS 入口，点播放开始；不依赖 HTML 文件预览。只听不看会隐藏例句、语块提示和目录，切换句子重新隐藏。随机在当前筛选范围内抽句，当前一轮内不重复。已听完句数按本地日期记录在当前浏览器，不跨设备同步。切到后台会停止播放。20 分钟计时从用户点击开始，支持暂停与继续，刷新后重置。

文件：index.html / style.css / app.js / content.js / audio/*.wav。原 Listening Lab 首页和 build.py 已加入持久的专题入口。
