// Tampermonkey version: Use GM APIs
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
}

// Userscripts version: Use standard Web APIs
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
}
