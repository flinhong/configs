// @icon         https://cdn.honglin.ac.cn/favicon.ico
// @resource     font_Google https://cdn.honglin.ac.cn/fonts/g/css?family=Crimson+Pro:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Lato:ital@0;1&family=Noto+Serif+SC:wght@300;400;500&family=Oswald:wght@300&family=IBM+Plex+Mono:ital@0;1&display=swap
// @grant        GM_getResourceText
// @grant        GM_addStyle
// ==/UserScript==

;(function () {
    "use strict"

    // Your code here...
    // add 'data-domain' attribute for css selector
    document.body.setAttribute("data-domain", window.location.hostname)

    // Google fonts
    const googleFont = GM_getResourceText("font_Google")
    GM_addStyle(googleFont)

    // Custom styles
    const domain = window.location.hostname
        .replace(".com", "")
        .replace(".co.uk", "")
        .replace("www.", "")
        .replace("cn.", "")
    const styleFont = GM_getResourceText("css_" + domain)
    GM_addStyle(styleFont)
})()
