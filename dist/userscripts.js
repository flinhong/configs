// ==UserScript==
// @name          Styling Fonts
// @namespace     https://github.com/flinhong/userscripts
// @version       0.0.14
// @description   Styling fonts with CSS for better reading experience.
// @author        Frank Lin
// @icon          https://cdn.honglin.ac.cn/favicon.ico
// @match         *://*.baidu.com/*
// @match         *://google.com/*
// @match         *://www.google.co.uk/*
// @match         *://www.google.com/*
// @run-at        document-end
// @downloadURL   https://cdn.honglin.ac.cn/statically/gh/flinhong/configs@main/dist/userscripts.js
// @updateURL     https://cdn.honglin.ac.cn/statically/gh/flinhong/configs@main/dist/userscripts.meta.js
// ==/UserScript==


function userscriptsCore(cssBaseUrl) {
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

    // Function to inject CSS via external link
    function injectCssLink(href) {
        const link = document.createElement("link")
        link.rel = "stylesheet"
        link.type = "text/css"
        link.href = href
        document.head.appendChild(link)
    }

    // Load CSS based on domain
    function loadDomainCss() {
        // Domain is already processed and standardized, use it directly
        if (domain) {
            const cssUrl = `${cssBaseUrl}${domain}.css`
            injectCssLink(cssUrl)
        }
    }

    loadDomainCss()
};

userscriptsCore("https://cdn.honglin.ac.cn/statically/gh/flinhong/configs@main/dist/styles/");