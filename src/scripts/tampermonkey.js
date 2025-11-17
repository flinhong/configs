// @icon         https://cdn.honglin.ac.cn/favicon.ico
// @resource     font_Google https://cdn.honglin.ac.cn/fonts/g/css?family=Crimson+Text:ital,wght@0,400;0,600;0,700;1,400;1,600;1,700&family=IBM+Plex+Mono:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;1,100;1,200;1,300;1,400;1,500;1,600;1,700&family=Noto+Serif+SC:wght@200..900&family=Oswald:wght@200..700&family=Outfit:wght@100..900&display=swap
// @grant        GM_getResourceText
// @grant        GM_addStyle
// ==/UserScript==

;(function () {
    "use strict"

    // Your code here...
    // add 'data-domain' attribute for css selector
    document.body.setAttribute("data-domain", window.location.hostname)

    const domain = window.location.hostname
        .replace(".com", "")
        .replace(".co.uk", "")
        .replace("www.", "")
        .replace("cn.", "")

    // Google fonts
    const byPassList = ["chatgpt.com", "reddit.com"]
    if (!byPassList.includes(domain)) {
        const googleFont = GM_getResourceText("font_Google")
        GM_addStyle(googleFont)
    }

    // Custom styles
    const styleFont = GM_getResourceText("css_" + domain)
    GM_addStyle(styleFont)
})()
