# Hermes Mobile HTML Share

这个仓库用于通过 GitHub Pages 发布 Hermes 生成的静态 HTML 预览页，让手机微信可以在不同 WiFi 环境下打开查看。

首页：

https://ethangaolei.github.io/mobile-html-share/

## 发布新 HTML

在本地项目目录执行：

```bash
cd /Users/ethangao/.hermes/projects/mobile-html-share
./scripts/publish_html.sh /path/to/report.html your-report-slug
```

示例：

```bash
./scripts/publish_html.sh ~/Downloads/report.html kunpeng-org-design
```

脚本会：

1. 复制 HTML 到 `reports/YYYY-MM-DD-slug/index.html`
2. 如存在同名资源目录，也会复制 assets
3. 自动 git commit + push
4. 输出微信可打开的 GitHub Pages URL

## 目录建议

- `index.html`：首页/测试页
- `reports/`：项目报告和预览页
- `assets/`：公共静态资源
- `scripts/publish_html.sh`：发布脚本

## 注意

GitHub Pages 免费方案通常是公开访问，不应上传高度敏感内容。
