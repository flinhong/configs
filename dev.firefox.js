const fs = require("fs").promises // Using promises for cleaner async code
const path = require("path")

/**
 * Copies a file from a source path to a destination folder.
 *
 * @param {string} sourceFile - The full path to the source file.
 * @param {string} destinationFolder - The full path to the destination folder.
 * @returns {Promise<void>} - A Promise that resolves when the file is copied successfully,
 *                             or rejects if there's an error.
 */
async function copyFileToFolder(sourceFile, destinationFolder) {
    try {
        // 1. Check if the source file exists
        await fs.access(sourceFile, fs.constants.F_OK)
        // 2. Check if the destination folder exists
        try {
            await fs.access(destinationFolder, fs.constants.F_OK)
        } catch (err) {
            if (err.code === "ENOENT") {
                // Destination folder does not exist, create it
                console.log(
                    `Destination folder "${destinationFolder}" does not exist. Creating it...`,
                )
                await fs.mkdir(destinationFolder, { recursive: true }) // { recursive: true } creates parent folders if needed
                console.log(
                    `Destination folder "${destinationFolder}" created.`,
                )
            } else {
                // Other error accessing destination folder (e.g., permissions)
                throw err // Re-throw the error to be caught in the main try-catch
            }
        }
        // 3. Construct the full destination file path
        const fileName = path.basename(sourceFile) // Get the filename from the source path
        const destinationFile = path.join(destinationFolder, fileName)
        // 4. Copy the file
        console.log(`Copying file "${sourceFile}" to "${destinationFile}"...`)
        await fs.copyFile(sourceFile, destinationFile)
        console.log(
            `File "${sourceFile}" copied to "${destinationFile}" successfully.`,
        )
    } catch (error) {
        console.error("Error copying file:", error)
        throw error // Re-throw the error so the caller knows something went wrong
    }
}

// --- Usage ---
const release = "beniecrh.default-release"
const paths = {
    wsl: `/mnt/c/Users/flinh/AppData/Roaming/Mozilla/Firefox/Profiles/${release}/chrome`,
    win: `C:\Users\flinh\AppData\Roaming\Mozilla\Firefox\Profiles\${release}\chrome`,
}

let firefoxPath = path.resolve(paths.wsl)
let customContentPath = path.resolve("./public/styles/userContent.css")

copyFileToFolder(customContentPath, firefoxPath)
    .then(() => {
        console.log("File copy process completed successfully.")
    })
    .catch((error) => {
        console.error("File copy process failed.")
        // Handle the error further if needed
    })
