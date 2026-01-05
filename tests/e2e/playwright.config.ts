import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:7000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'cd ../.. && python -m uvicorn api.main:app --host 0.0.0.0 --port 7000',
    url: 'http://localhost:7000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
