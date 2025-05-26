// ==UserScript==
// @name         URI identity & styling
// @namespace    scripts.frankindev.com
// @version      0.1.20
// @description  try to take over the world with styles...
// @author       Frank Lin
// @match        *://*.baidu.com/*
// @resource     css_baidu	https://cdn.honglin.ac.cn/statically/gh/flinhong/configs/main/public/styles/baidu.css
// @match        *://www.google.co.uk/*
// @resource     css_google	https://cdn.honglin.ac.cn/statically/gh/flinhong/configs/main/public/styles/google.css
// @match        *://www.google.com/*
// @resource     css_google	https://cdn.honglin.ac.cn/statically/gh/flinhong/configs/main/public/styles/google.css
// @match        *://www.zhihu.com/*
// @resource     css_zhihu	https://cdn.honglin.ac.cn/statically/gh/flinhong/configs/main/public/styles/zhihu.css
// @match        *://*.smzdm.com/*
// @resource     css_smzdm	https://cdn.honglin.ac.cn/statically/gh/flinhong/configs/main/public/styles/smzdm.css
// @match        *://www.bilibili.com/*
// @resource     css_bilibili	https://cdn.honglin.ac.cn/statically/gh/flinhong/configs/main/public/styles/bilibili.css
// @match        *://doubao.com/*
// @resource     css_doubao	https://cdn.honglin.ac.cn/statically/gh/flinhong/configs/main/public/styles/doubao.css
// @match        *://www.doubao.com/*
// @resource     css_doubao	https://cdn.honglin.ac.cn/statically/gh/flinhong/configs/main/public/styles/doubao.css
// @match        *://www.bing.com/*
// @resource     css_bing	https://cdn.honglin.ac.cn/statically/gh/flinhong/configs/main/public/styles/bing.css
// @match        *://cn.bing.com/*
// @resource     css_cn.bing	https://cdn.honglin.ac.cn/statically/gh/flinhong/configs/main/public/styles/bing.css
// @match        *://www.msn.cn/*
// @resource     css_msn.cn	https://cdn.honglin.ac.cn/statically/gh/flinhong/configs/main/public/styles/bing.css
// @match        *://www.reddit.com/*
// @resource     css_reddit	https://cdn.honglin.ac.cn/statically/gh/flinhong/configs/main/public/styles/reddit.css
// @icon         https://cdn.honglin.ac.cn/favicon.ico
// @resource     font_Google https://cdn.honglin.ac.cn/fonts/g/css?family=Crimson+Text:ital,wght@0,400;0,600;0,700;1,400;1,600;1,700&family=IBM+Plex+Mono:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;1,100;1,200;1,300;1,400;1,500;1,600;1,700&family=Noto+Serif+SC:wght@200..900&family=Oswald:wght@200..700&family=Outfit:wght@100..900&display=swap
// @grant        GM_getResourceText
// @grant        GM_addStyle
// ==/UserScript==
;
(function () {
  "use strict"
  // Your code here...
  // add 'data-domain' attribute for css selector
  document.body.setAttribute("data-domain", window.location.hostname)
  // Google fonts
  const googleFont = GM_getResourceText("font_Google")
  GM_addStyle(googleFont)
  // Custom styles
  const domain = window.location.hostname.replace(".com", "").replace(".co.uk", "").replace("www.", "").replace("cn.", "")
  const styleFont = GM_getResourceText("css_" + domain)
  GM_addStyle(styleFont)
})()
