# Enhanced Font Customizer

一个功能强大的用户脚本，可自定义任何网站的字体风格，提升阅读体验。支持 Tampermonkey 和 Userscripts 用户脚本引擎。

## ✨ 功能特性

- 🎯 **通用字体定制** - 适用于任何网站，自定义字体和样式
- 🔧 **双引擎支持** - 兼容 Tampermonkey (Firefox, Chrome) 和 Userscripts (Safari)
- 🌐 **智能域名匹配** - 自动识别域名并应用对应样式配置
- 📦 **CDN 加速** - 使用 jsDelivr CDN 加载样式文件，速度快
- 🎨 **Google Fonts** - 集成 Google Fonts 鏡像，访问无障碍
- 📱 **响应式设计** - 支持系统字体后备，确保跨平台一致性
- 🔄 **自动更新** - 版本控制系统确保样式文件实时更新
- ⚡ **性能优化** - 仅在配置的网站上运行，不影响其他页面

## 🛠️ 安装方法

### Tampermonkey 用户 (Firefox, Chrome)

1. 安装 [Tampermonkey](https://www.tampermonkey.net/) 扩展
2. 点击安装链接：
   ```
   https://cdn.jsdelivr.net/gh/flinhong/userscripts/dist/tampermonkey.js
   ```
3. 或者在 Tampermonkey 中手动创建脚本，粘贴上述链接内容

### Safari Userscripts 用户

1. 安装 [Userscripts](https://userscripts.org/) 扩展或 Safari 原生支持
2. 点击安装链接：
   ```
   https://cdn.jsdelivr.net/gh/flinhong/userscripts/dist/userscripts.js
   ```

## 📁 项目结构

```
userscripts/
├── src/
│   └── core.js              # 核心逻辑
├── configs/
│   ├── domain.json          # 域名映射配置
│   ├── version.json         # 版本号管理
│   └── styles/              # 网站样式文件
│       ├── github.css       # GitHub 字体配置
│       ├── google.css       # Google 字体配置
│       ├── bing.css         # Bing 字体配置
│       ├── chatgpt.css      # ChatGPT 字体配置
│       └── custom.css       # 自定义样式模板
├── templates/               # 脚本模板
├── scripts/
│   ├── build.js            # 构建脚本
│   └── release.js          # 发布脚本
└── dist/                   # 构建输出
```

## 🚀 开发指南

### 环境准备

```bash
# 克隆项目
git clone https://github.com/flinhong/userscripts.git
cd userscripts

# 安装依赖
npm install
```

### 本地开发

```bash
# 构建脚本
npm run build

# 清理构建文件
npm run clean
```

### 添加新网站支持

1. **更新域名配置** - 在 `configs/domain.json` 中添加新域名映射：

```json
{
  "name": "example",
  "domains": ["example.com", "www.example.com", "*.example.com"]
}
```

2. **创建样式文件** - 在 `configs/styles/` 目录下创建 `example.css`：

```css
@import url('https://fonts.googleapis.cn/css2?family=Inter:wght@400;600&display=swap');

:root {
  --font-family-sans: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
  --font-family-mono: "JetBrains Mono", "Courier New", monospace;
}

/* 自定义网站样式 */
body {
  font-family: var(--font-family-sans) !important;
}

code, pre {
  font-family: var(--font-family-mono) !important;
}
```

3. **重新构建**：
```bash
npm run build
```

### 自定义通用样式

创建 `custom.css` 文件，适用于所有未特别配置的网站：

```css
:root {
  --font-family-sans: "Roboto", -apple-system, BlinkMacSystemFont, sans-serif;
}

/* 基础样式重置 */
* {
  font-family: inherit !important;
}

body, html {
  font-family: var(--font-family-sans) !important;
}
```

## 📦 版本发布

项目使用语义化版本管理，支持自动化发布流程：

```bash
# 发布补丁版本 (x.x.(X+1))
npm run release

# 发布次版本 (x.(X+1).0)
npm run release:minor

# 发布主版本 ((X+1).0.0)
npm run release:major

# 预览版本变更，不执行实际操作
npm run release:dryrun

# 自定义版本管理
npm run version:set -- 2.1.0    # 设置指定版本
npm run version:reset           # 重置为 1.0.0
```

## 🔄 工作原理

### 智能域名解析

脚本使用智能算法提取主域名：

```javascript
// 例如：news.google.co.uk → google
// 例如：blog.example.com → example
// 例如：github.com → github
// 例如：sub.domain.org → domain
```

### 样式加载机制

- **Tampermonkey 版本**：使用 `GM_getResourceText` 和 `GM_addStyle` API
- **Userscripts 版本**：使用动态 `<link>` 标签注入样式
- **CDN 加速**：样式文件通过 jsDelivr CDN 分发

### 版本控制

- 配置文件版本：`configs/version.json`
- 包版本：`package.json`
- 自动同步更新

## 🎨 样式定制

### CSS 变量系统

使用标准化的 CSS 变量命名：

```css
:root {
  --font-family-sans: "Inter", sans-serif;      /* 无衬线字体 */
  --font-family-serif: "Georgia", serif;        /* 衬线字体 */
  --font-family-mono: "JetBrains Mono", monospace; /* 等宽字体 */
  --font-size-base: 16px;                       /* 基础字体大小 */
  --line-height-base: 1.6;                      /* 基础行高 */
}
```

### 字体导入

支持多种字体源：

```css
/* Google Fonts (中国镜像) */
@import url('https://fonts.googleapis.cn/css2?family=Inter:wght@400;600&display=swap');

/* 自定义字体服务 */
@import url('https://cdn.jsdelivr.net/gh/font-source/source-fonts@latest/inter.css');

/* 本地字体后备 */
@font-face {
  font-family: 'Custom Font';
  src: local('Custom Font Regular');
  font-display: swap;
}
```

## 🌐 适用场景

### 阅读优化
- 新闻网站、博客、文档站点
- 提升长文阅读体验
- 统一字体风格

### 开发工具
- 代码编辑器界面优化
- 控制台字体美化
- 开发者工具适配

### 社交媒体
- 信息流字体优化
- 聊天界面改进
- 内容展示美化

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/new-website`
3. 添加新网站的样式配置
4. 提交更改：`git commit -m 'Add: support for example.com'`
5. 推送分支：`git push origin feature/new-website`
6. 创建 Pull Request

## 📄 许可证

本项目采用 [ISC 许可证](LICENSE)

## 🔗 相关链接

- [GitHub 仓库](https://github.com/flinhong/userscripts)
- [问题反馈](https://github.com/flinhong/userscripts/issues)
- [CDN 分发](https://cdn.jsdelivr.net/gh/flinhong/userscripts/)
- [Tampermonkey 官网](https://www.tampermonkey.net/)
- [Userscripts 官网](https://userscripts.org/)

## 💡 使用提示

- 脚本在 `document-start` 时运行，确保样式尽早生效
- 支持 CSS 变量，便于主题定制
- 自动回退到系统字体，确保兼容性
- 使用中国镜像访问 Google Fonts，国内用户加载更流畅
- 仅在配置的网站上运行，不影响其他页面性能
- 可通过修改 `configs/domain.json` 添加更多网站支持

---

**注意**：安装后请确保脚本在相应网站上启用，可在脚本管理器中调整权限设置。对于需要支持的网站，请按照开发指南添加相应的域名和样式配置。