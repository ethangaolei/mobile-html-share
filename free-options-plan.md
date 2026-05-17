# 免费方案：手机微信查看电脑生成的 HTML

更新时间：2026-05-17 20:03 CST

## 目标

让电脑生成的 HTML 页面可以通过手机微信打开查看；手机和电脑不要求在同一个 WiFi 环境下。

## 推荐结论

如果没有腾讯云，优先使用：

GitHub Pages

理由：

1. 免费
2. 稳定
3. 自动 HTTPS
4. 适合静态 HTML/PDF/图片/CSS/JS
5. 微信内置浏览器一般可以直接打开
6. 不需要维护服务器
7. 后续可以绑定自有域名，但不是必需

访问链路：

电脑生成 HTML → 上传到 GitHub 仓库 → GitHub Pages 自动发布 → 手机微信打开 HTTPS 链接

## 方案对比

| 方案 | 免费 | HTTPS | 微信打开 | 国内访问稳定性 | 适合程度 | 备注 |
|---|---|---|---|---|---|---|
| GitHub Pages | 是 | 是 | 通常可打开 | 中等 | 推荐 | 最简单，适合报告和静态页 |
| Cloudflare Pages | 是 | 是 | 通常可打开 | 中等偏不稳定 | 可选 | 国内网络有时不稳定 |
| Netlify | 是 | 是 | 通常可打开 | 中等偏不稳定 | 可选 | 部署简单，但国内访问不一定稳 |
| Vercel | 是 | 是 | 通常可打开 | 中等偏不稳定 | 可选 | 适合前端项目，国内访问波动 |
| 本机内网穿透 | 可免费 | 视工具 | 不稳定 | 取决于工具 | 临时调试 | 不建议正式用 |
| 本机局域网 http.server | 免费 | 否 | 同 WiFi 可用 | 只限局域网 | 仅本地测试 | 不满足不同 WiFi |

## 推荐方案：GitHub Pages

### 目录结构

建议项目放在 Hermes 目录下：

/Users/ethangao/.hermes/projects/mobile-html-share/
  site/
    index.html
    reports/
      2026-05-17-kunpeng-org-design.html
      2026-05-17-kunpeng-org-design.pdf
  scripts/
    publish.sh
  free-options-plan.md

### GitHub Pages 发布方式

有两种：

#### 方式 A：最简单

创建一个公开仓库，例如：

mobile-html-share

把 HTML 文件放到仓库根目录或 docs/ 目录，然后在 GitHub 设置里开启 Pages。

访问地址类似：

https://ethangao.github.io/mobile-html-share/

#### 方式 B：更适合长期使用

使用一个专门的仓库作为“报告发布站”：

html-share

每个报告一个目录：

/reports/2026-05-17-kunpeng-org-design/index.html
/reports/2026-05-17-kunpeng-org-design/document.pdf

访问地址：

https://ethangao.github.io/html-share/reports/2026-05-17-kunpeng-org-design/

## 隐私与安全边界

GitHub Pages 免费方案通常意味着：

1. 仓库公开，页面公开
2. 不适合放高度敏感材料
3. 可以用“随机长路径”降低被无意发现的概率，但这不是严格权限控制

例如：

/reports/2026-05-17-kunpeng-org-design-a8f3k2p9/index.html

如果内容敏感，不建议使用公开 GitHub Pages。可以改用：

1. 私有 GitHub 仓库 + 手动下载查看
2. Cloudflare Access 等带登录的方案
3. 临时本地服务 + Tailscale/ZeroTier
4. 后续再上云服务

## 最小落地步骤

### Step 1：确认 GitHub CLI 是否可用

运行：

gh auth status

如果未登录，需要先登录：

gh auth login

### Step 2：创建本地项目目录

/Users/ethangao/.hermes/projects/mobile-html-share/

### Step 3：创建 site/index.html 测试页

内容：

<html>
<head><meta charset="utf-8"><title>HTML Share Test</title></head>
<body>
<h1>手机微信 HTML 访问测试</h1>
<p>如果你在微信里看到这行字，说明免费发布链路跑通。</p>
</body>
</html>

### Step 4：创建 GitHub 仓库并推送

建议仓库名：

mobile-html-share

### Step 5：开启 GitHub Pages

仓库 Settings → Pages → Source 选择 main branch / root 或 docs。

### Step 6：手机微信打开链接验证

把链接发送到微信，手机端打开。

成功标准：

1. 手机和电脑不在同一 WiFi 也能打开
2. 微信内置浏览器显示中文正常
3. HTTPS 正常
4. HTML 样式正常

## 我建议下一步

先检测本机是否已经安装并登录 GitHub CLI：

1. gh 是否存在
2. gh 是否登录
3. git 用户配置是否存在

如果都就绪，就可以直接创建 GitHub Pages 测试仓库并发布 test.html。

如果没有 GitHub CLI，也可以用浏览器手动创建仓库，或者我生成本地文件，你手动上传。
