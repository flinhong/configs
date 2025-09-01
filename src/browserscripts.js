const sites = require("./site.configs.json")
const { insertScriptFromFile } = require("./scripts/insertScriptFromFile")
const tampermonkeyContent = insertScriptFromFile("tampermonkey.js")
const userscriptContent = insertScriptFromFile("userscript.js")

const versionInformation = (version) => `
// ==UserScript==
// @name         URI identity & styling
// @namespace    scripts.frankindev.com
// @version      ${version}
// @description  try to take over the world with styles...
// @author       Frank Lin
`

const userscriptString = (version) => `
${versionInformation(version)}

${sites
    .map((site) => {
        return `// @match        *://${site.domain}/*`
    })
    .join("\r\n")}

    ${userscriptContent}
`

const tampermonkeyString = (version) => `
${versionInformation(version)}

${sites
    .map((site) => {
        return `// @match        *://${site.domain}/*\r\n// @resource     css_${site.domain.replace("*.", "").replace(".com", "").replace(".co.uk", "").replace("www.", "")}\thttps://cdn.honglin.ac.cn/statically/gh/flinhong/configs/main/public/styles/${site.css}`
    })
    .join("\r\n")}

    ${tampermonkeyContent}
`

module.exports = { userscriptString, tampermonkeyString }
