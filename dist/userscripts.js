// ==UserScript==
// @name          Styling Fonts
// @namespace     https://github.com/flinhong/userscripts
// @version       0.0.5
// @description   Styling fonts with CSS for better reading experience.
// @author        Frank Lin
// @icon          https://cdn.honglin.ac.cn/favicon.ico
// @match         *://*.baidu.com/*
// @match         *://*.google.co.uk/*
// @match         *://*.google.com/*
// @match         *://baidu.com/*
// @match         *://google.com/*
// @match         *://www.baidu.com/*
// @match         *://www.google.co.uk/*
// @match         *://www.google.com/*
// @run-at        document-start
// @downloadURL   https://cdn.honglin.ac.cn/statically/gh/flinhong/configs@main/dist/userscripts.js
// @updateURL     https://cdn.honglin.ac.cn/statically/gh/flinhong/configs@main/dist/userscripts.meta.js
// ==/UserScript==


function userscriptsCore(cssBaseUrl) {
    "use strict"

    // Extract main domain name for CSS resource lookup (elegant approach)
    const domain = (function () {
        // Correctly split hostname into parts
        const parts = window.location.hostname.replace(/^www\./, "").split(".")
        const len = parts.length

        // Handle TLDs like .co.uk, .com.au, etc.
        // A simple heuristic for ccSLDs (country-code second-level domains).
        const specialTLDs = ["co", "com"]
        const isSpecialTLD = len >= 3 && specialTLDs.includes(parts[len - 2])

        if (len === 1) {
            // Handles 'localhost' or other single-word hostnames
            return parts[0]
        }

        // For isSpecialTLD (e.g., news.google.co.uk), return the part before the ccSLD ('google').
        // For normal subdomains (e.g., news.google.com), return the part before the TLD ('google').
        // For base domains (e.g., google.com), also return the part before the TLD ('google').
        return isSpecialTLD ? parts[len - 3] : parts[len - 2]
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