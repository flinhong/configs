const fs = require('fs');
const path = require('path');
const semver = require('semver');
const { execSync } = require('child_process');

const projectRoot = path.join(__dirname, '..');
const configsDir = path.join(projectRoot, 'configs');
const versionPath = path.join(configsDir, 'version.json');
const packageJsonPath = path.join(projectRoot, 'package.json'); // New: Path to package.json

function getVersion() {
    const versionFile = fs.readFileSync(versionPath, 'utf8');
    return JSON.parse(versionFile).version;
}

function writeVersion(newVersion) {
    const versionFile = JSON.stringify({ version: newVersion }, null, 2);
    fs.writeFileSync(versionPath, versionFile);
}

// New function: Update version in package.json
function updatePackageJsonVersion(newVersion) {
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    packageJson.version = newVersion;
    fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2));
    console.log(`Updated package.json version to ${newVersion}`);
}

function runBuild() {
    console.log('Running build...');
    execSync('npm run build', { stdio: 'inherit', cwd: projectRoot });
}

function handleBump(releaseType, isDryRun) {
    const currentVersion = getVersion();
    const newVersion = semver.inc(currentVersion, releaseType);

    if (isDryRun) {
        console.log('--- Dry Run ---');
        console.log(`Command: bump ${releaseType}`);
        console.log(`Current version: ${currentVersion}`);
        console.log(`Next version would be: ${newVersion}`);
        console.log('No files will be changed.');
        return;
    }

    console.log(`Bumping version from ${currentVersion} to ${newVersion}`);
    writeVersion(newVersion);
    updatePackageJsonVersion(newVersion); // New: Update package.json
    runBuild();
}

function handleSet(newVersion, isDryRun) {
    if (!semver.valid(newVersion)) {
        console.error(`Error: Invalid version format "${newVersion}". Please use a valid semantic version (e.g., 1.2.3).`);
        process.exit(1);
    }

    const currentVersion = getVersion();

    if (isDryRun) {
        console.log('--- Dry Run ---');
        console.log(`Command: set ${newVersion}`);
        console.log(`Current version: ${currentVersion}`);
        console.log(`Version would be set to: ${newVersion}`);
        console.log('No files will be changed.');
        return;
    }

    console.log(`Setting version from ${currentVersion} to ${newVersion}`);
    writeVersion(newVersion);
    updatePackageJsonVersion(newVersion); // New: Update package.json
    runBuild();
}

function handleReset(isDryRun) {
    const defaultVersion = '1.0.0';
    const currentVersion = getVersion();

    if (isDryRun) {
        console.log('--- Dry Run ---');
        console.log('Command: reset');
        console.log(`Current version: ${currentVersion}`);
        console.log(`Version would be reset to: ${defaultVersion}`);
        console.log('No files will be changed.');
        return;
    }

    console.log(`Resetting version from ${currentVersion} to ${defaultVersion}`);
    writeVersion(defaultVersion);
    updatePackageJsonVersion(defaultVersion); // New: Update package.json
    runBuild();
}


function main() {
    const args = process.argv.slice(2);
    const command = args[0] || 'bump'; // default to 'bump'
    const isDryRun = args.includes('--dryrun');

    switch (command) {
        case 'bump':
            const releaseType = args.find(arg => ['patch', 'minor', 'major'].includes(arg)) || 'patch';
            handleBump(releaseType, isDryRun);
            break;
        case 'set':
            const versionArg = args[1];
            if (!versionArg || versionArg.startsWith('--')) {
                console.error('Error: The "set" command requires a version argument.');
                console.log('Usage: npm run version:set -- <version>');
                process.exit(1);
            }
            handleSet(versionArg, isDryRun);
            break;
        case 'reset':
            handleReset(isDryRun);
            break;
        default:
            console.error(`Error: Unknown command "${command}".`);
            console.log('Available commands: bump, set, reset');
            process.exit(1);
    }
}

// Only run main() if not being imported (i.e., not during testing)
if (require.main === module) {
    main();
}
