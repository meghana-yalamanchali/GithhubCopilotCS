const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
    testDir: './tests/browser',
    workers: 1,
    use: {
        baseURL: 'http://127.0.0.1:5001',
        headless: true
    },
    webServer: {
        command: 'py -3 -c "from main import app; app.run(port=5001, debug=False, use_reloader=False)"',
        url: 'http://127.0.0.1:5001',
        reuseExistingServer: false
    }
});