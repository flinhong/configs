// Tampermonkey version: Use GM APIs
function tampermonkeyCore() {
    'use strict';

    // Extract main domain name for CSS resource lookup (elegant approach)
    const domain = (function() {
        // Correctly split hostname into parts
        const parts = window.location.hostname.replace(/^www\./, "").split('.');
        const len = parts.length;
        
        // Handle TLDs like .co.uk, .com.au, etc.
        // A simple heuristic for ccSLDs (country-code second-level domains).
        const specialTLDs = ['co', 'com'];
        const isSpecialTLD = len >= 3 && specialTLDs.includes(parts[len - 2]);
        
        if (len === 1) {
            // Handles 'localhost' or other single-word hostnames
            return parts[0];
        }
        
        // For isSpecialTLD (e.g., news.google.co.uk), return the part before the ccSLD ('google').
        // For normal subdomains (e.g., news.google.com), return the part before the TLD ('google').
        // For base domains (e.g., google.com), also return the part before the TLD ('google').
        return isSpecialTLD ? parts[len - 3] : parts[len - 2];
    })();

    // Map domain to resource key
    function getResourceKey(domain) {
        // Domain is already processed and standardized, use it directly
        return domain;
    }

    try {
        const resourceKey = getResourceKey(domain);
        const styleContent = GM_getResourceText("css_" + resourceKey);
        if (styleContent) {
            GM_addStyle(styleContent);
        }
    } catch (e) {
        // Resource not found, do nothing
    }
}

// Userscripts version: Use standard Web APIs
function userscriptsCore(cssBaseUrl) {
    'use strict';

    // Extract main domain name for CSS resource lookup (elegant approach)
    const domain = (function() {
        // Correctly split hostname into parts
        const parts = window.location.hostname.replace(/^www\./, "").split('.');
        const len = parts.length;
        
        // Handle TLDs like .co.uk, .com.au, etc.
        // A simple heuristic for ccSLDs (country-code second-level domains).
        const specialTLDs = ['co', 'com'];
        const isSpecialTLD = len >= 3 && specialTLDs.includes(parts[len - 2]);
        
        if (len === 1) {
            // Handles 'localhost' or other single-word hostnames
            return parts[0];
        }
        
        // For isSpecialTLD (e.g., news.google.co.uk), return the part before the ccSLD ('google').
        // For normal subdomains (e.g., news.google.com), return the part before the TLD ('google').
        // For base domains (e.g., google.com), also return the part before the TLD ('google').
        return isSpecialTLD ? parts[len - 3] : parts[len - 2];
    })();

    // Function to inject CSS via external link
    function injectCssLink(href) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.type = 'text/css';
        link.href = href;
        document.head.appendChild(link);
    }

    // Load CSS based on domain
    function loadDomainCss() {
        // Domain is already processed and standardized, use it directly
        if (domain) {
            const cssUrl = `${cssBaseUrl}${domain}.css`;
            injectCssLink(cssUrl);
        }
    }

    loadDomainCss();
}