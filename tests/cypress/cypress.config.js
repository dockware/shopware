const {defineConfig} = require('cypress')

module.exports = defineConfig({
    chromeWebSecurity: false,
    retries: {
        "runMode": 0,
        "openMode": 0
    },
    watchForFileChanges: false,
    trashAssetsBeforeRuns: true,
    screenshotOnRunFailure: true,
    video: false,
    videoCompression: 50,
    // the Shopware Administration is a heavy SPA and crashed the Electron renderer
    // on the CircleCI machines. free memory between tests and do not keep old DOM snapshots
    numTestsKeptInMemory: 0,
    experimentalMemoryManagement: true,
    devices: [
        {
            key: 'desktop',
            name: 'Desktop',
            width: 1920,
            height: 1080,
        },
    ],
    e2e: {
        testIsolation: true,
        experimentalWebKitSupport: true,
        // We've imported your old cypress plugins here.
        // You may want to clean this up later by importing these.
        setupNodeEvents(on, config) {
            return require('./cypress/plugins/index.js')(on, config)
        },
    },
})
