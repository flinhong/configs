// ==UserScript==
// @name         URI identity & styling
// @namespace    scripts.frankindev.com
// @version      0.1.12
// @description  try to take over the world with styles...
// @author       Frank Lin
// @match        *://*.baidu.com/*
// @match        *://www.google.co.uk/*
// @match        *://www.google.com/*
// @match        *://www.zhihu.com/*
// @match        *://*.smzdm.com/*
// @match        *://www.bilibili.com/*
// @match        *://doubao.com/*
// @match        *://www.doubao.com/*
// @icon         https://cdn.honglin.ac.cn/favicon.ico
// @updateURL    https://cdn.honglin.ac.cn/statically/gh/flinhong/configs/main/public/userscript.js
// @grant        GM_addStyle
// ==/UserScript==

(function () {
  "use strict";

  // Your code here...
  // add 'data-domain' attribute for css selector
  document.body.setAttribute("data-domain", window.location.hostname);

  const domain = window.location.hostname
    .replace(".com", "")
    .replace(".co.uk", "")
    .replace("www.", "");

  const styles = [
    'https://cdn.honglin.ac.cn/fonts/g/css?family=Crimson+Pro:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Lato:ital@0;1&family=Noto+Serif+SC:wght@300;400;500&family=Oswald:wght@300&family=IBM+Plex+Mono:ital@0;1&display=swap',
    'https://cdn.honglin.ac.cn/statically/gh/flinhong/configs/main/public/styles/' + domain + '.css'
  ]

  styles.forEach((href) => {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.type = 'text/css';
    link.href = href;
    document.getElementsByTagName('HEAD')[0].appendChild(link);
  })
})();
