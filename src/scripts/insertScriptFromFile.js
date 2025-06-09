const fs = require("fs")
const path = require("path")

function insertScriptFromFile(filePath) {
    try {
        // Construct the absolute path to the file (important for Node.js)
        const absoluteFilePath = path.resolve(__dirname, filePath)

        // Read the content of the external JavaScript file synchronously
        const fileContent = fs.readFileSync(absoluteFilePath, "utf8")

        // Now you have the file content as a string in 'fileContent'
        return fileContent
    } catch (error) {
        console.error("Error reading or inserting script:", error)
    }
}

// Example usage:
// Assuming you have a file named 'external_script.js' in the same directory
// insertScriptFromFile('external_script.js');
module.exports = { insertScriptFromFile }
