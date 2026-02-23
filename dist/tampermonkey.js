// ==UserScript==
// @name          Styling Fonts
// @namespace     https://github.com/flinhong/configs
// @version       0.0.14
// @description   Styling fonts with CSS for better reading experience.
// @author        Frank Lin
// @icon          https://cdn.honglin.ac.cn/favicon.ico
// @match         *://*.baidu.com/*
// @match         *://google.com/*
// @match         *://www.google.co.uk/*
// @match         *://www.google.com/*
// @run-at        document-end
// @grant         GM_addStyle
// @grant         GM_getResourceText
// @downloadURL   https://cdn.honglin.ac.cn/statically/gh/flinhong/configs@main/dist/tampermonkey.js
// @updateURL     https://cdn.honglin.ac.cn/statically/gh/flinhong/configs@main/dist/tampermonkey.meta.js
// @resource      css_baidu https://cdn.honglin.ac.cn/statically/gh/flinhong/configs@main/dist/styles/baidu.css
// @resource      css_google https://cdn.honglin.ac.cn/statically/gh/flinhong/configs@main/dist/styles/google.css
// ==/UserScript==


function tampermonkeyCore() {
    "use strict"

    // Extract main domain name for CSS resource lookup (elegant approach)
    const domain = (() => {
        const h = location.hostname.split(":")[0].replace(/^www\./, "")
        if (h === "localhost" || h === "127.0.0.1") return "localhost"

        const p = h.split("."),
            l = p.length
        const s = ["co", "com", "org", "net", "gov", "edu"]
        const special = l >= 3 && s.includes(p[l - 2])
        const dIdx = special ? l - 3 : l - 2

        const original = location.hostname
            .split(":")[0]
            .replace(/^www\./, "")
            .split(".")
        const base =
            original.length === 2 ||
            (original.length === 3 && s.includes(original[1]))

        return base ? p[dIdx] : p[dIdx - 1] + "_" + p[dIdx]
    })()

    try {
        const styleContent = GM_getResourceText("css_" + domain)
        if (styleContent) {
            GM_addStyle(styleContent)
        }
    } catch (e) {
        // Resource not found, do nothing
    }
};

tampermonkeyCore();