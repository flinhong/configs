const fs = require("fs")
const beautify = require("js-beautify/js").js
const AutoVersion = require("auto-version-js")
const { userscriptString, tampermonkeyString } = require("./src/browserscripts")

const version = AutoVersion.getVersion()

const formattedUserscript = (version) =>
    beautify(userscriptString(version), {
        indent_size: 2,
        jslint_happy: true,
        preserve_newlines: false,
        end_with_newline: true,
    })

const formattedTampermonkey = (version) =>
    beautify(tampermonkeyString(version), {
        indent_size: 2,
        jslint_happy: true,
        preserve_newlines: false,
        end_with_newline: true,
    })

fs.writeFile(
    "./public/tampermonkey.js",
    formattedTampermonkey(version),
    (err) => {
        if (err) {
            console.log(err)
        }
        console.log(`tampermonkey script updated!`)
    },
)

fs.writeFile("./public/userscript.js", formattedUserscript(version), (err) => {
    if (err) {
        console.log(err)
    }
    console.log(`userscript updated!`)
})
