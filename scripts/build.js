const fs = require("fs")
const path = require("path")

const projectRoot = path.join(__dirname, "..")

const distDir = path.join(projectRoot, "dist")
const srcDir = path.join(projectRoot, "src")
const templatesDir = path.join(projectRoot, "templates")
const configsDir = path.join(projectRoot, "configs")
const stylesDir = path.join(configsDir, "styles")
const distStylesDir = path.join(distDir, "styles")

const repoBaseUrl =
    "https://cdn.honglin.ac.cn/statically/gh/flinhong/configs@main"

function getVersion() {
    const versionPath = path.join(configsDir, "version.json")
    const versionFile = fs.readFileSync(versionPath, "utf8")
    return JSON.parse(versionFile).version
}

function processRules() {
    const domainConfigPath = path.join(configsDir, "domain.json")
    const config = JSON.parse(fs.readFileSync(domainConfigPath, "utf8"))
    const rules = config.rules

    const allMatchPatterns = new Set()
    const uniqueStyles = new Set()

    rules.forEach((rule) => {
        uniqueStyles.add(rule.name)
        rule.domains.forEach((domain) => {
            // 域名匹配
            allMatchPatterns.add(`*://${domain}/*`)
        })
    })

    const sortedMatchPatterns = Array.from(allMatchPatterns).sort()

    return {
        matchPatterns: sortedMatchPatterns,
        styleNames: Array.from(uniqueStyles),
    }
}

function buildCss(styleNames) {
    if (!fs.existsSync(distStylesDir)) {
        fs.mkdirSync(distStylesDir, { recursive: true })
    }

    styleNames.forEach((styleName) => {
        const styleFilePath = path.join(stylesDir, `${styleName}.css`)

        if (fs.existsSync(styleFilePath)) {
            const cssContent = fs.readFileSync(styleFilePath, "utf8")
            fs.writeFileSync(
                path.join(distStylesDir, `${styleName}.css`),
                cssContent
            )
        }
    })

    console.log("Successfully built CSS bundles.")
}

function build() {
    if (!fs.existsSync(distDir)) {
        fs.mkdirSync(distDir)
    }

    const version = getVersion()
    const { matchPatterns, styleNames } = processRules()

    buildCss(styleNames)

    function generateResourceDeclarations(styleNames) {
        return styleNames
            .map((name) => {
                const cssUrl = `${repoBaseUrl}/dist/styles/${name}.css`
                return `// @resource      css_${name} ${cssUrl}`
            })
            .join("\n")
    }

    const resourceDeclarations = generateResourceDeclarations(styleNames)
    const fullCoreJs = fs.readFileSync(path.join(srcDir, "core.js"), "utf8")

    const tampermonkeyMatch = fullCoreJs.match(
        /function tampermonkeyCore\(\) \{[\s\S]*?\n\}/
    )
    const tampermonkeyCoreJs = tampermonkeyMatch
        ? `${tampermonkeyMatch[0]};\n\ntampermonkeyCore();`
        : ""

    const userscriptsMatch = fullCoreJs.match(
        /function userscriptsCore\(.*?\) \{[\s\S]*?\n\}/
    )
    const userscriptsFunc = userscriptsMatch ? userscriptsMatch[0] : ""

    const cssBaseUrl = `${repoBaseUrl}/dist/styles/`
    const userscriptsCoreJs = `${userscriptsFunc};\n\nuserscriptsCore(${JSON.stringify(
        cssBaseUrl
    )});`

    const matchPatternStr = matchPatterns.join("\n// @match         ")

    // --- Build Tampermonkey Script ---
    const tampermonkeyDownloadUrl = `${repoBaseUrl}/dist/tampermonkey.js`
    const tampermonkeyUpdateUrl = `${repoBaseUrl}/dist/tampermonkey.meta.js`

    const tampermonkeyHeader = fs
        .readFileSync(path.join(templatesDir, "tampermonkey.headers"), "utf8")
        .replace(/__VERSION__/g, version)
        .replace("__MATCH_PATTERNS__", matchPatternStr)
        .replace("__DOWNLOAD_URL__", tampermonkeyDownloadUrl)
        .replace("__UPDATE_URL__", tampermonkeyUpdateUrl)
        .replace("__RESOURCE_DECLARATIONS__", resourceDeclarations)

    fs.writeFileSync(
        path.join(distDir, "tampermonkey.meta.js"),
        tampermonkeyHeader
    )
    console.log("Successfully built tampermonkey.meta.js")

    const tampermonkeyScript = `${tampermonkeyHeader}\n\n${tampermonkeyCoreJs}`
    fs.writeFileSync(path.join(distDir, "tampermonkey.js"), tampermonkeyScript)
    console.log("Successfully built tampermonkey.js")

    // --- Build Userscripts Script ---
    const userscriptsDownloadUrl = `${repoBaseUrl}/dist/userscripts.js`
    const userscriptsUpdateUrl = `${repoBaseUrl}/dist/userscripts.meta.js`

    const userscriptsHeader = fs
        .readFileSync(path.join(templatesDir, "userscripts.headers"), "utf8")
        .replace(/__VERSION__/g, version)
        .replace("__MATCH_PATTERNS__", matchPatternStr)
        .replace("__DOWNLOAD_URL__", userscriptsDownloadUrl)
        .replace("__UPDATE_URL__", userscriptsUpdateUrl)

    fs.writeFileSync(
        path.join(distDir, "userscripts.meta.js"),
        userscriptsHeader
    )
    console.log("Successfully built userscripts.meta.js")

    const userscriptsScript = `${userscriptsHeader}\n\n${userscriptsCoreJs}`
    fs.writeFileSync(path.join(distDir, "userscripts.js"), userscriptsScript)
    console.log("Successfully built userscripts.js")
}

if (require.main === module) {
    build()
}
