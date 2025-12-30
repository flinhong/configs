// ==UserScript==
// @name          Styling Fonts
// @namespace     https://github.com/flinhong/configs
// @version       0.0.8
// @description   Styling fonts with CSS for better reading experience.
// @author        Frank Lin
// @icon          https://cdn.honglin.ac.cn/favicon.ico
// @match         *://google.com/*
// @match         *://news.baidu.com/*
// @match         *://www.baidu.com/*
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

    // Map domain to resource key
    function getResourceKey(domain) {
        // Domain is already processed and standardized, use it directly
        return domain
    }

    try {
        const resourceKey = getResourceKey(domain)
        const styleContent = GM_getResourceText("css_" + resourceKey)
        if (styleContent) {
            GM_addStyle(styleContent)
        }
    } catch (e) {
        // Resource not found, do nothing
    }
};

tampermonkeyCore();